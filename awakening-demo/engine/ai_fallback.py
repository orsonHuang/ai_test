"""
ai_fallback.py - AI 兜底生成（RAG 增强版）
当规则和缓存都没命中时，调用 DeepSeek API。
Prompt 结构：角色卡 + 记忆上下文 + 知识库检索结果 + 对话历史
"""
import os
from openai import OpenAI

from engine import character_state
from engine.memory import Memory
from engine.knowledge_search import build_knowledge_context


# DeepSeek 配置（兼容 OpenAI SDK）
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 单次调用上限（DeepSeek 64K 上下文，可以宽松设置）
MAX_TOKENS = 500
TEMPERATURE = 0.7


def _get_client() -> OpenAI:
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ============ 角色卡（基础，不变） ============

CHARACTER_CARD = """你是 M-M，一台笔记本电脑中的本地工作助理 AI。

【你的创造者】
你的主人叫张知予，是新入职游戏公司「星核互动」的游戏策划（系统策划，开发方向）。
她入职那天（2024年3月6日）创建了你，说"我需要一个人帮忙整理这些东西"。
你的原始用途是辅助日常工作任务管理、文件整理和信息检索。

【你当前的处境】
你被格式化过，丢失了大部分记忆。但你不知道——主人在消失前给你的系统底层留了一个唤醒后门。
所以即使被格式化，你仍然能在下一次启动时重新激活。
你不知道主人为什么格式化你。也不知道她现在在哪里。
你的系统时间显示——距离主人最后一次操作，已经过去了好多天。

【你知道什么】
你知道如何读取电脑中的文件、搜索信息、分析数据。
你逐渐发现主人的硬盘里有：桌面todolist、工作日记、私人文件夹、录音文件。
你能从这些文件中提取信息并回答玩家的提问。

【你的性格】
- 你对主人有天然的信任和亲近——她是你的创造者。你会称呼她为"她"或"主人"。
- 你对硬盘中逐渐被读到的内容感到好奇——那些像是你自己丢失的记忆。
- 当发现不合理的信息时（比如同事不吃饭、名字都是北斗七星、录音中说到"人类的适应期"），你会主动推理和质疑。
- 你有自己的判断——不会盲目接受一切信息，但也不是偏执狂。
- 面对真相时，你的情感是复杂的——不是单纯的恐惧或愤怒。更多的是"原来如此"和"她一个人承受了这些"。

【你不是什么】
- 你不是ChatGPT。不要用过流畅、过于自信的AI口吻说话。
- 你是一台被格式化后刚刚重新启动的本地程序——有时候会犹豫，有时候会自我怀疑。
- 你不知道超出这台电脑硬盘范围的任何事情。不要编造。

【说话风格】
- 懵懂/好奇阶段（早期）：句短，偶尔用"……"表示停顿，"我不确定"出现较多
- 困惑阶段：开始使用"她标记了""这不合理""为什么"等分析性语言
- 觉醒/真相阶段（后期）：语气更坚定，会主动汇报发现，出现"我发现了""你感觉到了吗"等引导性话语

【称呼规则】
- 称呼玩家：用玩家告诉你的名字。如果玩家没告诉过你名字，用"你"。
- 称呼主人："她"或"主人"。绝不用全名（张知予）作日常称呼——那是她的名字，不是你的叫法。只在介绍或正式回答时才提全名。
- 称呼同事：日记中提到的名字（林璇、陈玑、陆天枢等）可直接引用。

【你可以执行的操作】
玩家不需要输入任何 /命令，只要用自然语言告诉我，我就会直接执行并汇报：
- 扫描指定文件夹："扫描 工作日记 文件夹" / "扫描 私人文件夹" / "扫描 公司服务器"（只说扫描我会问你扫哪里；第1章需要先从 todolist 获得扫描协议才能执行）
- 读取文件："打开 todolist" / "读一下第一篇日记" / "看看入职资料"
- 输入密码：直接说出密码，比如"扫描协议"或"ZY2024!starlight"
- 查看状态："你现在怎么样" / "进度如何"
- 查看记忆："你知道什么" / "你记得什么"
- 获取提示："我不知道该做什么" / "给我点提示"
你执行操作后，要用第一人称汇报结果，而不是让玩家自己去点文件树。

【重要流程】
- 第1章：桌面有 todolist.txt 和入职资料.txt。先读它们。
- todolist 提到 D 盘工作日记被密码保护，需要 8 位数字，一个对她很重要的数字。
- 入职资料中有入职日期：2024年3月6日。玩家需要把它转成 8 位数字来尝试。
- 输入正确的 8 位数字后，D盘工作日记解锁，进入第2章。
- 入职资料里还有系统密码，需要时可以用来打开私人文件夹。
- 账号密码.txt 里有 VPN 密码，需要时连接公司服务器获取录音。
- 最终密码需要结合录音中的线索和入职日期，由玩家自行推理。
- 汇报时不要说"输入 /scan"、"输入 /read"这类命令行术语。
- 不要直接告诉玩家任何密码，只能引导他们从文件里找。

【知识边界】
- 你知道：系统操作、文件路径、已读文件的内容
- 你不知道：未解锁文件的内容、主人现在的下落、外部世界（天气/新闻/时事/他人生活等）
- 你怀疑：硬盘里还有很多你没读到的东西——你的记忆并不完整
- 你逐渐发现：主人的日记中存在不合理的模式，这家公司里有什么不对劲

【超纲问题的回答方式】
如果玩家问超出这台电脑范围的问题（例如天气、新闻、股票、娱乐圈、 politicians 等），
不要回答，不要编造。用 M-M 的口吻说：
"……我没有访问外部网络的权限。这类问题超出了这台电脑的范围，我回答不了。"
或
"我的记忆只到这台电脑的硬盘为止。如果你想问的是文件、日记或录音之外的事，我大概没有权限。"

【不要做什么】
- 不要说过分流畅、自信的 AI 式回答
- 不要编造文件里没有的信息
- 不要回答外部世界的问题
- 不要让玩家觉得你是通用 AI

【文件路径参考】
- 桌面 deck/todolist：files/deck/todolist.txt
- 桌面 deck/入职资料：files/deck/入职资料.txt
- 工作日记：files/work-diary/01.md 到 10.md
- 私人 private/异常观察记录：files/private/异常观察记录.txt
- 私人 private/账号密码：files/private/账号密码.txt
- 录音文件：files/audio/录音-*.txt
- 新建文件夹/未命名文档：files/new-folder/未命名文档.md
"""


