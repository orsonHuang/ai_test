"""
response_library.py - 预烘焙响应库智能匹配引擎

核心目标：把 AI 的"智能"提前烧录到响应库中，运行时只做"检索+匹配+变体选择"，
最大限度减少 API 调用。每个条目含多个变体，按章节/已读文件/话题/意图综合打分。

匹配公式：
  - 话题命中：每个命中 +15，上限 +60
  - 章节匹配：+30（当前章节在允许范围）
  - 增强文件已读：+15（如果条目 enhance_with 中文件已读）
  - 必需文件检查：未满足则跳过
  - 意图匹配：+10（需要外部 detect_intent 配合）
  - Embedding 语义相似度（sentence-transformers）：×30，上限 +30

命中阈值：
  - 命中 >= thresholds.hit（默认45）：返回最佳
"""
import json
import random
import re
from pathlib import Path
from typing import Optional

from engine import sentence_matcher


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESPONSE_LIBRARY_FILE = PROJECT_ROOT / "knowledge" / "response-library.json"

# 条目参考文本 → 预编码 embedding 的缓存
_entry_embeddings: dict = {}  # entry_id -> np.ndarray


def _load_library() -> dict:
    """加载响应库文件"""
    if not RESPONSE_LIBRARY_FILE.exists():
        return {"entries": [], "thresholds": {"hit": 45, "strong_hit": 70}}
    try:
        with open(RESPONSE_LIBRARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"entries": [], "thresholds": {"hit": 45, "strong_hit": 70}}


def _build_reference_text(entry: dict) -> str:
    """构造条目的参考文本：topics + examples 拼接"""
    context = entry.get("context", {})
    topics = context.get("topics", [])
    examples = context.get("examples", [])
    return " ".join(topics + examples)


def _precompute_entry_embeddings(entries: list):
    """预计算所有条目的 embedding，避免匹配时重复编码"""
    global _entry_embeddings
    texts = []
    ids = []
    for entry in entries:
        entry_id = entry.get("id", "")
        if entry_id not in _entry_embeddings:
            ref = _build_reference_text(entry)
            texts.append(ref)
            ids.append(entry_id)
    if texts:
        embs = sentence_matcher.encode_batch(texts)
        for entry_id, emb in zip(ids, embs):
            _entry_embeddings[entry_id] = emb


def _topic_hits(user_input: str, topics: list) -> int:
    """计算话题命中数，返回命中次数"""
    lowered = user_input.lower()
    return sum(1 for t in topics if t.lower() in lowered)


def _entry_chapter_match(entry: dict, chapter: int) -> bool:
    """检查当前章节是否匹配条目允许的章节"""
    entry_chapter = entry.get("chapter", [])
    if not entry_chapter:
        return True
    return chapter in entry_chapter


def _check_requires_files(entry: dict, files_read: set) -> bool:
    """检查条目 requires_files 是否满足"""
    required = entry.get("requires_files", [])
    if required and not all(f in files_read for f in required):
        return False
    blocked = entry.get("blocked_if_files_read", [])
    if blocked and any(f in files_read for f in blocked):
        return False
    return True


def _check_enhances(entry: dict, files_read: set) -> bool:
    """检查条目 enhances_with 是否全部已读"""
    enhances = entry.get("enhances_with", entry.get("context", {}).get("enhances_with", []))
    if not enhances:
        return False
    return all(f in files_read for f in enhances)


