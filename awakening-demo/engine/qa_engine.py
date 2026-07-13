"""
qa_engine.py - 本地问答库匹配（Embedding 版）
使用 Sentence-Transformers embedding 余弦相似度替代 Jaccard。
"""
import json
from pathlib import Path
from typing import Optional

from engine import sentence_matcher


PROJECT_ROOT = Path(__file__).resolve().parent.parent
QA_FILE = PROJECT_ROOT / "knowledge" / "qa-library.json"


def _load_qa() -> dict:
    """加载 Q&A 知识库"""
    if not QA_FILE.exists():
        return {"categories": {}, "threshold": 0.4}
    try:
        with open(QA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"categories": {}, "threshold": 0.4}


def _category_priority(category: str) -> int:
    """
    类别优先级：超纲问题优先命中，避免浪费 AI 额度
    基础问题次之，主观评价最后
    """
    priorities = {
        "out_of_scope": 0,
        "basic_identity": 1,
        "basic_gameplay": 2,
        "basic_story": 3,
        "folder_help": 2,
        "opinion": 4,
    }
    return priorities.get(category, 5)


def _select_answer(item: dict, game_state: dict = None) -> str:
    """
    根据条件选择条目的回答文本。
    支持 conditional_answers：按 requires_files_read 判断返回哪个变体。
    优先匹配最后一条满足条件的（表示最新游戏进度）。
    """
    files_read = set(game_state.get("files_read", [])) if game_state else set()

    # 反向遍历，优先返回最后匹配的（最新进度）
    for cond in reversed(item.get("conditional_answers", [])):
        required = cond.get("requires_files_read", [])
        if required and all(f in files_read for f in required):
            return cond.get("answer", item.get("answer", ""))

    return item.get("answer", "")


def find_answer(user_input: str, chapter: int = 1,
                min_score: float = None, game_state: dict = None) -> Optional[dict]:
    """
    在 Q&A 库中匹配最佳回答（embedding 余弦相似度）

    Args:
        user_input: 玩家输入
        chapter: 当前章节，用于章节过滤
        min_score: 自定义阈值，默认使用配置中的 threshold
        game_state: 当前游戏状态，用于条件回答判断

    Returns:
        {"category": str, "id": str, "answer": str, "score": float} or None
    """
    if not user_input:
        return None

    qa = _load_qa()
    threshold = min_score if min_score is not None else qa.get("threshold", 0.4)

    # 收集所有 QA 条目的参考文本（question + keywords 拼接）
    candidates = []  # [(ref_text, (category, item)), ...]
    for category, items in qa.get("categories", {}).items():
        for item in items:
            # 章节过滤
            item_chapter = item.get("chapter", "all")
            if item_chapter != "all" and item_chapter != chapter:
                continue
            # 构建参考文本
            parts = item.get("questions", []) + item.get("keywords", [])
            ref_text = " ".join(parts)
            if ref_text.strip():
                candidates.append((ref_text, (category, item)))

    if not candidates:
        return None

    # 批量编码 query + 所有候选
    texts = [user_input] + [c[0] for c in candidates]
    import numpy as np
    all_embs = sentence_matcher.encode_batch(texts)
    query_emb = all_embs[0]

    best = None
    best_score = 0.0

    for i, (_, (category, item)) in enumerate(candidates):
        score = float(np.dot(query_emb, all_embs[i + 1]))
        # 同分时超纲优先
        if score > best_score or (
            score >= best_score and score > 0
            and _category_priority(category) < _category_priority(best["category"] if best else "")
        ):
            best_score = score
            best = {
                "category": category,
                "id": item.get("id", ""),
                "answer": _select_answer(item, game_state),
                "score": round(score, 4),
            }

    if best and best_score >= threshold:
        return best
    return None


def is_out_of_scope(user_input: str, chapter: int = 1, game_state: dict = None) -> bool:
    """
    快速判断是否为超纲问题
    """
    result = find_answer(user_input, chapter, game_state=game_state)
    return result is not None and result.get("category") == "out_of_scope"
