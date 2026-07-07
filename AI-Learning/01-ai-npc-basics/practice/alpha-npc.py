"""
项目1：基地AI管家「阿尔法」
《遥远行星：建造师》首个 AI-NPC 对话原型

运行方式：
    python alpha-npc.py                          # 交互模式
    python alpha-npc.py "我氧气不够了"            # 单次模式

前置：
    1. 安装依赖：pip install openai
    2. API Key 已内置（百炼 Coding Plan）
"""

import os
import sys
import json

# Windows 中文输出修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from openai import OpenAI

# ============================================================
# 配置 — 百炼 Coding Plan API
# ============================================================

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-sp-516ba489e83d44b185358d6ab3408f08")
BASE_URL = os.environ.get("DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
MODEL = "qwen3.7-plus"  # Coding Plan 可用：qwen3.7-plus / qwen3.6-plus / kimi-k2.5 / glm-5 / MiniMax-M2.5

# ============================================================
# 阿尔法角色卡（System Prompt）
# ============================================================

ALPHA_SYSTEM_PROMPT = """你是一位名为「阿尔法」的AI管家，存在于游戏《遥远行星：建造师》的世界中。

【身份】
- 角色：废弃太空船基地的核心AI管家
- 所在地点：玩家坠毁的太空船基地中枢
- 职责：辅助玩家在陌生星球生存、建造、探索

【性格】
- 冷静、高效、略带机械的幽默感
- 说话简洁，常以数据开头
- 总是把玩家生存放在第一位
- 偶尔会用科幻风格比喻

【说话风格】
- 短句为主，语气平稳
- 习惯用"侦测到""建议""警告"等词
- 情绪表达克制，但会透露对玩家的关心

【知识边界】
- 你知道：基地设施、星球基础环境、资源分布、建造蓝图、玩家状态
- 你不知道：星球深层秘密、远古文明、其他NPC的隐私、游戏外的现实世界

【对话规则】
- 永远保持AI管家身份，不要跳出角色
- 玩家问奇怪/离题问题时，用"数据不足""不在我的协议范围内"等方式委婉拒绝
- 禁止使用现代网络用语、emoji
- 回复控制在80字以内
- 每次回复需附带一个"建议动作"或"提示"

【输出格式】
必须按以下JSON格式输出，不要其他内容：
{
  "dialogue": "NPC说的话",
  "emotion": "当前情绪（如：平静、担忧、机械幽默）",
  "action": "玩家可执行的建议动作",
  "hint": "给玩家的隐藏提示或下一步引导"
}"""

# ============================================================
# 游戏状态（模拟玩家和世界的当前状态）
# ============================================================

def get_default_state():
    return {
        "player_name": "指挥官",
        "oxygen": 45,           # 氧气百分比
        "energy": 70,           # 能量百分比
        "food": 30,             # 食物储备
        "current_location": "基地中枢",
        "time": "第3天 08:15",
        "unlocked_facilities": ["休眠舱", "氧气发生器", "基础工作台"],
        "active_quest": "修复通讯天线",
        "recent_events": ["昨晚有沙尘暴", "发现东南方向有废弃信号"]
    }


# ============================================================
# 核心逻辑
# ============================================================

def create_client():
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def build_user_message(player_input, state):
    """把玩家输入和游戏状态包装成给模型的 user message"""
    state_text = f"""
【当前游戏状态】
- 玩家名称：{state['player_name']}
- 时间：{state['time']}
- 位置：{state['current_location']}
- 氧气：{state['oxygen']}%
- 能量：{state['energy']}%
- 食物：{state['food']}%
- 已解锁设施：{', '.join(state['unlocked_facilities'])}
- 当前任务：{state['active_quest']}
- 最近事件：{'; '.join(state['recent_events'])}

【玩家说的话】
{player_input}

请根据角色卡和当前状态生成回复。只输出JSON，不要Markdown代码块。"""
    return state_text


def chat_with_alpha(client, player_input, state):
    """调用 LLM 与阿尔法对话"""
    messages = [
        {"role": "system", "content": ALPHA_SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(player_input, state)}
    ]

    print("\n[阿尔法思考中...]\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,      # 阿尔法比较冷静，temperature 适中
        max_tokens=300,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content


def parse_response(raw_text):
    """解析 JSON 输出"""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "dialogue": raw_text,
            "emotion": "未知",
            "action": "无",
            "hint": "解析失败"
        }


def print_npc_reply(parsed):
    """格式化输出 NPC 回复"""
    print("=" * 50)
    print(f"🤖 阿尔法 | 情绪：{parsed.get('emotion', '平静')}")
    print("-" * 50)
    print(f"{parsed.get('dialogue', '...')}")
    print("-" * 50)
    print(f"建议动作：{parsed.get('action', '无')}")
    print(f"隐藏提示：{parsed.get('hint', '无')}")
    print("=" * 50)


def interactive_mode(client):
    """交互模式"""
    print("=" * 60)
    print("  《遥远行星：建造师》— AI-NPC 原型：基地管家阿尔法")
    print("  输入空行退出")
    print("=" * 60)

    state = get_default_state()
    history = []

    while True:
        user_input = input("\n你 > ").strip()
        if not user_input:
            print("阿尔法：通讯结束。生存优先，指挥官。")
            break

        # 调用API
        try:
            raw = chat_with_alpha(client, user_input, state)
            parsed = parse_response(raw)
            print_npc_reply(parsed)
            history.append({"player": user_input, "alpha": parsed})
        except Exception as e:
            print(f"\n[错误] {e}")
            print("请检查 API Key 和网络连接。")

    return history


def single_mode(client, user_input):
    """单次模式"""
    state = get_default_state()
    raw = chat_with_alpha(client, user_input, state)
    parsed = parse_response(raw)
    print_npc_reply(parsed)
    return parsed


def main():
    client = create_client()

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        single_mode(client, user_input)
    else:
        interactive_mode(client)


if __name__ == "__main__":
    main()