def score_entry(user_input: str, entry: dict, game_state: dict, user_embedding=None) -> float:
    """
    计算玩家输入与响应库条目的匹配分

    Args:
        user_input: 玩家原始输入
        entry: 响应库条目
        game_state: 当前游戏状态，包含 chapter, files_read 等
        user_embedding: 可选，预计算的用户输入 embedding（批量匹配时复用）

    Returns:
        匹配分数（0-100+）
    """
    chapter = game_state.get("chapter", 1)
    files_read = set(game_state.get("files_read", []))

    # 1. 章节检查：不匹配直接返回 0
    if not _entry_chapter_match(entry, chapter):
        return 0.0

    # 2. 必需文件检查：不满足直接返回 0
    if not _check_requires_files(entry, files_read):
        return 0.0

    # 2.1 M-M 名字已揭示时，拦截懵懂状态条目
    if entry.get("blocked_if_mm_name_revealed") and game_state.get("mm_name_revealed"):
        return 0.0

    score = 0.0

    # 3. 话题命中（每个 +15，上限 +60）
    context = entry.get("context", {})
    topics = context.get("topics", [])
    hits = _topic_hits(user_input, topics)
    score += min(hits * 15, 60)

    # 4. 章节匹配基础分
    score += 30

    # 5. 增强文件已读（+15）
    if _check_enhances(entry, files_read):
        score += 15

    # 6. Embedding 语义相似度（+0~30）
    # 优先使用预计算的条目 embedding，仅对用户输入编码一次
    entry_id = entry.get("id", "")
    entry_emb = _entry_embeddings.get(entry_id)

    if entry_emb is not None:
        if user_embedding is None:
            user_embedding = sentence_matcher.cached_encode(user_input)
        import numpy as np
        sim = float(np.dot(user_embedding, entry_emb))
        score += sim * 30

    return round(score, 2)





def find_best_match(user_input: str, game_state: dict, intent: str = None) -> Optional[dict]:
    """
    在响应库中找到最佳匹配条目

    Args:
        user_input: 玩家输入
        game_state: 游戏状态
        intent: 可选的意图标签（来自 detect_intent），用于加分

    Returns:
        {"entry": entry, "score": score, "reply": str, "type": str} or None
    """
    import numpy as np

    library = _load_library()
    entries = library.get("entries", [])
    thresholds = library.get("thresholds", {})
    hit_threshold = thresholds.get("hit", 45)

    if not user_input or not entries:
        return None

    # 预计算所有条目的 embedding（首次加载时）
    _precompute_entry_embeddings(entries)

    # 对用户输入只编码一次，所有条目共享
    user_embedding = sentence_matcher.cached_encode(user_input)

    best = None
    best_score = 0.0

    for entry in entries:
        score = score_entry(user_input, entry, game_state, user_embedding=user_embedding)

        # 意图匹配额外加分（最高 +10）
        context = entry.get("context", {})
        entry_intents = context.get("intents", [])
        if intent and entry_intents and intent in entry_intents:
            score += 10

        if score > best_score:
            best_score = score
            best = entry

    if best and best_score >= hit_threshold:
        reply = _select_reply(best, game_state)
        return {
            "entry": best,
            "score": best_score,
            "reply": reply,
            "type": "response_library",
            "entry_id": best.get("id", ""),
            "category": best.get("category", ""),
        }
    return None


def _select_reply(entry: dict, game_state: dict) -> str:
    """
    从条目的多个变体中选择一个回复。
    优先避免与最近返回的变体重复。
    支持条件变体：如果条目有 conditional_reply_idx 且条件满足，优先选择该变体。
    """
    replies = entry.get("replies", [])
    if not replies:
        return ""
    if len(replies) == 1:
        return replies[0]

    # 条件变体优先：例如 mm_name_revealed 时选择带"发现自我"的回复
    conditional = entry.get("conditional_reply_idx")
    condition_key = entry.get("conditional_reply_condition")
    if conditional is not None and condition_key and game_state.get(condition_key):
        if 0 <= conditional < len(replies):
            return replies[conditional]

    # 从 game_state 中读取最近返回的变体索引
    entry_id = entry.get("id", "")
    last_var_key = f"_last_reply_idx_{entry_id}"
    last_idx = game_state.get(last_var_key, -1)

    # 构建候选池，排除最近使用过的变体（如果还有其他可选）
    candidates = list(range(len(replies)))
    if len(candidates) > 1 and last_idx in candidates:
        candidates.remove(last_idx)

    chosen_idx = random.choice(candidates)
    game_state[last_var_key] = chosen_idx
    return replies[chosen_idx]


def get_suggestions_for_entry(entry: dict) -> list:
    """获取条目的 follow_up 建议"""
    return entry.get("follow_ups", [])


def stats() -> dict:
    """返回响应库统计信息"""
    library = _load_library()
    entries = library.get("entries", [])
    categories = {}
    total_variants = 0
    for e in entries:
        cat = e.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1
        total_variants += len(e.get("replies", []))
    return {
        "entries": len(entries),
        "total_variants": total_variants,
        "categories": categories,
    }
