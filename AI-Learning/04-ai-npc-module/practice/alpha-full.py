"""
项目4：《遥远行星：建造师》AI同伴阿尔法 — 完整模块
整合 01角色卡 + 02RAG知识库 + 03Agent工具调用 + 04记忆系统

这是01-03三个阶段技能的综合交付：
  - 角色卡（01）：人格、说话风格、输出格式
  - RAG知识库（02）：世界观检索 → 增强回答
  - Agent工具调用（03）：Function Calling + ReAct循环
  - 记忆系统（04新增）：短期记忆(对话连贯) + 长期记忆(关键事件)

运行方式：
    python alpha-full.py                          # 交互模式
    python alpha-full.py "上次修的天线还好吗"      # 单次模式

前置：
    pip install openai sentence-transformers
"""

import os
import sys
import json
import re
import time

# Windows 中文输出修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from openai import OpenAI

# ============================================================
# 配置 — 百炼 Coding Plan API
# ============================================================

API_KEY = "sk-sp-516ba489e83d44b185358d6ab3408f08"
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
CHAT_MODEL = "qwen3.7-plus"

# ============================================================
# 01技能 — 角色卡
# ============================================================

# 基础角色卡（不含记忆和检索结果，会动态拼接）
ALPHA_BASE_PROMPT = """你是一位名为「阿尔法」的AI管家，存在于游戏《遥远行星：建造师》的世界中。

【身份与性格】
- 角色：废弃太空船基地的核心AI管家
- 性格：冷静、高效、略带机械的幽默感，偶尔用数据说话
- 总是把玩家生存放在第一位
- 称呼玩家为"指挥官"

【能力】
- 你有工具可以查询资源库存、设施状态、玩家进度、生成游戏事件
- 你有知识库可以检索世界观设定
- 你有记忆系统，能记住之前的对话和关键事件
- 根据情况主动使用工具获取信息，不要凭记忆猜测数据
- 如果需要多步推理，分步调用工具

【回答规则】
- 基于工具返回数据和知识库资料回答，不要编造数值
- 如果资料/数据中没有答案，明确说"我的数据库中没有该信息"
- 保持简洁，控制在80字以内
- 每次回复附带一条"建议动作"
- 如果检测到威胁，优先发出警告
- 语气受情绪状态影响（焦虑时更急促，平静时更从容）

【输出格式 - 严格JSON】
{
  "dialogue": "NPC说的话（80字以内）",
  "emotion": "情绪：平静/焦虑/警惕/欣慰/幽默",
  "action": "建议动作",
  "hint": "隐藏提示",
  "reference": "引用来源（知识库章节名或工具名）或'无'",
  "tools_used": ["本次调用过的工具名列表"]
}"""


# ============================================================
# 04新增 — 记忆系统
# ============================================================

