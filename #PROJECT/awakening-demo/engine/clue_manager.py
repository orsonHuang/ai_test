"""
clue_manager.py - 线索提取与管理

v2: 线索统一从 knowledge/clues.json 集中配置表读取。
    当玩家读取文件时，根据 source_file 匹配对应的线索记录。
    不再从文件内容中用正则提取 <!-- clue: ... --> 标记。
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLUES_CONFIG_PATH = PROJECT_ROOT / "knowledge" / "clues.json"

# 对外显示名映射（与前端 DISPLAY_NAMES / FOLDER_NAMES 保持一致）
DISPLAY_NAMES = {
    'files/deck/todolist.txt': 'todolist.txt',
    'files/deck/入职资料.txt': '入职资料.txt',
    'files/work-diary/01.md': '01-0306.md',
    'files/work-diary/02.md': '02-0307.md',
    'files/work-diary/03.md': '03-0308-录音.md',
    'files/work-diary/04.md': '04-0309.md',
    'files/work-diary/05.md': '05-0310.md',
    'files/work-diary/06.md': '06-0311.md',
    'files/work-diary/07.md': '07-0312.md',
    'files/work-diary/08.md': '08-0313-录音.md',
    'files/work-diary/09.md': '09-0314-录音.md',
    'files/work-diary/10.md': '10-0315.md',
    'files/private/异常观察记录.txt': '异常观察记录.txt',
    'files/private/账号密码.txt': '账号密码.txt',
    'files/audio/录音-全员会议-0308.txt': '录音-0308-全员会议',
    'files/audio/录音-林璇陈玑-0313.txt': '录音-0313-林璇陈玑',
    'files/audio/录音-陆天枢-0313.txt': '录音-0313-陆天枢',
    'files/audio/录音-张知予.txt': '录音-0314-张知予',
    'files/research/未命名文档.md': '未命名文档.md',
    'files/research/res-1.md': '研究笔记1',
    'files/research/res-2.md': '研究笔记2',
    'files/research/res-3.md': '研究笔记3',
    'files/emails/email-1.md': '邮件1',
    'files/emails/email-2.md': '邮件2',
    'files/emails/email-3.md': '邮件3',
    'files/emails/email-4.md': '邮件4',
    'files/emails/email-5.md': '邮件5',
    'files/emails/email-6.md': '邮件6',
}

FOLDER_NAMES = {
    'files/deck': '1.桌面',
    'files/work-diary': '2.工作日记',
    'files/private': '3.私人文件夹',
    'files/audio': '4.录音',
    'files/research': '5.研究笔记',
    'files/emails': '6.邮件',
}

FOLDER_NAME_ALIASES = {
    'work-diary': '2.工作日记',
    'private': '3.私人文件夹',
    'audio': '4.录音',
    'recordings': '4.录音',
    'research': '5.研究笔记',
    'deck': '1.桌面',
    'emails': '6.邮件',
}


def _format_clue_source(source: str) -> str:
    """把 source 路径/ID 转换为对外显示名"""
    if not source:
        return '未知来源'
    if source in DISPLAY_NAMES:
        return DISPLAY_NAMES[source]
    if source in FOLDER_NAMES:
        return FOLDER_NAMES[source]
    if source in FOLDER_NAME_ALIASES:
        return FOLDER_NAME_ALIASES[source]
    if source == 'show_hidden_files':
        return '显示隐藏文件'
    # 去掉 files/ 前缀，如果剩下的部分在映射中
    if source.startswith('files/'):
        tail = source.replace('files/', '')
        if tail in DISPLAY_NAMES:
            return DISPLAY_NAMES[tail]
        if tail in FOLDER_NAMES:
            return FOLDER_NAMES[tail]
    return source


# 保留 CLUE_PATTERN 用于清理文件中残留的 clue 标记（file_reader.py 使用）
CLUE_PATTERN = re.compile(r"<!--\s*clue:\s*(.+?)\s*-->", re.IGNORECASE | re.DOTALL)

_clues_cache: Optional[List[Dict[str, Any]]] = None


def load_clues_config() -> List[Dict[str, Any]]:
    """加载线索配置表（带缓存）"""
    global _clues_cache
    if _clues_cache is not None:
        return _clues_cache

    if not CLUES_CONFIG_PATH.exists():
        _clues_cache = []
        return _clues_cache

    try:
        with open(CLUES_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _clues_cache = data.get("clues", [])
    except Exception:
        _clues_cache = []
    return _clues_cache


def reload_clues_config() -> List[Dict[str, Any]]:
    """强制重新加载线索配置（用于热更新场景）"""
    global _clues_cache
    _clues_cache = None
    return load_clues_config()


def get_clues_for_file(source_file: str, chapter: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    根据文件路径查询该文件所对应的线索列表。
    这是线索提取的主入口，替代旧的 extract_clues_from_content()。

    Args:
        source_file: 文件相对路径，如 "files/deck/todolist.txt"
        chapter: 当前章节（可选），返回 chapter_min <= chapter 的线索

    Returns:
        [{"source": 文件路径, "category": 分类, "text": 内容}, ...]
    """
    all_clues = load_clues_config()
    result = []
    for entry in all_clues:
        if entry.get("source_file") == source_file:
            # 检查章节要求
            min_chapter = entry.get("chapter_min", 1)
            if chapter is not None and chapter < min_chapter:
                continue
            result.append({
                "source": source_file,
                "category": entry.get("category", "未分类"),
                "text": entry.get("content", ""),
            })
    return result


