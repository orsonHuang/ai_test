"""
rule_engine.py - 规则匹配
从 keyword-rules.json 加载模板，根据玩家输入匹配模板回复
"""
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_FILE = PROJECT_ROOT / "knowledge" / "triggers" / "keyword-rules.json"


def _load_rules() -> list:
    """加载规则文件，不存在则返回空列表"""
    if not RULES_FILE.exists():
        return []
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("rules", [])
    except Exception:
        return []


def match_keyword_template(user_input: str, chapter: int) -> str | None:
    """
    匹配关键词模板
    返回模板字符串或None
    """
    if not user_input:
        return None

    rules = _load_rules()
    user_input_lower = user_input.lower().strip()

    for rule in rules:
        rule_chapter = rule.get("chapter", "all")
        # 章节过滤：当前章或全局
        if rule_chapter != "all" and rule_chapter != chapter:
            continue

        keywords = rule.get("keywords", [])
        for kw in keywords:
            if kw.lower() in user_input_lower:
                return rule.get("reply", "")

    return None


def find_file_suggestion(user_input: str) -> str | None:
    """
    检测玩家是否在询问文件（如"看看邮件"、"读日记"）
    """
    file_triggers = {
        "邮件": "emails",
        "邮箱": "emails",
        "mail": "emails",
        "日记": "diary",
        "diary": "diary",
        "研究": "research",
        "笔记": "research",
    }
    user_lower = user_input.lower()
    for trigger, dir_name in file_triggers.items():
        if trigger in user_lower:
            return dir_name
    return None