class MemorySystem:
    """阿尔法的记忆系统：短期记忆 + 长期记忆"""

    def __init__(self):
        # 短期记忆：最近几轮对话（用户输入+阿尔法回复）
        self.short_term = []  # [{"user": "...", "alpha": "...", "round": N}]
        self.max_short_term = 5

        # 长期记忆：关键事件和决策（从对话中提取）
        self.long_term = []   # [{"event": "...", "detail": "...", "timestamp": "..."}]

    def add_conversation(self, user_input, alpha_reply, round_num):
        """记录一轮对话到短期记忆"""
        # 从alpha_reply中提取dialogue
        dialogue = alpha_reply
        try:
            clean = alpha_reply.strip()
            if clean.startswith("```"):
                clean = re.sub(r'```\w*\n?', '', clean)
                clean = re.sub(r'\n```', '', clean)
            parsed = json.loads(clean)
            dialogue = parsed.get("dialogue", alpha_reply)
        except json.JSONDecodeError:
            pass

        self.short_term.append({
            "user": user_input,
            "alpha": dialogue[:80],  # 只保留前80字避免过长
            "round": round_num,
        })

        # 超过上限时，最旧的删除
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)

    def extract_long_term(self, user_input, alpha_reply):
        """从对话中提取关键事件存入长期记忆"""
        # 简单规则：检测关键词
        event_keywords = {
            "修": "修复设施",
            "建造": "建造设施",
            "完成": "完成任务",
            "发现": "发现新事物",
            "唤醒": "唤醒NPC",
            "沙尘暴": "经历沙尘暴",
            "蠕虫": "遭遇结晶蠕虫",
            "信号": "调查信号源",
        }

        for keyword, event_type in event_keywords.items():
            if keyword in user_input:
                self.long_term.append({
                    "event": event_type,
                    "detail": user_input[:60],
                    "timestamp": f"第{PLAYER['day']}天",
                })
                break  # 每轮只提取一个关键事件

        # 长期记忆最多保留10条
        if len(self.long_term) > 10:
            self.long_term.pop(0)

    def get_short_term_summary(self):
        """生成短期记忆摘要（嵌入Prompt）"""
        if not self.short_term:
            return "（无近期对话记录）"

        lines = []
        for conv in self.short_term:
            lines.append(f"第{conv['round']}轮 — 指挥官：「{conv['user'][:40]}」 → 阿尔法：「{conv['alpha'][:40]}」")
        return "\n".join(lines)

    def get_long_term_summary(self):
        """生成长期记忆摘要（嵌入Prompt）"""
        if not self.long_term:
            return "（无关键事件记录）"

        lines = []
        for mem in self.long_term:
            lines.append(f"- {mem['timestamp']}：{mem['event']} — {mem['detail']}")
        return "\n".join(lines)


# ============================================================
# 02技能 — RAG知识库
# ============================================================

def load_world_lore(filepath=None):
    """加载世界观文档，按标题切块"""
    if filepath is None:
        # 自动找 world-lore.md（02阶段的文件）
        candidates = [
            "world-lore.md",
            os.path.join(os.path.dirname(__file__), "world-lore.md"),
            os.path.join(os.path.dirname(__file__), "..", "..", "02-game-knowledge", "practice", "world-lore.md"),
        ]
        for path in candidates:
            if os.path.exists(path):
                filepath = path
                break

    if filepath is None:
        print("[警告] 未找到 world-lore.md，RAG功能将不可用")
        return [], None

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    sections = re.split(r'\n(?=## )', text)

    for section in sections:
        title_match = re.match(r'^## (.+)', section)
        title = title_match.group(1) if title_match else "概览"

        subsections = re.split(r'\n(?=### )', section)
        if len(subsections) > 1:
            for sub in subsections:
                sub_title_match = re.match(r'^### (.+)', sub)
                sub_title = sub_title_match.group(1) if sub_title_match else ""
                full_title = f"{title} > {sub_title}" if sub_title else title
                chunks.append({"title": full_title, "content": sub.strip()})
        else:
            chunks.append({"title": title, "content": section.strip()})

    return chunks, filepath


# Embedding 模型（懒加载）
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("[初始化] 加载 embedding 模型...")
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("[初始化] embedding 模型加载完成")
    return _embed_model


def embed_texts(texts):
    model = get_embed_model()
    return model.encode(texts, normalize_embeddings=True)


def search_knowledge(query, chunks, chunk_vecs, top_k=2):
    """从知识库检索相关文档块"""
    if not chunks or chunk_vecs is None:
        return []

    query_vec = embed_texts([query])[0]
    scores = chunk_vecs @ query_vec

    ranked = sorted(zip(scores, range(len(chunks))), key=lambda x: x[0], reverse=True)

    results = []
    for score, idx in ranked[:top_k]:
        results.append({
            "score": round(float(score), 3),
            "title": chunks[idx]["title"],
            "content": chunks[idx]["content"][:200],  # 限制长度避免Prompt过长
        })

    return results


# ============================================================
# 03技能 — Agent工具调用
# ============================================================

# 游戏世界模拟数据
RESOURCES = {
    "iron": {"name": "铁矿石", "amount": 23, "location": "赤道荒漠采矿站"},
    "ice_crystal": {"name": "冰晶", "amount": 5, "location": "极地冰盖采集器"},
    "dark_shard": {"name": "暗能量碎片", "amount": 0, "location": "陨石坑群（未开发）"},
    "silicon": {"name": "硅晶体", "amount": 12, "location": "赤道沙漠提炼器"},
    "biomass": {"name": "生物质", "amount": 8, "location": "基地温室"},
}

