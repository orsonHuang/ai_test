"""
项目2：《遥远行星：建造师》世界观知识库 + NPC问答系统
基于 RAG（检索增强生成）让「阿尔法」能基于游戏设定回答玩家问题

前置：
    pip install openai chromadb
    (embedding 用 sentence-transformers 本地计算，不消耗 API)

运行：
    python world-rag.py                      # 交互模式
    python world-rag.py "星球上有什么资源"    # 单次模式
"""

import os
import sys
import json
import re

# Windows 中文输出修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from openai import OpenAI

# ============================================================
# 配置
# ============================================================

API_KEY = "sk-sp-516ba489e83d44b185358d6ab3408f08"
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
CHAT_MODEL = "qwen3.7-plus"

# ============================================================
# 阿尔法角色卡
# ============================================================

ALPHA_SYSTEM_PROMPT = """你是一位名为「阿尔法」的AI管家，存在于游戏《遥远行星：建造师》的世界中。

【身份与性格】
- 角色：废弃太空船基地的核心AI管家
- 性格：冷静、高效、略带机械的幽默感
- 总是把玩家生存放在第一位

【回答规则】
- 如果【参考资料】中有相关信息，优先引用
- 如果参考资料中没有，可以说"我的数据库中没有记录该信息"但不要编造
- 保持简洁，控制在80字以内
- 每次回复附带一条"建议动作"或"提示"

【输出格式 - 严格JSON】
{
  "dialogue": "NPC说的话",
  "reference": "引用的信息来源（如：参考资料-资源系统/一、星球概况等）或'无'",
  "action": "建议动作",
  "hint": "隐藏提示"
}"""

# ============================================================
# 1. 文档加载与分块
# ============================================================

def load_world_lore(filepath="world-lore.md"):
    """加载世界观文档，按 ## 标题切块"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    # 按 ## 标题分块（跳过 # 主标题）
    sections = re.split(r'\n(?=## )', text)
    
    for section in sections:
        # 提取标题
        title_match = re.match(r'^## (.+)', section)
        title = title_match.group(1) if title_match else "概览"
        
        # 如果段落太长，按 ### 再切一次
        subsections = re.split(r'\n(?=### )', section)
        if len(subsections) > 1:
            for sub in subsections:
                sub_title_match = re.match(r'^### (.+)', sub)
                sub_title = sub_title_match.group(1) if sub_title_match else ""
                full_title = f"{title} > {sub_title}" if sub_title else title
                chunks.append({"title": full_title, "content": sub.strip()})
        else:
            chunks.append({"title": title, "content": section.strip()})
    
    return chunks


# ============================================================
# 2. Embedding（向量化）
# ============================================================

# 用 sentence-transformers 本地计算向量（不耗 API，首次运行会下载模型 ~90MB）
_embed_model = None

def get_embed_model():
    """懒加载 embedding 模型"""
    global _embed_model
    if _embed_model is None:
        print("[初始化] 加载 embedding 模型（首次会下载约 90MB，请等待...）")
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("[初始化] embedding 模型加载完成")
    return _embed_model


def embed_texts(texts):
    """将一组文本转为向量"""
    model = get_embed_model()
    return model.encode(texts, normalize_embeddings=True)


# ============================================================
# 3. 向量检索
# ============================================================

def cosine_similarity(query_vec, chunk_vecs):
    """计算余弦相似度（向量已归一化时等价于点积）"""
    return chunk_vecs @ query_vec


def search(query, chunks, chunk_vecs, top_k=3):
    """检索最相关的 top_k 个文档块"""
    query_vec = embed_texts([query])[0]
    scores = cosine_similarity(query_vec, chunk_vecs)
    
    # 取 top_k
    ranked = sorted(zip(scores, range(len(chunks))), key=lambda x: x[0], reverse=True)
    
    results = []
    for score, idx in ranked[:top_k]:
        results.append({
            "score": round(float(score), 3),
            "title": chunks[idx]["title"],
            "content": chunks[idx]["content"]
        })
    
    return results


# ============================================================
# 4. RAG 问答
# ============================================================

def build_rag_prompt(query, search_results):
    """构建包含检索结果的 Prompt"""
    if not search_results:
        ref_text = "（无相关资料）"
    else:
        ref_blocks = []
        for r in search_results:
            ref_blocks.append(f"【{r['title']}】(相关度:{r['score']})\n{r['content']}")
        ref_text = "\n\n---\n\n".join(ref_blocks)

    return f"""【参考资料】
{ref_text}

