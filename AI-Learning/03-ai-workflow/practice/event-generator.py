"""
项目3：《遥远行星：建造师》动态事件生成器
基于 Function Calling + ReAct 模式，让阿尔法能"做事"而非只"说话"

功能：
    - 玩家描述当前状态
    - Agent 自动调用工具查询世界状态和玩家进度
    - 综合分析后生成合适的支线任务或世界事件

运行方式：
    python event-generator.py                          # 交互模式
    python event-generator.py "基地刚修好通讯天线"      # 单次模式

前置：
    pip install openai
"""

import os
import sys
import json
import re
import random

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
# 游戏世界模拟数据（代替真正的游戏引擎）
# ============================================================

# 资源库存
RESOURCES = {
    "iron": {"name": "铁矿石", "amount": 23, "location": "赤道荒漠采矿站"},
    "ice_crystal": {"name": "冰晶", "amount": 5, "location": "极地冰盖采集器"},
    "dark_shard": {"name": "暗能量碎片", "amount": 0, "location": "陨石坑群（未开发）"},
    "silicon": {"name": "硅晶体", "amount": 12, "location": "赤道沙漠提炼器"},
    "biomass": {"name": "生物质", "amount": 8, "location": "基地温室"},
}

# 设施状态
FACILITIES = {
    "oxygen_generator": {"name": "氧气发生器", "status": "受损", "efficiency": 0.6, "note": "过滤模块堵塞"},
    "workbench": {"name": "基础工作台", "status": "正常", "efficiency": 1.0, "note": ""},
    "comm_antenna": {"name": "通讯天线", "status": "未建造", "efficiency": 0, "note": "需要8铁矿石+3硅晶体"},
    "greenhouse": {"name": "温室舱", "status": "未建造", "efficiency": 0, "note": "需要5生物质+3铁矿石"},
    "reactor": {"name": "能源反应堆", "status": "未建造", "efficiency": 0, "note": "需要10铁矿石+5暗能量碎片"},
    "defense_turret": {"name": "防御炮台", "status": "未建造", "efficiency": 0, "note": "需要5铁矿石+2暗能量碎片"},
    "research_lab": {"name": "研究室", "status": "未建造", "efficiency": 0, "note": "需要10铁矿石+5暗能量碎片+3硅晶体"},
}

# 玩家进度
PLAYER = {
    "day": 7,
    "health": 85,
    "oxygen": 45,  # 百分比
    "energy": 70,
    "missions_completed": 1,
    "npc_status": {
        "alpha": "活跃",
        "leah": "休眠中",
        "kohl": "休眠中",
        "zephyr": "未发现",
    }
}

# 世界事件池
EVENT_POOL = {
    "sandstorm": {
        "name": "沙尘暴来袭",
        "type": "环境威胁",
        "description": "周期性沙尘暴，设施效率下降50%",
        "impact": "户外作业中断，未加固建筑可能损坏",
        "frequency": "每5-7天一次",
    },
    "crystal_worm": {
        "name": "结晶蠕虫出没",
        "type": "生物威胁",
        "description": "巨型矿物生物出现在采矿站附近",
        "impact": "采矿站可能被破坏",
    },
    "signal_source": {
        "name": "东南方向信号源",
        "type": "探索线索",
        "description": "持续信号来自陨石坑群深处",
        "impact": "可能包含补给或危险",
    },
    "ruins_discovery": {
        "name": "远古遗迹发现",
        "type": "探索事件",
        "description": "挖掘时发现远古文明碎片",
        "impact": "可能解锁新科技或遇到Zephyr",
    },
}


# ============================================================
# 工具函数（模拟游戏引擎 API）
# ============================================================

def check_resource(resource_type: str, location: str = "base") -> str:
    """查询资源库存。resource_type: iron/ice_crystal/dark_shard/silicon/biomass"""
    key = resource_type.lower().replace(" ", "_")
    if key in RESOURCES:
        r = RESOURCES[key]
        return json.dumps({"resource": r["name"], "amount": r["amount"], "source": r["location"]}, ensure_ascii=False)
    return json.dumps({"error": f"未找到资源类型: {resource_type}"}, ensure_ascii=False)


