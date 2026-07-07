"""
cache_manager.py - 缓存管理
存储AI生成的回复，避免重复调用API
"""
import json
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_FILE = CACHE_DIR / "ai_responses.json"


def _ensure_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _load_data() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_data(data: dict):
    _ensure_dir()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize(text: str) -> str:
    """标准化输入：去空格、取前30字、生成hash"""
    text = text.strip()[:30]
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def get(user_input: str, chapter: int) -> str | None:
    """查询缓存的AI回复"""
    data = _load_data()
    key = f"{chapter}:{_normalize(user_input)}"
    return data.get(key)


def set(user_input: str, value: str, chapter: int):
    """存储AI回复到缓存"""
    data = _load_data()
    key = f"{chapter}:{_normalize(user_input)}"
    data[key] = value
    _save_data(data)


def clear():
    """清空缓存（重置游戏时调用）"""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def stats() -> dict:
    """缓存统计"""
    data = _load_data()
    return {"total_entries": len(data), "file": str(CACHE_FILE)}