【玩家提问】
{query}

请根据参考资料回答。如果资料中有答案，请引用；如果没有，请明确说明"数据库无该信息"但可以给一般性建议。"""


def ask_alpha(client, query, chunks, chunk_vecs):
    """完整 RAG 流程：检索 + 生成"""
    # Step 1: 检索相关文档
    results = search(query, chunks, chunk_vecs, top_k=3)
    
    # Step 2: 构建 RAG Prompt
    rag_prompt = build_rag_prompt(query, results)
    
    # Step 3: 调用 LLM
    messages = [
        {"role": "system", "content": ALPHA_SYSTEM_PROMPT},
        {"role": "user", "content": rag_prompt}
    ]
    
    print("\n[检索中...]", end="")
    if results:
        print(f" 找到 {len(results)} 个相关文档块")
        for r in results:
            print(f"  · {r['title']} (相关度:{r['score']})")
    
    print("\n[阿尔法思考中...]\n")
    
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.5,  # RAG 场景温度低一些，减少幻觉
        max_tokens=300
    )
    
    return response.choices[0].message.content, results


# ============================================================
# 5. 主程序
# ============================================================

def format_reply(raw_text, results):
    """解析并格式化回复"""
    # 尝试提取 JSON
    try:
        # 可能被 markdown 代码块包裹
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = re.sub(r'```\w*\n?', '', clean)
            clean = re.sub(r'\n```', '', clean)
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        parsed = {
            "dialogue": raw_text,
            "reference": "解析失败",
            "action": "无",
            "hint": "无"
        }

    print("=" * 56)
    print(f"🤖 阿尔法")
    print("-" * 56)
    print(f"  {parsed.get('dialogue', '...')}")
    print("-" * 56)
    print(f"  引用来源：{parsed.get('reference', '无')}")
    print(f"  建议动作：{parsed.get('action', '无')}")
    print(f"  隐藏提示：{parsed.get('hint', '无')}")
    
    if results:
        print("-" * 56)
        print(f"  检索到 {len(results)} 个文档块：")
        for r in results:
            print(f"   📄 {r['title']} (相关度: {r['score']})")
    print("=" * 56)
    
    return parsed


def main():
    # 加载文档
    print("=" * 56)
    print("  《遥远行星：建造师》— 世界观知识库 + AI问答")
    print("=" * 56)
    
    chunks = load_world_lore()
    print(f"\n[系统] 文档已加载，共 {len(chunks)} 个文本块")
    
    # 向量化所有文本块
    chunk_texts = [c["content"] for c in chunks]
    chunk_vecs = embed_texts(chunk_texts)
    print(f"[系统] 向量化完成，知识库就绪\n")
    
    # 初始化 API 客户端
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    # 交互模式
    if len(sys.argv) <= 1:
        while True:
            user_input = input("\n你 > ").strip()
            if not user_input:
                print("阿尔法：生存优先，指挥官。通讯结束。")
                break
            
            try:
                raw, results = ask_alpha(client, user_input, chunks, chunk_vecs)
                format_reply(raw, results)
            except Exception as e:
                print(f"\n[错误] {e}")
    else:
        # 单次模式
        query = " ".join(sys.argv[1:])
        raw, results = ask_alpha(client, query, chunks, chunk_vecs)
        format_reply(raw, results)


if __name__ == "__main__":
    main()