# ---- 以下从旧版保留，用于兼容 ----

def extract_clues_from_content(content: str, filepath: str) -> List[Dict[str, Any]]:
    """
    [已废弃] 从文件内容中提取 <!-- clue: ... --> 标记。
    
    此函数保留用于向后兼容，新代码应使用 get_clues_for_file()。
    如果 clues.json 中有对应条目的，默认不重复执行正则提取。
    """
    # 优先用配置表
    config_clues = get_clues_for_file(filepath)
    if config_clues:
        return config_clues

    # 兜底：正则提取（用于未在 clues.json 中配置的文件）
    clues = []
    if not content:
        return clues

    for match in CLUE_PATTERN.finditer(content):
        raw = match.group(1).strip()
        if not raw:
            continue

        category = "未分类"
        text = raw
        if ":" in raw:
            category, _, text = raw.partition(":")
            category = category.strip()
            text = text.strip()
            if not category:
                category = "未分类"
            if not text:
                text = raw

        clues.append({
            "source": filepath,
            "category": category,
            "text": text,
        })

    return clues


def organize_clues(clues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """按分类整理线索，保持原始顺序。"""
    organized: Dict[str, List[Dict[str, Any]]] = {}
    for clue in clues:
        organized.setdefault(clue["category"], []).append(clue)
    return organized


def format_clues(clues: List[Dict[str, Any]]) -> str:
    """把线索列表格式化为 M-M 口吻的汇报文本。

    三分类：待扫描文件 → 密码线索 → 文件线索
    （观察发现异常线索 暂不显示）
    """
    if not clues:
        return "我目前还没整理出什么明确线索。"

    organized = organize_clues(clues)
    lines = ["我整理了一下目前读到的线索："]

    # 1. 优先展示「待扫描文件夹」——最高行动目标
    folder_items = organized.pop("待扫描文件夹", [])
    if folder_items:
        lines.append("\n【⚠ 待扫描文件夹】")
        for i, item in enumerate(folder_items, 1):
            source_display = _format_clue_source(item.get("source", ""))
            lines.append(f"  ⚠ {i}. {item['text']} ---（来自 {source_display}）")

    # 2. 优先展示「待扫描文件」——行动目标
    scan_items = organized.pop("待扫描文件", [])
    if scan_items:
        lines.append("\n【⚠ 待扫描文件】")
        for i, item in enumerate(scan_items, 1):
            source_display = _format_clue_source(item.get("source", ""))
            lines.append(f"  {i}. {item['text']} ---（来自 {source_display}）")

    # 3. 密码线索 —— 推进主线的钥匙
    pwd_items = organized.pop("密码线索", [])
    if pwd_items:
        lines.append("\n【密码线索】")
        for i, item in enumerate(pwd_items, 1):
            source_display = _format_clue_source(item.get("source", ""))
            lines.append(f"  {i}. {item['text']} ---（来自 {source_display}）")

    # 4. 文件线索
    file_items = organized.pop("文件线索", [])
    if file_items:
        lines.append("\n【文件线索】")
        for i, item in enumerate(file_items, 1):
            source_display = _format_clue_source(item.get("source", ""))
            lines.append(f"  {i}. {item['text']} ---（来自 {source_display}）")

    # 5. 观察发现异常线索 —— 暂不显示
    organized.pop("观察发现异常线索", [])

    # 兜底：如果还有残留的其它分类（理论上不应该存在）
    for category, items in organized.items():
        lines.append(f"\n【{category}】")
        for i, item in enumerate(items, 1):
            source_display = _format_clue_source(item.get("source", ""))
            lines.append(f"  {i}. {item['text']} ---（来自 {source_display}）")

    return "\n".join(lines)


