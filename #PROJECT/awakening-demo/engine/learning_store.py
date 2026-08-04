"""
learning_store.py - API 学习闭环

核心目标：当响应库未命中、需要调用 API 时，把 API 生成的结果存入学习库。
下次玩家问类似问题，优先从学习库返回，不再重复消耗 API。

匹配方式：Sentence-Transformers embedding 余弦相似度
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from engine import sentence_matcher


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEARNED_FILE = PROJECT_ROOT / "knowledge" / "learned-library.json"

# 无意义输入，不值得学习/调用 API
STOP_WORDS = {
    "嗯", "哦", "啊", "哈", "好", "好的", "行", "可以", "是的", "没错",
    "ok", "yes", "no", "不知道", "不明白", "不懂", " maybe", "好吧",
}


def _load_store() -> dict:
    """加载学习库"""
    if not LEARNED_FILE.exists():
        return {"version": "1.0", "entries": []}
    try:
        with open(LEARNED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": "1.0", "entries": []}


def _save_store(store: dict):
    """保存学习库"""
    LEARNED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def _hash_input(text: str) -> str:
    """生成输入的短 hash"""
    return hashlib.md5(text.lower().strip().encode("utf-8")).hexdigest()[:12]


def is_worth_learning(user_input: str) -> bool:
    """判断输入是否值得学习和调用 API"""
    text = user_input.strip()
    if len(text) < 4:
        return False
    if text in STOP_WORDS:
        return False
    # 纯标点/无意义内容
    if not re.search(r"[\u4e00-\u9fa5a-zA-Z0-9]", text):
        return False
    return True


def has_similar(user_input: str, threshold: float = 0.45) -> bool:
    """检查学习库中是否有相似输入"""
    return find_similar(user_input, threshold) is not None


def find_similar(user_input: str, threshold: float = 0.45) -> Optional[dict]:
    """
    在学习库中查找语义相似输入（embedding 余弦相似度）。

    Returns:
        {"id": str, "input": str, "reply": str, "chapter": int, "score": float} or None
    """
    store = _load_store()
    entries = store.get("entries", [])
    if not entries:
        return None

    # 收集所有已学习输入的文本
    texts = [e.get("input", "") for e in entries]
    if not any(texts):
        return None

    # 预编码用户输入 + 批量编码所有候选
    query_emb = sentence_matcher.cached_encode(user_input)
    cand_embs = sentence_matcher.cached_encode_batch(texts)

    import numpy as np
    best = None
    best_score = 0.0
    for i, emb in enumerate(cand_embs):
        score = float(np.dot(query_emb, emb))
        if score > best_score:
            best_score = score
            best = entries[i]

    if best and best_score >= threshold:
        return {
            "id": best.get("id", ""),
            "input": best.get("input", ""),
            "reply": best.get("reply", ""),
            "chapter": best.get("chapter", 1),
            "score": round(best_score, 3),
        }
    return None


def add_learned(user_input: str, reply: str, game_state: dict):
    """
    把 API 生成的结果存入学习库

    Args:
        user_input: 玩家输入
        reply: AI 生成的回复
        game_state: 游戏状态（提取 chapter）
    """
    if not is_worth_learning(user_input):
        return

    store = _load_store()
    entries = store.get("entries", [])

    entry = {
        "id": f"learned_{_hash_input(user_input)}",
        "input": user_input.strip(),
        "input_hash": _hash_input(user_input),
        "reply": reply,
        "chapter": game_state.get("chapter", 1),
        "learned_at": datetime.now(timezone.utc).isoformat(),
    }

    entries.append(entry)
    store["entries"] = entries
    _save_store(store)


def clear():
    """清空学习库（重置游戏时调用）"""
    if LEARNED_FILE.exists():
        LEARNED_FILE.unlink()
    sentence_matcher.clear_cache()


def stats() -> dict:
    """返回学习库统计"""
    store = _load_store()
    entries = store.get("entries", [])
    return {"total_entries": len(entries), "file": str(LEARNED_FILE)}