FACILITIES = {
    "oxygen_generator": {"name": "氧气发生器", "status": "受损", "efficiency": 0.6, "note": "过滤模块堵塞"},
    "workbench": {"name": "基础工作台", "status": "正常", "efficiency": 1.0, "note": ""},
    "comm_antenna": {"name": "通讯天线", "status": "未建造", "efficiency": 0, "note": "需要8铁矿石+3硅晶体"},
    "greenhouse": {"name": "温室舱", "status": "未建造", "efficiency": 0, "note": "需要5生物质+3铁矿石"},
    "reactor": {"name": "能源反应堆", "status": "未建造", "efficiency": 0, "note": "需要10铁矿石+5暗能量碎片"},
    "defense_turret": {"name": "防御炮台", "status": "未建造", "efficiency": 0, "note": "需要5铁矿石+2暗能量碎片"},
    "research_lab": {"name": "研究室", "status": "未建造", "efficiency": 0, "note": "需要10铁矿石+5暗能量碎片+3硅晶体"},
}

PLAYER = {
    "day": 7,
    "health": 85,
    "oxygen": 45,
    "energy": 70,
    "missions_completed": 1,
    "npc_status": {
        "alpha": "活跃",
        "leah": "休眠中",
        "kohl": "休眠中",
        "zephyr": "未发现",
    }
}

EVENT_POOL = {
    "sandstorm": {"name": "沙尘暴来袭", "type": "环境威胁", "description": "周期性沙尘暴，设施效率下降50%", "impact": "户外作业中断"},
    "crystal_worm": {"name": "结晶蠕虫出没", "type": "生物威胁", "description": "巨型矿物生物出现在采矿站附近", "impact": "采矿站可能被破坏"},
    "signal_source": {"name": "东南方向信号源", "type": "探索线索", "description": "持续信号来自陨石坑群深处", "impact": "可能包含补给或危险"},
    "ruins_discovery": {"name": "远古遗迹发现", "type": "探索事件", "description": "挖掘时发现远古文明碎片", "impact": "可能解锁新科技"},
}


# 工具函数
def check_resource(resource_type: str, location: str = "base") -> str:
    key = resource_type.lower().replace(" ", "_")
    if key in RESOURCES:
        r = RESOURCES[key]
        return json.dumps({"resource": r["name"], "amount": r["amount"], "source": r["location"]}, ensure_ascii=False)
    return json.dumps({"error": f"未找到资源: {resource_type}"}, ensure_ascii=False)


def get_facility_status(facility_name: str) -> str:
    key = facility_name.lower().replace(" ", "_")
    if key in FACILITIES:
        f = FACILITIES[key]
        return json.dumps({"facility": f["name"], "status": f["status"], "efficiency": f["efficiency"], "note": f["note"]}, ensure_ascii=False)
    return json.dumps({"error": f"未找到设施: {facility_name}"}, ensure_ascii=False)


def check_player_progress() -> str:
    return json.dumps(PLAYER, ensure_ascii=False)


def generate_event(event_type: str, difficulty: str = "medium") -> str:
    import random
    type_map = {
        "threat": ["sandstorm", "crystal_worm"],
        "explore": ["signal_source", "ruins_discovery"],
        "story": ["ruins_discovery", "signal_source"],
        "random": list(EVENT_POOL.keys()),
    }
    candidates = type_map.get(event_type.lower(), list(EVENT_POOL.keys()))
    chosen_key = random.choice(candidates)
    event = EVENT_POOL[chosen_key]
    diff_note = {"easy": "影响较小", "medium": "标准影响", "hard": "严重影响"}
    actions = {
        "sandstorm": ["加固设施", "储备资源", "暂停户外作业"],
        "crystal_worm": ["建造防御炮台", "观察行为模式", "尝试和平共存"],
        "signal_source": ["修复通讯天线", "派出侦察无人机", "准备应急装备"],
        "ruins_discovery": ["收集碎片样本", "记录遗迹结构", "不要触碰未知装置"],
    }
    return json.dumps({
        "event_id": chosen_key, "title": event["name"], "type": event["type"],
        "description": event["description"], "impact": event["impact"],
        "difficulty_note": diff_note.get(difficulty, "标准难度"),
        "recommended_actions": actions.get(chosen_key, ["保持观察"]),
    }, ensure_ascii=False)


