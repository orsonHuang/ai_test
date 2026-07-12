"""
qa_engine.py - 本地问答库匹配（RAG 轻量版）
用于处理常见基础问题和超纲问题，减少 AI 调用次数
"""
import json
from pathlib import Path
from typing import Optional

from engine.knowledge_search import _tokenize



PROJECT_ROOT = Path(__file__).resolve().parent.parent
QA_FILE = PROJECT_ROOT / "knowledge" / "qa-library.json"


def _load_qa() -> dict:
    """加载 Q&A 知识库"""
    if not QA_FILE.exists():
        return {"categories": {}, "threshold": 0.18}
    try:
        with open(QA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"categories": {}, "threshold": 0.18}


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


def find_answer(user_input: str, chapter: int = 1, min_score: float = None) -> Optional[dict]:
    """
    在 Q&A 库中匹配最佳回答

    匹配策略：
    - 对每条 Q&A 的每个 question 单独计算 Jaccard 相似度
    - 取该条 Q&A 的最高分作为其得分
    - 最后再与 keywords 合并后的 token 集计算一次作为补充
    - 超过阈值且最高的条目返回

    Args:
        user_input: 玩家输入
        chapter: 当前章节，用于章节过滤
        min_score: 自定义阈值，默认使用配置中的 threshold

    Returns:
        {"category": str, "id": str, "answer": str, "score": float} or None
    """
    if not user_input:
        return None

    qa = _load_qa()
    threshold = min_score if min_score is not None else qa.get("threshold", 0.18)
    query_tokens = _tokenize(user_input)
    if not query_tokens:
        return None

    best = None
    best_score = 0.0

    for category, items in qa.get("categories", {}).items():
        for item in items:
            # 章节过滤
            item_chapter = item.get("chapter", "all")
            if item_chapter != "all" and item_chapter != chapter:
                continue

            item_tokens = set()
            max_score = 0.0

            # 逐条 question 计算，避免长问题稀释得分
            for text in item.get("questions", []):
                text_tokens = _tokenize(text)
                if not text_tokens:
                    continue
                intersection = query_tokens & text_tokens
                union = query_tokens | text_tokens
                score = len(intersection) / len(union) if union else 0.0
                if score > max_score:
                    max_score = score
                item_tokens.update(text_tokens)

            # 用 keywords 再算一次作为补充
            for text in item.get("keywords", []):
                text_tokens = _tokenize(text)
                if not text_tokens:
                    continue
                item_tokens.update(text_tokens)
                intersection = query_tokens & text_tokens
                union = query_tokens | text_tokens
                score = len(intersection) / len(union) if union else 0.0
                if score > max_score:
                    max_score = score

            # 所有 questions/keywords 合并后再算一次（兜底）
            if item_tokens:
                intersection = query_tokens & item_tokens
                union = query_tokens | item_tokens
                score = len(intersection) / len(union) if union else 0.0
                if score > max_score:
                    max_score = score

            # 同分情况下，超纲问题优先
            if max_score > best_score or (
                max_score >= best_score
                and max_score > 0
                and _category_priority(category) < _category_priority(best["category"] if best else "")
            ):
                best_score = max_score
                best = {
                    "category": category,
                    "id": item.get("id", ""),
                    "answer": item.get("answer", ""),
                    "score": best_score,
                }

    if best and best_score >= threshold:
        return best
    return None



def is_out_of_scope(user_input: str, chapter: int = 1) -> bool:
    """
    快速判断是否为超纲问题
    如果最佳匹配属于 out_of_scope 类别，返回 True
    """
    result = find_answer(user_input, chapter)
    return result is not None and result.get("category") == "out_of_scope"
