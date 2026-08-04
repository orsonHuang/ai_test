"""
fuzzy_matcher.py - 文件名模糊纠错
用标准库 difflib 对玩家输入和可访问文件进行相似度匹配，
处理"入职自立"->"入职资料"这类拼写错误。
"""
from difflib import SequenceMatcher
from typing import Optional, Tuple


DEFAULT_THRESHOLD = 0.6
SHORT_THRESHOLD = 0.5


def _is_close_enough(score: float, user_input: str) -> bool:
    """
    根据输入长度决定是否接受当前相似度。
    短输入（<=4 字符）允许较低阈值，因为中文同音错别字通常差异较小。
    """
    if len(user_input.strip()) <= 4:
        return score >= SHORT_THRESHOLD
    return score >= DEFAULT_THRESHOLD



def _build_candidates(accessible_files):
    """
    为可访问文件构建候选名集合。
    候选包括：完整路径、短路径、文件名、无扩展名文件名。
    """
    candidates = {}
    for path in accessible_files:
        # 完整路径
        candidates[path] = path
        # 短路径（去掉 files/）
        short = path.replace("files/", "")
        candidates[short] = path
        # 无扩展名短路径
        if "." in short:
            name_no_ext = short.rsplit(".", 1)[0]
            candidates[name_no_ext] = path
        # 最后一级文件名
        parts = short.split("/")
        if len(parts) > 1:
            candidates[parts[-1]] = path
            if "." in parts[-1]:
                candidates[parts[-1].rsplit(".", 1)[0]] = path
    return candidates


def correct_filename(
    user_input: str, accessible_files: set, threshold: float = DEFAULT_THRESHOLD
) -> Tuple[Optional[str], float]:
    """
    尝试把玩家输入纠正为一个可访问文件路径。

    Args:
        user_input: 玩家输入（如"入职自立"）
        accessible_files: 当前可访问文件路径集合
        threshold: 最低相似度阈值（0.0~1.0），默认 0.6；短输入自动放宽到 0.5


    Returns:
        (corrected_path, score): 如果未匹配到高置信度文件，返回 (None, best_score)
    """
    if not user_input or not accessible_files:
        return None, 0.0

    candidates = _build_candidates(accessible_files)
    lowered = user_input.lower().strip()

    best_path = None
    best_score = 0.0
    best_candidate = ""

    for candidate, path in candidates.items():
        score = SequenceMatcher(None, lowered, candidate.lower()).ratio()
        if score > best_score:
            best_score = score
            best_path = path
            best_candidate = candidate

    if _is_close_enough(best_score, lowered):
        return best_path, best_score

    return None, best_score


def correct_scan_target(user_input: str, scan_targets: dict, threshold: float = DEFAULT_THRESHOLD) -> Tuple[Optional[str], float]:
    """
    尝试把玩家输入纠正为一个扫描目标 ID。
    scan_targets: {target_id: {"names": [...]}}
    """
    if not user_input or not scan_targets:
        return None, 0.0

    lowered = user_input.lower().strip()
    best_target = None
    best_score = 0.0

    for target_id, config in scan_targets.items():
        for name in config.get("names", []):
            score = SequenceMatcher(None, lowered, name.lower()).ratio()
            if score > best_score:
                best_score = score
                best_target = target_id

    if _is_close_enough(best_score, lowered):
        return best_target, best_score

    return None, best_score

