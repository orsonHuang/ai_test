"""
file_reader.py - 知识库读取
读取 knowledge/ 下的文件内容供AI引用
"""
from pathlib import Path
from typing import Optional


# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def read_knowledge_file(rel_path: str) -> Optional[str]:
    """
    读取知识库文件
    rel_path: 相对 knowledge/ 的路径，如 "files/welcome.txt"
    """
    # 安全检查：防止路径穿越
    if ".." in rel_path or rel_path.startswith("/"):
        return None

    file_path = KNOWLEDGE_DIR / rel_path
    if not file_path.exists() or not file_path.is_file():
        return None

    try:
        return file_path.read_text(encoding="utf-8")
    except Exception:
        return None


def list_files(sub_dir: str) -> list:
    """
    列出子目录下的所有文件
    sub_dir: 如 "files" "files/emails" "plot"
    """
    if ".." in sub_dir or sub_dir.startswith("/"):
        return []

    target = KNOWLEDGE_DIR / sub_dir
    if not target.exists() or not target.is_dir():
        return []

    files = []
    for item in sorted(target.rglob("*")):
        if item.is_file():
            rel = item.relative_to(target)
            files.append(str(rel).replace("\\", "/"))
    return files


def find_file_in_knowledge(filename: str) -> Optional[str]:
    """
    在 knowledge/ 下递归查找文件
    filename: 如 "welcome.txt" 或 "1.md"
    """
    for f in KNOWLEDGE_DIR.rglob(filename):
        if f.is_file():
            try:
                return f.read_text(encoding="utf-8")
            except Exception:
                continue
    return None


def resolve_file_path(raw_path: str) -> Optional[str]:
    """
    智能解析文件路径，支持多种输入格式：
    - "todolist.txt" → 查找 files/todolist.txt
    - "diary/01.md" → 查找 work-diary/01.md
    - "录音/xxx.txt" → 查找 company/录音/xxx.txt
    返回相对 knowledge/ 的路径，或 None
    """
    if ".." in raw_path or raw_path.startswith("/"):
        return None

    # 1. 精确路径
    file_path = KNOWLEDGE_DIR / raw_path
    if file_path.exists() and file_path.is_file():
        return raw_path

    # 2. files/ 前缀
    file_path = KNOWLEDGE_DIR / "files" / raw_path
    if file_path.exists() and file_path.is_file():
        return f"files/{raw_path}"

    # 3. 递归查找
    filename = raw_path.split("/")[-1] if "/" in raw_path else raw_path
    for f in KNOWLEDGE_DIR.rglob(filename):
        if f.is_file():
            rel = f.relative_to(KNOWLEDGE_DIR)
            return str(rel).replace("\\", "/")

    return None


def get_file_summary(filepath: str, max_chars: int = 80) -> str:
    """
    获取文件内容摘要（前 max_chars 个字符，去掉 markdown 标记）
    """
    content = read_knowledge_file(filepath)
    if not content:
        return f"[空文件: {filepath}]"

    # 去掉 markdown 标题标记
    lines = content.strip().split("\n")
    clean_lines = []
    for line in lines[:5]:
        line = line.strip()
        if line.startswith("#"):
            line = line.lstrip("# ").strip()
        if line:
            clean_lines.append(line)

    summary = " ".join(clean_lines)
    if len(summary) > max_chars:
        summary = summary[:max_chars] + "..."
    return summary if summary else f"[{filepath}]"
