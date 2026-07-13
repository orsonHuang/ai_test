"""
sentence_matcher.py - 基于 Sentence-Transformers 的语义相似度引擎
使用轻量多语言 embedding 模型（~118MB），替换原有的 Jaccard/SequenceMatcher。

设计要点：
  - 懒加载：首次调用时才加载模型，不影响冷启动速度
  - 预编码缓存：同一文本只编码一次
  - 统一接口：text_similarity(a,b) → 0-1 余弦相似度
  - 批量匹配：find_most_similar / find_top_k 一次编码 query + 批量编码候选
  - 可观察加载：支持后台异步加载，前端可轮询进度
"""
import threading
import time
import numpy as np
from typing import Optional, List, Tuple, Any

# ---- 全局状态 ----
_model = None          # SentenceTransformer 实例
_model_lock = threading.Lock()
_loading = False       # 是否有后台线程正在加载
_embed_cache: dict = {}  # text -> np.ndarray

_load_status = {
    "progress": 0,
    "message": "等待开始",
    "loaded": False,
    "error": None,
}


def _set_status(progress: int, message: str, loaded: bool = False, error: str = None):
    """原子更新加载状态"""
    _load_status.update({
        "progress": progress,
        "message": message,
        "loaded": loaded,
        "error": error,
    })


def get_load_status():
    """获取当前模型加载状态（前端轮询用）"""
    return _load_status.copy()


def load_model_async():
    """在后台线程异步加载模型，不阻塞主线程。"""
    global _loading
    with _model_lock:
        if _loading or _model is not None:
            return
        _loading = True
    t = threading.Thread(target=_load_model_sync, daemon=True)
    t.start()


def _load_model_sync():
    """同步加载模型并更新进度状态。"""
    global _model, _loading
    try:
        from sentence_transformers import SentenceTransformer

        _set_status(5, "检查本地模型缓存...")
        # 让 UI 有机会渲染初始进度
        time.sleep(0.05)

        _set_status(20, "正在加载 embedding 模型（首次约需 5-15 秒）...")
        # 轻量多语言模型，支持中英文，CPU 友好
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        _set_status(75, "模型加载完成，正在预热...")
        _model.encode(["预热"], normalize_embeddings=True)

        _set_status(100, "模型已就绪", loaded=True)
    except Exception as e:
        _set_status(0, f"模型加载失败: {e}", error=str(e))
    finally:
        _loading = False


def _get_model():
    """懒加载 SentenceTransformer 模型（会等待后台加载完成）"""
    global _model
    if _model is None:
        _load_model_sync()
    return _model


# ===== 基础编码 =====

def encode(text: str) -> np.ndarray:
    """编码单个文本 → 归一化的 embedding 向量"""
    if not text or not text.strip():
        return np.zeros(384, dtype=np.float32)
    model = _get_model()
    # normalize_embeddings=True 后余弦相似度等价于点积
    return model.encode(text.strip(), normalize_embeddings=True)


def encode_batch(texts: List[str]) -> np.ndarray:
    """批量编码（比逐个编码快 3-5 倍）"""
    if not texts:
        return np.array([], dtype=np.float32)
    model = _get_model()
    cleaned = [t.strip() if t else "" for t in texts]
    return model.encode(cleaned, normalize_embeddings=True)


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """两个已归一化向量的余弦相似度 ← 等价于点积"""
    return float(np.dot(a, b))


# ===== 带缓存的编码 =====

def cached_encode(text: str) -> np.ndarray:
    """编码并缓存，同一文本只编码一次"""
    if text not in _embed_cache:
        _embed_cache[text] = encode(text)
    return _embed_cache[text]


def cached_encode_batch(texts: List[str]) -> List[np.ndarray]:
    """批量编码并缓存，跳过已缓存的文本"""
    result = [None] * len(texts)
    to_encode = []
    to_encode_indices = []

    for i, t in enumerate(texts):
        if t in _embed_cache:
            result[i] = _embed_cache[t]
        else:
            to_encode.append(t)
            to_encode_indices.append(i)

    if to_encode:
        embs = encode_batch(to_encode)
        for j, idx in enumerate(to_encode_indices):
            emb = embs[j]
            _embed_cache[to_encode[j]] = emb
            result[idx] = emb

    return result


def clear_cache():
    """清空 embedding 缓存（重置时调用）"""
    _embed_cache.clear()


# ===== 高层接口 =====

def text_similarity(a: str, b: str) -> float:
    """两个文本的语义余弦相似度（0-1）"""
    if not a or not b:
        return 0.0
    emb_a = cached_encode(a)
    emb_b = cached_encode(b)
    return _cosine_sim(emb_a, emb_b)


def find_most_similar(
    query: str,
    candidates: List[Tuple[str, Any]],
    threshold: float = 0.4,
) -> Optional[Tuple[Any, float]]:
    """
    在候选列表中找到语义最相似的一条。

    Args:
        query: 查询文本
        candidates: [(text, payload), ...]
        threshold: 最低相似度阈值

    Returns:
        (payload, score) 或 None
    """
    if not query or not candidates:
        return None

    texts = [c[0] for c in candidates]
    query_emb = cached_encode(query)
    cand_embs = cached_encode_batch(texts)

    best_idx = -1
    best_score = 0.0
    for i, emb in enumerate(cand_embs):
        score = _cosine_sim(query_emb, emb)
        if score > best_score:
            best_score = score
            best_idx = i

    if best_idx >= 0 and best_score >= threshold:
        return (candidates[best_idx][1], round(best_score, 4))
    return None


def find_top_k(
    query: str,
    candidates: List[Tuple[str, Any]],
    top_k: int = 3,
    threshold: float = 0.25,
) -> List[Tuple[Any, float]]:
    """
    返回 top_k 个最相似的候选。

    Args:
        query: 查询文本
        candidates: [(text, payload), ...]
        top_k: 返回数量
        threshold: 最低相似度阈值

    Returns:
        [(payload, score), ...] 按分数降序排列
    """
    if not query or not candidates:
        return []

    texts = [c[0] for c in candidates]
    query_emb = cached_encode(query)
    cand_embs = cached_encode_batch(texts)

    scored = []
    for i, emb in enumerate(cand_embs):
        score = _cosine_sim(query_emb, emb)
        if score >= threshold:
            scored.append((candidates[i][1], round(score, 4)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
