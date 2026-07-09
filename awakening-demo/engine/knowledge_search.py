"""
knowledge_search.py - 知识库检索
根据玩家问题 + M-M 记忆范围，在知识库中搜索相关内容片段
用于注入 AI prompt 的"知识层"（RAG 的 Retrieval 部分）
"""
import re
from pathlib import Path
from typing import Optional

from engine.file_reader import read_knowledge_file, list_files, KNOWLEDGE_DIR


# ============ 分块 ============

def _split_into_chunks(text: str, max_chunk_size: int = 300) -> list:
    """
    将文本切分为语义块
    - 按段落分割
    - 过长的段落进一步按句号切
    """
    chunks = []
    paragraphs = text.split("\n\n")

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_chunk_size:
            chunks.append(para)
        else:
            # 长段落按句号/换行切分
            sentences = re.split(r"[。！？\n]", para)
            current = ""
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(current) + len(s) + 1 <= max_chunk_size:
                    current += s + "。"
                else:
                    if current:
                        chunks.append(current.strip())
                    current = s + "。"
            if current.strip():
                chunks.append(current.strip())

    return chunks


def _tokenize(text: str) -> set:
    """中文简易分词：按2-3字滑动窗口提取特征词"""
    text = text.lower().strip()
    tokens = set()

    # 2字词
    for i in range(len(text) - 1):
        tokens.add(text[i : i + 2])

    # 3字词
    for i in range(len(text) - 2):
        tokens.add(text[i : i + 3])

    # 英文单词
    for word in re.findall(r"[a-zA-Z]+", text):
        tokens.add(word.lower())

    return tokens


# ============ 检索 ============

def search(
    query: str,
    accessible_files: set,
    top_k: int = 3,
) -> list[dict]:
    """
    在可访问的知识库文件中搜索与查询相关的内容

    Args:
        query: 玩家的问题/输入
        accessible_files: M-M 当前可访问的文件路径集合
        top_k: 返回前 k 个最相关片段

    Returns:
        [{"file": "work-diary/01.md", "score": 0.85, "content": "片段文本"}, ...]
    """
    if not query or not accessible_files:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    results = []

    for filepath in accessible_files:
        content = read_knowledge_file(filepath)
        if not content:
            continue

        chunks = _split_into_chunks(content)
        for chunk in chunks:
            chunk_tokens = _tokenize(chunk)
            if not chunk_tokens:
                continue

            # Jaccard 相似度
            intersection = query_tokens & chunk_tokens
            union = query_tokens | chunk_tokens
            score = len(intersection) / len(union) if union else 0

            if score > 0.05:  # 最低阈值
                results.append(
                    {
                        "file": filepath,
                        "score": round(score, 3),
                        "content": chunk[:500],  # 截断
                    }
                )

    # 按分数排序，去重（相似片段只保留分数最高的）
    results.sort(key=lambda x: x["score"], reverse=True)
    seen = set()
    unique = []
    for r in results:
        key = r["content"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique[:top_k]


# ============ Prompt 组装 ============

def build_knowledge_context(query: str, accessible_files: set, top_k: int = 3) -> str:
    """
    构建注入 AI prompt 的知识上下文字符串
    这是 RAG 架构中的"知识层"

    Returns:
        格式化的知识片段文本，可直接拼入 system prompt
    """
    snippets = search(query, accessible_files, top_k=top_k)

    if not snippets:
        return "（知识库中未找到直接相关信息）"

    parts = ["【知识库检索结果——基于玩家问题找到的相关文件内容】"]
    for i, s in enumerate(snippets, 1):
        parts.append(f"\n[来源 {i}: {s['file']}] (相关度: {s['score']})\n{s['content']}")

    parts.append("\n请基于以上文件内容，用 M-M 的视角回答玩家。不要编造文件中不存在的信息。")
    return "\n".join(parts)


# ============ 批量索引（用于初始化时批量加载） ============

def batch_index_files(filepaths: list) -> dict:
    """
    批量读取并索引文件内容
    返回 {filepath: [chunk1, chunk2, ...]}
    """
    index = {}
    for fp in filepaths:
        content = read_knowledge_file(fp)
        if content:
            index[fp] = _split_into_chunks(content)
    return index
