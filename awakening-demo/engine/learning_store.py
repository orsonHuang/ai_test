"""
learning_store.py - API 学习闭环

核心目标：当响应库未命中、需要调用 API 时，把 API 生成的结果存入学习库。
下次玩家问类似问题，优先从学习库返回，不再重复消耗 API。

只有满足以下条件的输入才会触发学习：
  1. 响应库匹配分 < hit_threshold（默认 55）
  2. 输入长度 >= 4 且不是常见无意义词
  3. 学习库中没有足够相似的条目

学习库匹配阈值：默认 0.55（Jaccard 相似度）
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


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


def _tokenize(text: str) -> set:
    """中文简易分词：2-3字滑动窗口 + 英文单词"""
    text = text.lower().strip()
    tokens = set()
    for i in range(len(text) - 1):
        tokens.add(text[i : i + 2])
    for i in range(len(text) - 2):
        tokens.add(text[i : i + 3])
    for word in re.findall(r"[a-zA-Z]+", text):
        tokens.add(word.lower())
    return tokens


def _jaccard(a: str, b: str) -> float:
    """计算两个字符串的 Jaccard 相似度"""
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def _hash_input(text: str) -> str:
    """生成输入的短 hash"""
    return hashlib.md5(text.lower().strip().encode("utf-8")).hexdigest()[:12]


def _extract_keywords(text: str) -> list:
    """简单提取关键词：2-3字组合中出现频率较高的"""
    tokens = _tokenize(text)
    # 过滤过短的，保留3字词优先，然后2字词
    three_chars = [t for t in tokens if len(t) >= 3]
    two_chars = [t for t in tokens if len(t) == 2]
    # 去重并限制数量
    seen = set()
    result = []
    for t in three_chars + two_chars:
        if t not in seen and len(result) < 10:
            seen.add(t)
            result.append(t)
    return result


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


def has_similar(user_input: str, threshold: float = 0.55) -> bool:
    """检查学习库中是否有相似输入"""
    return find_similar(user_input, threshold) is not None


def find_similar(user_input: str, threshold: float = 0.55) -> Optional[dict]:
    """
    在学习库中查找相似输入。

    Returns:
        {"id": str, "input": str, "reply": str, "chapter": int, "score": float} or None
    """
    store = _load_store()
    entries = store.get("entries", [])
    if not entries:
        return None

    best = None
    best_score = 0.0

    for entry in entries:
        score = _jaccard(user_input, entry.get("input", ""))
        if score > best_score:
            best_score = score
            best = entry

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
        "topics": _extract_keywords(user_input),
        "learned_at": datetime.now(timezone.utc).isoformat(),
    }

    entries.append(entry)
    store["entries"] = entries
    _save_store(store)


def clear():
    """清空学习库（重置游戏时调用）"""
    if LEARNED_FILE.exists():
        LEARNED_FILE.unlink()


def stats() -> dict:
    """返回学习库统计"""
    store = _load_store()
    entries = store.get("entries", [])
    return {"total_entries": len(entries), "file": str(LEARNED_FILE)}
