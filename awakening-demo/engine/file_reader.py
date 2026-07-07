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