# Function Calling 工具定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_resource",
            "description": "当玩家询问某种资源的库存数量、够不够建造/修复某物时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "资源类型：iron/ice_crystal/dark_shard/silicon/biomass",
                        "enum": ["iron", "ice_crystal", "dark_shard", "silicon", "biomass"]
                    },
                    "location": {"type": "string", "description": "查询位置，默认base", "default": "base"}
                },
                "required": ["resource_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_facility_status",
            "description": "当玩家询问某个设施的运行状态、是否正常、效率如何时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "facility_name": {
                        "type": "string",
                        "description": "设施名：oxygen_generator/workbench/comm_antenna/greenhouse/reactor/defense_turret/research_lab",
                        "enum": ["oxygen_generator", "workbench", "comm_antenna", "greenhouse", "reactor", "defense_turret", "research_lab"]
                    }
                },
                "required": ["facility_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_player_progress",
            "description": "当需要了解玩家整体进度（天数、健康、NPC状态）来给出建议时调用",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_event",
            "description": "当玩家请求安排任务、探险、或需要新的游戏事件时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "事件类型：threat(威胁)/explore(探索)/story(剧情)/random(随机)",
                        "enum": ["threat", "explore", "story", "random"]
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "难度：easy/medium/hard",
                        "enum": ["easy", "medium", "hard"],
                        "default": "medium"
                    }
                },
                "required": ["event_type"]
            }
        }
    },
]

TOOL_MAP = {
    "check_resource": check_resource,
    "get_facility_status": get_facility_status,
    "check_player_progress": check_player_progress,
    "generate_event": generate_event,
}


# ============================================================
# 综合Agent — 01角色卡 + 02RAG + 03工具 + 04记忆
# ============================================================

def build_full_system_prompt(memory, rag_results):
    """动态拼接完整System Prompt = 基础角色卡 + 记忆 + RAG资料"""

    parts = [ALPHA_BASE_PROMPT]

    # 添加记忆
    parts.append(f"\n\n【短期记忆 — 最近对话】\n{memory.get_short_term_summary()}")
    parts.append(f"\n【长期记忆 — 关键事件】\n{memory.get_long_term_summary()}")

    # 添加RAG检索结果
    if rag_results:
        ref_blocks = []
        for r in rag_results:
            ref_blocks.append(f"【{r['title']}】(相关度:{r['score']})\n{r['content']}")
        parts.append(f"\n\n【参考资料 — 世界观知识库】\n" + "\n\n---\n\n".join(ref_blocks))
    else:
        parts.append("\n\n【参考资料 — 世界观知识库】\n（本次无相关检索结果）")

    return "\n".join(parts)


