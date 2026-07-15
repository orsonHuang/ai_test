"""
hidden_file_state.py - 隐藏文件状态管理
管理「显示/隐藏」文件状态：
  - 默认隐藏文件不出现在 file system 和 AI 知识范围中
  - 玩家输入对应隐藏文件的外部显示文件名即可揭示该文件
"""
import json
from pathlib import Path
from typing import Set, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
HIDDEN_FILES_FILE = PROJECT_ROOT / "knowledge" / "hidden-files.json"

_default_hidden_files: Set[str] = set()
_hidden_file_display_names: dict = {}


def _load_registry() -> dict:
    if not HIDDEN_FILES_FILE.exists():
        return {"hidden_files": []}
    try:
        with open(HIDDEN_FILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"hidden_files": []}


def _ensure_loaded():
    global _default_hidden_files, _hidden_file_display_names
    if not _default_hidden_files:
        registry = _load_registry()
        for entry in registry.get("hidden_files", []):
            path = entry.get("path")
            if entry.get("default") == "hidden" and path:
                _default_hidden_files.add(path)
                display_name = entry.get("display_name")
                if display_name:
                    _hidden_file_display_names[path] = display_name


def get_default_hidden_files() -> Set[str]:
    """返回所有默认隐藏的文件路径集合"""
    _ensure_loaded()
    return set(_default_hidden_files)


def is_default_hidden(filepath: str) -> bool:
    """判断文件是否默认隐藏"""
    _ensure_loaded()
    return filepath in _default_hidden_files


def get_display_name(filepath: str) -> Optional[str]:
    """返回隐藏文件的对外显示名，非隐藏文件返回 None"""
    _ensure_loaded()
    return _hidden_file_display_names.get(filepath)


def resolve_hidden_by_display_name(display_name: str) -> Optional[str]:
    """根据外部显示名查找对应的隐藏文件路径"""
    _ensure_loaded()
    for path, name in _hidden_file_display_names.items():
        if name == display_name:
            return path
    return None


def get_revealed_hidden_files(game_state: dict) -> Set[str]:
    """从 game_state 中读取已揭示的隐藏文件集合"""
    hidden_state = game_state.get("hidden_files", {})
    revealed = hidden_state.get("revealed", [])
    return set(revealed) if revealed else set()


def is_file_visible(filepath: str, game_state: dict) -> bool:
    """
    判断文件是否对 AI/玩家可见。
    非隐藏文件始终可见；默认隐藏文件只有在被揭示后才可见。
    """
    if not is_default_hidden(filepath):
        return True
    return filepath in get_revealed_hidden_files(game_state)


def reveal_hidden_file(filepath: str, game_state: dict) -> bool:
    """
    揭示单个隐藏文件。
    返回 True 表示本次为新揭示，False 表示已经揭示过或不是隐藏文件。
    """
    if not is_default_hidden(filepath):
        return False
    hidden_state = game_state.setdefault("hidden_files", {"skill_installed": False, "revealed": []})
    revealed = set(hidden_state.get("revealed", []))
    if filepath in revealed:
        return False
    revealed.add(filepath)
    hidden_state["revealed"] = sorted(revealed)
    return True


def get_visible_files(accessible_files: Set[str], game_state: dict) -> Set[str]:
    """
    从已解锁文件中过滤出当前可见的文件。
    注意：隐藏文件被揭示后应已被加入 accessible_files，这里只需排除尚未揭示的默认隐藏文件。
    """
    hidden = get_default_hidden_files()
    revealed = get_revealed_hidden_files(game_state)
    still_hidden = hidden - revealed
    return accessible_files - still_hidden


def get_hidden_files_in_folder(folder: str, game_state: dict) -> List[str]:
    """
    返回某个文件夹下仍然处于隐藏状态的文件。
    folder: 如 "files/audio" 或 "files/research"
    """
    hidden = get_default_hidden_files()
    revealed = get_revealed_hidden_files(game_state)
    prefix = folder.rstrip("/") + "/"
    return [p for p in hidden if p.startswith(prefix) and p not in revealed]


def get_hidden_files_in_unlocked_folders(accessible_files: Set[str], game_state: dict) -> List[str]:
    """
    返回所有已解锁文件夹中包含的隐藏文件（仍未揭示）。
    一个文件夹被视为已解锁，当其中至少有一个可见文件。
    """
    visible = get_visible_files(accessible_files, game_state)
    unlocked_folders = set()
    for f in visible:
        parts = f.split("/")
        # 收集所有父文件夹路径，如 files/audio
        for i in range(2, len(parts)):
            unlocked_folders.add("/".join(parts[:i]))

    hidden = get_default_hidden_files()
    revealed = get_revealed_hidden_files(game_state)
    result = []
    for path in hidden:
        if path in revealed:
            continue
        folder = "/".join(path.split("/")[:-1])
        if folder in unlocked_folders:
            result.append(path)
    return result