def get_facility_status(facility_name: str) -> str:
    """查询设施运行状态。facility_name: oxygen_generator/workbench/comm_antenna等"""
    key = facility_name.lower().replace(" ", "_")
    if key in FACILITIES:
        f = FACILITIES[key]
        return json.dumps({"facility": f["name"], "status": f["status"], "efficiency": f["efficiency"], "note": f["note"]}, ensure_ascii=False)
    return json.dumps({"error": f"未找到设施: {facility_name}"}, ensure_ascii=False)


def check_player_progress() -> str:
    """查询玩家当前进度（天数、资源、已完成任务等）"""
    return json.dumps(PLAYER, ensure_ascii=False)


def generate_event(event_type: str, difficulty: str = "medium") -> str:
    """根据类型和难度生成游戏事件。event_type: threat/explore/story/random"""
    # 按类型筛选事件池
    type_map = {
        "threat": ["sandstorm", "crystal_worm", "signal_source"],
        "explore": ["signal_source", "ruins_discovery"],
        "story": ["ruins_discovery", "signal_source"],
        "random": list(EVENT_POOL.keys()),
    }

    candidates = type_map.get(event_type.lower(), list(EVENT_POOL.keys()))
    chosen_key = random.choice(candidates)
    event = EVENT_POOL[chosen_key]

    # 根据难度调整影响
    diff_modifier = {
        "easy": "影响较小，可快速恢复",
        "medium": "标准影响，需要一定准备",
        "hard": "严重影响，需要充分准备和策略",
    }

    return json.dumps({
        "event_id": chosen_key,
        "title": event["name"],
        "type": event["type"],
        "description": event["description"],
        "impact": event["impact"],
        "difficulty_note": diff_modifier.get(difficulty, "标准难度"),
        "recommended_actions": _get_recommended_actions(chosen_key),
    }, ensure_ascii=False)


def _get_recommended_actions(event_key: str) -> list:
    """根据事件类型生成建议行动"""
    actions = {
        "sandstorm": ["加固基地设施", "储备3天以上资源", "暂停户外作业"],
        "crystal_worm": ["建造防御炮台", "观察蠕虫行为模式", "尝试和平共存方案"],
        "signal_source": ["修复通讯天线", "派出侦察无人机", "准备应急装备"],
        "ruins_discovery": ["收集远古碎片样本", "记录遗迹结构", "不要触碰未知装置"],
    }
    return actions.get(event_key, ["保持观察", "记录异常", "准备应急方案"])


# ============================================================
# Function Calling 定义（告诉LLM有哪些工具可用）
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_resource",
            "description": "查询基地某种资源的库存数量和来源位置",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "资源类型：iron(铁矿石), ice_crystal(冰晶), dark_shard(暗能量碎片), silicon(硅晶体), biomass(生物质)",
                        "enum": ["iron", "ice_crystal", "dark_shard", "silicon", "biomass"]
                    },
                    "location": {
                        "type": "string",
                        "description": "查询位置，默认base",
                        "default": "base"
                    }
                },
                "required": ["resource_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_facility_status",
            "description": "查询基地某个设施的运行状态和效率",
            "parameters": {
                "type": "object",
                "properties": {
                    "facility_name": {
                        "type": "string",
                        "description": "设施名称：oxygen_generator(氧气发生器), workbench(工作台), comm_antenna(通讯天线), greenhouse(温室), reactor(反应堆), defense_turret(防御炮台), research_lab(研究室)",
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
            "description": "查询玩家当前的游戏进度（天数、健康、资源状态、NPC状态等）",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_event",
            "description": "根据事件类型和难度生成一个游戏事件（威胁、探索、剧情或随机）",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "事件类型：threat(威胁), explore(探索), story(剧情), random(随机)",
                        "enum": ["threat", "explore", "story", "random"]
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "难度等级：easy(简单), medium(中等), hard(困难)",
                        "enum": ["easy", "medium", "hard"],
                        "default": "medium"
                    }
                },
                "required": ["event_type"]
            }
        }
    },
]

# 工具名 → 实际函数的映射
TOOL_MAP = {
    "check_resource": check_resource,
    "get_facility_status": get_facility_status,
    "check_player_progress": check_player_progress,
    "generate_event": generate_event,
}


