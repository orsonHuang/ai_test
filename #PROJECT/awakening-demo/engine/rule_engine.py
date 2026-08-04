"""
rule_engine.py - 轻量规则辅助

原关键词模板系统已废弃，功能由 response_library.py 替代。
本文件保留两类轻量匹配：
  1. find_file_suggestion：检测玩家是否在询问某类文件（如"读日记""看看邮件"）
  2. find_file_commentary：读取文件时触发 M-M 的插嘴台词（数据源：response-library.json）
"""
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESPONSE_LIBRARY_FILE = PROJECT_ROOT / "knowledge" / "response-library.json"


def _load_response_library() -> dict:
    """加载响应库文件"""
    if not RESPONSE_LIBRARY_FILE.exists():
        return {}
    try:
        with open(RESPONSE_LIBRARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def find_file_suggestion(user_input: str):  # -> str or None
    """
    检测玩家是否在询问某类文件（如"看看邮件""读日记"）
    """
    file_triggers = {
        "邮件": "emails",
        "邮箱": "emails",
        "mail": "emails",
        "日记": "work-diary",
        "diary": "work-diary",
        "工作日记": "work-diary",
        "研究": "research",
        "笔记": "research",
    }
    user_lower = user_input.lower()
    for trigger, dir_name in file_triggers.items():
        if trigger in user_lower:
            return dir_name
    return None


# ============ M-M 文件阅读插嘴 ============
def find_file_commentary(filename: str, chapter: int, files_read: list, game_state: dict = None) -> str:
    """
    根据刚读取的文件名，返回 M-M 的插嘴台词。
    调用方负责只在第一次读取时触发，本函数不再重复检查。

    数据源：response-library.json 中 category 为 file_commentary 的条目，
    通过条目的 file_commentary 字段匹配文件名，支持条件变体。
    """
    library = _load_response_library()
    for entry in library.get("entries", []):
        if entry.get("category") != "file_commentary":
            continue

        fc = entry.get("file_commentary", "")
        if not fc or fc not in filename:
            continue

        rule_chapter = entry.get("chapter", [])
        if rule_chapter and chapter not in rule_chapter:
            continue

        # 检查必需文件是否已读
        required = entry.get("requires_files", [])
        if required and not all(f in files_read for f in required):
            continue

        # 检查是否被 mm_name_revealed 拦截
        if entry.get("blocked_if_mm_name_revealed") and game_state and game_state.get("mm_name_revealed"):
            continue

        replies = entry.get("replies", [])
        if not replies:
            continue

        # 条件变体：例如 mm_name_revealed 时选择特定回复
        conditional = entry.get("conditional_reply_idx")
        condition_key = entry.get("conditional_reply_condition")
        if (conditional is not None and condition_key and game_state
                and game_state.get(condition_key)):
            if 0 <= conditional < len(replies):
                return replies[conditional]

        return replies[0]

    return ""