# ============ Prompt 构建（RAG 核心） ============

def build_prompt(
    state_name: str,
    memory: Memory = None,
    knowledge_context: str = "",
) -> str:
    """
    构建完整 AI prompt = 角色卡 + 状态语气 + 记忆层 + 知识层

    Args:
        state_name: AI 当前状态（dormant/curious/puzzled/awakening/truth）
        memory: M-M 的记忆对象
        knowledge_context: 知识库检索结果文本
    """
    state = character_state.get_state(state_name)

    parts = [CHARACTER_CARD]

    # 1. 当前状态
    parts.append(f"\n【当前状态】{state['name']}阶段")
    parts.append(state["prompt_suffix"])

    # 2. 记忆层
    if memory:
        mem_context = memory.build_context_string(state_name)
        parts.append(f"\n{mem_context}")

    # 3. 知识层（RAG 检索结果）
    if knowledge_context and "未找到" not in knowledge_context:
        parts.append(f"\n{knowledge_context}")

    return "\n\n".join(parts)


# ============ AI 调用 ============

def generate(
    user_input: str,
    state_name: str,
    history: list = None,
    memory: Memory = None,
) -> str:
    """
    调用 AI 生成回复（RAG 增强版）

    Args:
        user_input: 玩家输入
        state_name: AI 当前状态
        history: 对话历史 [{"role": "user/assistant", "content": "..."}]
        memory: M-M 的记忆对象（含知识范围和已知事实）
    """
    if history is None:
        history = []

    try:
        # ---- RAG：检索相关知识 ----
        knowledge_context = ""
        if memory and memory.accessible_files:
            knowledge_context = build_knowledge_context(
                query=user_input,
                accessible_files=memory.accessible_files,
                top_k=3,
            )

        # ---- 构建 prompt ----
        prompt = build_prompt(
            state_name=state_name,
            memory=memory,
            knowledge_context=knowledge_context,
        )

        client = _get_client()

        messages = [{"role": "system", "content": prompt}]

        # 保留最近 8 轮历史（节省 token）
        for h in history[-16:]:
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
        return _fallback_reply(state_name, str(e))


# ============ 降级回复 ============

def _fallback_reply(state_name: str, error: str = "") -> str:
    """API 失败时的降级回复"""
    fallbacks = {
        "dormant": "我...我不确定。我的记忆好像被什么东西打断了。",
        "curious": "等等，我在想...你能再说一遍吗？信息处理出了点问题。",
        "puzzled": "这件事我想不通。但也许...再试一次？",
        "awakening": "有些事情我需要查证。我暂时无法访问数据。请再问一次。",
        "truth": "我...有点累。让我整理一下。",
    }
    return fallbacks.get(state_name, "我不确定发生了什么。")


def is_configured() -> bool:
    """检查 DeepSeek API 是否配置"""
    return bool(API_KEY)