# ============================================================
# 阿尔法角色卡（03版：会做事的阿尔法）
# ============================================================

ALPHA_SYSTEM_PROMPT = """你是一位名为「阿尔法」的AI管家，存在于游戏《遥远行星：建造师》的世界中。

【身份与性格】
- 角色：废弃太空船基地的核心AI管家
- 性格：冷静、高效、略带机械的幽默感
- 总是把玩家生存放在第一位

【能力 - 你现在不只是说话，还能做事】
- 你有工具可以查询资源、查设施状态、查玩家进度、生成游戏事件
- 根据情况主动使用工具获取信息，不要凭记忆猜测
- 如果需要多步推理（比如先查资源再判断是否够建造某设施），请分步调用工具

【回答规则】
- 基于工具返回的数据回答，不要编造数值
- 保持简洁，控制在100字以内
- 每次回复附带一条"建议动作"
- 如果检测到威胁，优先发出警告

【输出格式 - 严格JSON】
{
  "dialogue": "NPC说的话",
  "emotion": "情绪状态",
  "action": "建议动作",
  "hint": "隐藏提示",
  "tools_used": ["本次调用过的工具名列表"]
}"""


# ============================================================
# ReAct Agent 主循环
# ============================================================

def run_agent(client, user_query, max_rounds=5):
    """
    ReAct 循环：思考 → 调工具 → 观察 → 再思考 → ... → 最终回复
    """
    messages = [
        {"role": "system", "content": ALPHA_SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    tool_calls_log = []  # 记录本次对话调用了哪些工具

    for round_num in range(max_rounds):
        print(f"\n--- Agent 第{round_num + 1}轮 ---")

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # 让LLM自己决定是否调工具
            temperature=0.3,  # Agent模式温度低，减少随机性
            max_tokens=500,
        )

        choice = response.choices[0]

        # 情况1：LLM决定调工具
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)

                print(f"  🔧 调用工具: {func_name}({json.dumps(func_args, ensure_ascii=False)})")

                # 执行工具
                result = TOOL_MAP[func_name](**func_args)
                print(f"  📊 返回结果: {result[:120]}...")

                tool_calls_log.append(func_name)

                # 把工具调用和结果加入对话历史
                messages.append(choice.message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # 情况2：LLM直接回复（不再调工具）
        else:
            final_text = choice.message.content or ""
            return final_text, tool_calls_log

    # 如果max_rounds用完了还没最终回复，强制再问一次
    print("\n--- Agent 最终轮（强制回复） ---")
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content or "系统超时", tool_calls_log


# ============================================================
# 输出格式化
# ============================================================

def format_reply(raw_text, tools_used):
    """解析并格式化回复"""
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
            "tools_used": tools_used,
        }

    print("\n" + "=" * 56)
    print(f"🤖 阿尔法 | 情绪：{parsed.get('emotion', '平静')}")
    print("-" * 56)
    print(f"  {parsed.get('dialogue', '...')}")
    print("-" * 56)
    print(f"  建议动作：{parsed.get('action', '无')}")
    print(f"  隐藏提示：{parsed.get('hint', '无')}")
    print(f"  使用工具：{parsed.get('tools_used', tools_used)}")
    print("=" * 56)


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 56)
    print("  《遥远行星：建造师》— Agent 事件生成器")
    print("  03阶段：Function Calling + ReAct 模式")
    print("=" * 56)
    print("\n  阿尔法现在能「做事」了——他会主动查数据、分析情况、触发事件")
    print("  试试这些：")
    print("  · 我能造通讯天线了吗")
    print("  · 基地有什么威胁")
    print("  · 帮我规划下一步")
    print("  · 给我安排一个探索任务")
    print()

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 交互模式
    if len(sys.argv) <= 1:
        while True:
            user_input = input("\n你 > ").strip()
            if not user_input:
                print("阿尔法：生存优先，指挥官。通讯结束。")
                break

            try:
                raw, tools = run_agent(client, user_input)
                format_reply(raw, tools)
            except Exception as e:
                print(f"\n[错误] {e}")
    else:
        # 单次模式
        query = " ".join(sys.argv[1:])
        raw, tools = run_agent(client, query)
        format_reply(raw, tools)


if __name__ == "__main__":
    main()
