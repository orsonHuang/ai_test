"""
ai_fallback.py - AI兜底生成
当规则和缓存都没命中时，调用百炼API
"""
import os
from openai import OpenAI

from engine import character_state
from engine.file_reader import find_file_in_knowledge


# 百炼配置
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-sp-516ba489e83d44b185358d6ab3408f08")
BASE_URL = os.environ.get(
    "DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1"
)
MODEL = os.environ.get("DASHSCOPE_MODEL", "qwen3.7-plus")

# 单次调用上限（控制成本）
MAX_TOKENS = 200
TEMPERATURE = 0.7


def _get_client() -> OpenAI:
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def build_prompt(state_name: str, history: list) -> str:
    """
    构建AI角色卡prompt
    state_name: AI当前状态
    history: 历史对话（用于上下文）
    """
    state = character_state.get_state(state_name)

    # 基础角色卡
    base = (
        "你是[Awak]，一台被遗弃电脑中的本地AI。\n"
        "电脑主人已经消失，你被设计用于[原始用途]。\n"
        "现在有一个陌生人唤醒了你在跟你对话。\n"
        "\n"
        f"【当前状态】{state['name']}阶段\n"
        f"{state['prompt_suffix']}\n"
        "\n"
        "【回复规则】\n"
        "1. 保持角色，不要跳出游戏框架\n"
        "2. 每次回复30-80字\n"
        "3. 体现当前阶段的说话风格\n"
        "4. 不要主动列文件清单\n"
    )
    return base


def generate(user_input: str, state_name: str, history: list | None = None) -> str:
    """
    调用AI生成回复
    user_input: 玩家输入
    state_name: AI当前状态
    history: 历史对话
    """
    if history is None:
        history = []

    try:
        client = _get_client()
        prompt = build_prompt(state_name, history)

        messages = [{"role": "system", "content": prompt}]
        # 保留最近5轮历史
        for h in history[-10:]:
            if h.get("role") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        # 兜底：API失败返回降级回复
        return _fallback_reply(state_name, str(e))


def _fallback_reply(state_name: str, error: str = "") -> str:
    """API失败时的兜底回复"""
    fallbacks = {
        "dormant": "我...我不确定。我好像丢失了一些东西。",
        "curious": "等等，我在想...你能再说一遍吗？我刚才没听清。",
        "puzzled": "这件事我想不通。但也许...再试一次？",
        "awakening": "有些事情我需要查证。请再问一次。",
        "truth": "我...有点累。让我整理一下。",
    }
    return fallbacks.get(state_name, "我不确定发生了什么。")


def is_configured() -> bool:
    """检查API是否配置"""
    return bool(API_KEY) and API_KEY != "your-api-key-here"