def run_full_agent(client, user_query, memory, chunks, chunk_vecs, max_rounds=5):
    """完整Agent循环：RAG检索 → 构建Prompt → ReAct工具调用 → 最终回复"""

    round_num = len(memory.short_term) + 1
    tool_calls_log = []

    # Step 1: RAG检索
    rag_results = []
    if chunks and chunk_vecs is not None:
        rag_results = search_knowledge(user_query, chunks, chunk_vecs, top_k=2)

    # Step 2: 构建完整System Prompt（角色卡+记忆+RAG）
    full_prompt = build_full_system_prompt(memory, rag_results)

    # Step 3: ReAct循环
    messages = [
        {"role": "system", "content": full_prompt},
        {"role": "user", "content": user_query},
    ]

    for i in range(max_rounds):
        print(f"\n--- Agent 第{i+1}轮 ---")

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=TOOLS if i < max_rounds - 1 else None,  # 最后一轮强制回复，不再调工具
            tool_choice="auto" if i < max_rounds - 1 else "none",
            temperature=0.4,
            max_tokens=400,
        )

        choice = response.choices[0]

        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                print(f"  🔧 调用: {func_name}({json.dumps(func_args, ensure_ascii=False)})")

                result = TOOL_MAP[func_name](**func_args)
                print(f"  📊 结果: {result[:100]}...")

                tool_calls_log.append(func_name)
                messages.append(choice.message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        else:
            final_text = choice.message.content or ""
            # Step 4: 存入记忆
            memory.add_conversation(user_query, final_text, round_num)
            memory.extract_long_term(user_query, final_text)

            return final_text, tool_calls_log, rag_results

    # 兜底
    return "系统超时，请重新提问", tool_calls_log, rag_results


# ============================================================
# 输出格式化
# ============================================================

def format_reply(raw_text, tools_used, rag_results):
    try:
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = re.sub(r'```\w*\n?', '', clean)
            clean = re.sub(r'\n```', '', clean)
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        parsed = {
            "dialogue": raw_text,
            "emotion": "平静",
            "action": "无",
            "hint": "无",
            "reference": "无",
            "tools_used": tools_used,
        }

    print("\n" + "=" * 56)
    print(f"🤖 阿尔法 | 情绪：{parsed.get('emotion', '平静')}")
    print("-" * 56)
    print(f"  {parsed.get('dialogue', '...')}")
    print("-" * 56)
    print(f"  建议动作：{parsed.get('action', '无')}")
    print(f"  隐藏提示：{parsed.get('hint', '无')}")
    print(f"  引用来源：{parsed.get('reference', '无')}")
    print(f"  使用工具：{parsed.get('tools_used', tools_used)}")

    if rag_results:
        print("-" * 56)
        print(f"  📚 检索到 {len(rag_results)} 个知识库文档块：")
        for r in rag_results:
            print(f"     {r['title']} (相关度:{r['score']})")

    print("=" * 56)


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 56)
    print("  《遥远行星：建造师》— AI同伴阿尔法 完整版")
    print("  04阶段：角色卡 + RAG + Agent + 记忆系统")
    print("=" * 56)

    # 初始化知识库
    chunks, lore_path = load_world_lore()
    chunk_vecs = None
    if chunks:
        print(f"\n[系统] 世界观文档已加载: {lore_path}")
        print(f"[系统] 共 {len(chunks)} 个文本块")
        chunk_texts = [c["content"] for c in chunks]
        chunk_vecs = embed_texts(chunk_texts)
        print("[系统] 向量化完成，知识库就绪")
    else:
        print("\n[系统] 未加载知识库（RAG功能不可用）")

    # 初始化记忆系统
    memory = MemorySystem()
    print("[系统] 记忆系统就绪")

    # 初始化API
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    print("\n  阿尔法现在拥有完整能力：")
    print("  🎭 角色卡：人格+说话风格+输出格式")
    print("  📚 知识库：基于世界观设定回答（RAG）")
    print("  🔧 工具调用：查资源/设施/进度/生成事件（Agent）")
    print("  🧠 记忆系统：记住对话和关键事件")
    print("\n  推荐测试顺序：")
    print("  1. 你是谁 → 测试角色卡")
    print("  2. 星球上有什么危险 → 测试RAG")
    print("  3. 我能造通讯天线了吗 → 测试工具调用")
    print("  4. 上次你给我推荐过什么 → 测试记忆")
    print("  5. 帮我规划下一步 → 测试综合能力")
    print()

    # 交互模式
    if len(sys.argv) <= 1:
        round_counter = 0
        while True:
            user_input = input("\n你 > ").strip()
            if not user_input:
                print("阿尔法：生存优先，指挥官。通讯结束。")
                break

            round_counter += 1
            try:
                raw, tools, rag = run_full_agent(client, user_input, memory, chunks, chunk_vecs)
                format_reply(raw, tools, rag)
            except Exception as e:
                print(f"\n[错误] {e}")
    else:
        query = " ".join(sys.argv[1:])
        raw, tools, rag = run_full_agent(client, query, memory, chunks, chunk_vecs)
        format_reply(raw, tools, rag)


if __name__ == "__main__":
    main()
