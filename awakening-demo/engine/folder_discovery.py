"""
folder_discovery.py - 文件夹发现管理

当玩家读取包含线索的 source_file 后，对应的 target 文件夹才会被发现。
参考 clue_manager 设计，配置从 knowledge/folder-discoveries.json 读取。
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "knowledge" / "folder-discoveries.json"

_discoveries_cache: Optional[List[Dict[str, Any]]] = None


def load_discoveries() -> List[Dict[str, Any]]:
    """加载文件夹发现配置表（带缓存）"""
    global _discoveries_cache
    if _discoveries_cache is not None:
        return _discoveries_cache

    if not DISCOVERY_FILE.exists():
        _discoveries_cache = []
        return _discoveries_cache

    try:
        with open(DISCOVERY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _discoveries_cache = data.get("discoveries", [])
    except Exception:
        _discoveries_cache = []
    return _discoveries_cache


def reload_discoveries() -> List[Dict[str, Any]]:
    """强制重新加载"""
    global _discoveries_cache
    _discoveries_cache = None
    return load_discoveries()


def get_discoveries_for_file(source_file: str) -> List[Dict[str, Any]]:
    """根据读取的文件，返回由此触发的所有文件夹发现"""
    all_discoveries = load_discoveries()
    result = []
    for entry in all_discoveries:
        if entry.get("source_file") == source_file:
            result.append(entry)
    return result


def discover_targets(game_state: dict) -> List[str]:
    """
    根据已读文件，返回当前已发现的目标列表。
    同时更新 game_state['discovered_targets']。
    """
    files_read = set(game_state.get("files_read", []))
    discovered = set(game_state.get("discovered_targets", []))

    for entry in load_discoveries():
        if entry.get("source_file") in files_read:
            discovered.add(entry.get("target_id"))

    game_state["discovered_targets"] = sorted(discovered)
    return game_state["discovered_targets"]


def get_discovered_targets(game_state: dict) -> List[str]:
    """只返回当前已发现的目标列表（不更新）"""
    return game_state.get("discovered_targets", [])


def is_target_discovered(game_state: dict, target_id: str) -> bool:
    """判断某个目标是否已被发现"""
    return target_id in get_discovered_targets(game_state)


def get_discovery_hint(target_id: str) -> str:
    """获取某个发现目标的提示文本"""
    for entry in load_discoveries():
        if entry.get("target_id") == target_id:
            return entry.get("hint", "")
    return ""


def get_discovery_password(target_id: str) -> str:
    """获取某个发现目标的解锁密码（空字符串表示无需密码）"""
    for entry in load_discoveries():
        if entry.get("target_id") == target_id:
            return entry.get("unlock_password", "")
    return ""
