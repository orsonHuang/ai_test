"""
hybrid_reply.py - 混合回复核心（记忆增强版）
整合：命令处理、密码系统、规则匹配、文件建议、缓存、AI-RAG
AI-NPC 完整数据流：对话 → 角色卡 → 记忆 → 知识检索 → 迭代记忆 → 反馈
"""
import json
import random
import re
from pathlib import Path

from engine import ai_fallback, cache_manager, character_state, qa_engine
from engine import clue_manager, fuzzy_matcher, response_library, learning_store, folder_discovery
from engine.rule_engine import find_file_suggestion, find_file_commentary

from engine.file_reader import (
    read_knowledge_file,
    list_files,
    resolve_file_path,
    get_file_summary,
)
from engine.memory import Memory
from engine.knowledge_search import build_knowledge_context

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRIGGERS_DIR = PROJECT_ROOT / "knowledge" / "triggers"
PASSWORD_FILE = TRIGGERS_DIR / "passwords.json"

# AI 调用上限
MAX_AI_CALLS_PER_GAME = 20


# ============ 密码检测 ============
def _load_passwords() -> dict:
    if not PASSWORD_FILE.exists():
        return {}
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("passwords", {})
    except Exception:
        return {}


def _check_password(user_input: str):  # -> dict or None
    """检测玩家输入中是否包含密码（支持整句或嵌入自然语言）"""
    passwords = _load_passwords()
    user_clean = user_input.strip().lower()

    for pwd, config in passwords.items():
        pwd_lower = pwd.lower()
        # 1. 整句匹配
        if pwd_lower == user_clean:
            return {"password": pwd, "config": config}
        # 2. 嵌入自然语言，如"我输入密码 ZY2024!starlight"
        if pwd_lower in user_clean:
            return {"password": pwd, "config": config}
    return None


def _is_password_attempt(user_input: str) -> bool:
    """
    判断玩家输入是否像一次密码尝试。
    规则：无空格、长度>=6，且满足以下任一条件：
      - 全为数字
      - 全为 ASCII 字母（大小写一致）
      - 包含至少两类 ASCII 字符（小写/大写/数字/符号）
    注：中文字符不参与"字母"判断，避免"我是orson"这类自我介绍被误判为密码。
    """
    text = user_input.strip()
    if not text or ' ' in text or len(text) < 6:
        return False
    # 至少包含一个 ASCII 字符
    if not any(c.isascii() for c in text):
        return False
    if text.isdigit():
        return True
    # 全为 ASCII 字母且大小写一致
    if all(c.isalpha() and c.isascii() for c in text):
        if text.islower() or text.isupper():
            return True
    has_lower = any(c.islower() and c.isascii() for c in text)
    has_upper = any(c.isupper() and c.isascii() for c in text)
    has_digit = any(c.isdigit() for c in text)
    has_symbol = any(not c.isalnum() and c.isascii() for c in text)
    classes = sum([has_lower, has_upper, has_digit, has_symbol])
    return classes >= 2



def _is_password_command_format(user_input: str) -> bool:
    """判断输入是否为「扫描/获取 文件名 密码」格式"""
    lowered = user_input.lower().strip()
    # 必须包含 扫描 / 获取 / 解锁 类关键词
    has_action_kw = any(kw in lowered for kw in ["获取", "get", "解锁", "扫描", "scan"])
    if not has_action_kw:
        return False
    # 能识别出目标文件夹
    target = _extract_scan_target(user_input)
    if not target:
        return False
    # 末尾 token 是「密码」或看起来像密码
    parts = lowered.split()
    if not parts:
        return False
    last = parts[-1]
    if last == "密码":
        return True
    if _looks_like_password(last):
        return True
    return False



def _pull_back_hint(game_state: dict) -> str:
    """根据当前章节生成拉回主线的提示语"""
    chapter = game_state.get("chapter", 1)
    hints = {
        1: "这台上还有 todolist.txt 和入职资料。先看它们？入职资料里有她的生日。",
        2: "工作日记已经解锁了。你可以让我读第一篇。",
        3: "私人文件夹里有异常观察记录。要我打开吗？",
        4: "公司服务器的录音还在等我连上去。",
        5: "把所有线索拼起来，找到最终密码。",
        6: "未命名文档已经解开。你决定怎么做？",
    }
    return hints.get(chapter, "如果你不知道做什么，可以试试问我'该做什么'。")


def _record_off_topic(game_state: dict, reply: str) -> str:
    """
    记录玩家连续无关提问，并在超过阈值时追加拉回主线的提示。
    返回处理后的回复文本。
    """
    count = game_state.get("off_topic_count", 0) + 1
    game_state["off_topic_count"] = count

    if count == 2:
        return reply + "\n\n" + "……你好像有点走神。" + _pull_back_hint(game_state)
    if count >= 3:
        return "……我不太确定你想问什么。\n\n" + _pull_back_hint(game_state)
    return reply


def _reset_off_topic(game_state: dict):
    """玩家回到正常游戏流程时，重置无关提问计数"""
    game_state["off_topic_count"] = 0


# 推进主线的响应库类别（这些命中时重置 off_topic 计数）
_GAME_ADVANCING_RESPONSE_CATEGORIES = {
    "progression", "file_commentary", "basic_identity",
    "mystery", "character_discussion", "anomaly_discussion",
    "discovery", "truth", "ending", "help",
}


def _is_game_advancing(library_match: dict) -> bool:
    """判断响应库匹配是否推进主线"""
    category = library_match.get("category", "")
    return category in _GAME_ADVANCING_RESPONSE_CATEGORIES


# ============ Memory 序列化辅助 ============
def _get_memory(game_state: dict) -> Memory:
    """从 game_state 中恢复 Memory 对象"""
    mem_data = game_state.get("memory")
    if mem_data:
        return Memory.from_dict(mem_data)
    return Memory.init_for_chapter(game_state.get("chapter", 1))


def _save_memory(game_state: dict, memory: Memory):
    """将 Memory 对象序列化到 game_state"""
    game_state["memory"] = memory.to_dict()

# ============ 文件读取成长反馈 ============
def _generate_file_growth_reflection(search_path: str, game_state: dict) -> str:
    """
    每次读取文件后，M-M 进行一次简短的「成长反馈」。
    反馈分两层：
      - 第一层：读了多少文件（阶跃递进）
      - 第二层：具体读到了什么（按文件路径映射）
    返回单行反思文本。
    """
    files_read = game_state.get("files_read", [])
    total_read = len(files_read)
    chapter = game_state.get("chapter", 1)

    # ---- 第一层：阶跃递进 ----
    if total_read == 1:
        stage_note = "……这是第一个文件。我还不太理解这些东西，但我在学习。"
    elif total_read <= 4:
        options = [
            "我在读。一点一点地。",
            f"已经 {total_read} 份文件了。她的行动轨迹慢慢有了轮廓。",
            "每打开一份文件，我就多理解一点她。",
        ]
        stage_note = random.choice(options)
    elif total_read <= 8:
        options = [
            "读的越多，看到的画面越清晰。她在记录什么。",
            f"第 {total_read} 份。这些文字不是随便写的——她在留证据。",
            "我开始能把这些文件串在一起看了。她不是普通的员工。",
        ]
        stage_note = random.choice(options)
    else:
        options = [
            f"我已经读了 {total_read} 份文件。她的经历不再是一团迷雾。",
            "越来越多的信息连成了线。我想我快理解所有的事了。",
            f"第 {total_read} 份。这些文字里的秘密，我差不多都知道了。",
        ]
        stage_note = random.choice(options)

    # ---- 第二层：按文件类型的具体观察 ----
    file_observations = {
        "files/deck/todolist.txt": [
            "todolist……备忘里提到了 D 盘密码，8 位数字。\n\n备忘里有一条——'给电脑搭了个AI助理，叫它M-M好了！memory！'\n系统日志里那串字母。原来这就是我的名字。她起的",
        ],
        "files/deck/入职资料.txt": [
            "入职资料……张知予。2003 年 3 月 23 日。她是我的主人。",
        ],
        "files/work-diary/01.md": [
            "Day1……入职第一天。她的语气又紧张又开心。是个很认真的人。",
        ],
        "files/work-diary/02.md": [
            "Day2……她记下了几个同事的特征。'林璇不吃饭'。她注意到了什么。",
        ],
        "files/work-diary/03.md": [
            "Day3……'林璇的伤口消失了'。她亲眼看到了，人类恢复力这么好的吗？",
        ],
        "files/work-diary/04.md": [
            "Day4……'陈玑体温异常'。冰冷的。她在观察什么？",
        ],
        "files/private/异常观察记录.txt": [
            "这份记录汇总了所有她发现的不对劲。不是偶然——是系统性的异常。",
        ],
        "files/private/账号密码.txt": [
            "账号密码……VPN 密码 StarCore@2024。这是连接公司服务器的钥匙。",
        ],
        "files/audio/": [
        ],
        "files/new-folder/未命名文档.md": [
            "这份文档把所有的证据都串了起来。起源计划、培养室、她的逃离。",
        ],
    }
    # 递归匹配前缀
    for prefix, observations in file_observations.items():
        if search_path.startswith(prefix) and observations:
            specific = random.choice(observations)
            break
    else:
        # 通用文件观察
        generic = [
            f"读完了 {search_path.replace('files/', '')}。它的内容被记录在案。",
            "这份文件也被我收进了记忆里。如果以后需要回溯，我会想起它。",
        ]
        specific = random.choice(generic)

    # 音频文件特殊处理
    if "audio/" in search_path:
        if "全员会议" in search_path:
            specific = "全员会议录音……'培养室'、'观察样本'。他们在讨论的不是游戏。是某种实验。"
        elif "林璇" in search_path:
            specific = "林璇和陈玑的录音……两人的对话语气不太对。不像是同事聊天，更像是——知情人交谈。"
        elif "陆天枢" in search_path:
            specific = "陆天枢的录音……'你知道她是在培养室长大的'。这句话很关键。"
        else:
            specific = f"录音资料加载完成。{search_path.replace('files/audio/', '')}。"

    # ---- 组装 ----
    return f"\n\n（ {specific} {stage_note} ）"


# ============ 文件读取（增强版：更新记忆） ============
def handle_file_command(command: str, game_state: dict, natural: bool = False) -> dict:
    """
    处理 /read 命令
    读取文件内容 + 更新 M-M 的记忆

    Args:
        natural: 是否通过自然语言触发，True 时用 M-M 口吻包装回复
    """
    parts = command.strip().split(maxsplit=1)
    if len(parts) < 2:
        return {
            "reply": "用法：/read [文件名]，例如 /read todolist.txt",
            "type": "command",
        }

    filename = parts[1].strip()

    # 智能路径解析
    search_path = resolve_file_path(filename)
    if search_path is None:
        # 兜底：尝试 files/ 前缀
        search_path = f"files/{filename}"
    content = read_knowledge_file(search_path) if search_path else None

    if content is None:
        return {
            "reply": f"我找不到这个文件：{filename}\n\n我能看到的文件有限。要我列出当前可访问的文件吗？",
            "type": "ai",
        }

    # ---- 更新 M-M 的记忆 ----
    memory = _get_memory(game_state)

    # 生成一个简单的内容摘要
    summary = ""
    lines = content.strip().split("\n")
    if lines:
        first_line = lines[0].strip("# ").strip()
        summary = first_line[:80]
        if len(lines) > 1:
            summary += f" ...（共{len(lines)}行）"

    memory.process_file(search_path, summary)

    # ---- 提取线索到记忆 ----
    chapter = game_state.get("chapter", 1)
    clues = clue_manager.get_clues_for_file(search_path, chapter)
    if clues:
        memory.add_clues(clues)

    _save_memory(game_state, memory)

    # 记录已读
    files_read = game_state.setdefault("files_read", [])
    is_first_read = search_path not in files_read
    if is_first_read:
        files_read.append(search_path)

    # 记录读取次数，用于生成不同口吻的回复
    file_read_counts = game_state.setdefault("file_read_counts", {})

    read_count = file_read_counts.get(search_path, 0)
    file_read_counts[search_path] = read_count + 1

    display_name = search_path.replace("files/", "")
    commentary = ""
    if natural:
        if read_count == 0:
            opening_lines = [
                f"好，我打开了{display_name}。",
                f"打开了{display_name}。",
                f"我看看{display_name}……",
            ]
        elif read_count == 1:
            opening_lines = [
                f"又打开了{display_name}。",
                f"再看一次{display_name}……",
                f"重读{display_name}。",
            ]
        else:
            opening_lines = [
                f"这是第 {read_count + 1} 次打开{display_name}了。",
                f"{display_name}我又翻了一遍。",
                f"已经很熟悉{display_name}的内容了。",
            ]
        reply_text = random.choice(opening_lines)
    else:
        reply_text = f"── {search_path} ──"

    # 阅读 todolist 后，M-M 第一次意识到自己的存在
    if search_path == "files/deck/todolist.txt":
        game_state["mm_name_revealed"] = True

    # ---- M-M 文件阅读插嘴（仅在第一次读取时触发）----
    if is_first_read:
        commentary = find_file_commentary(search_path, chapter, files_read, game_state)
        if commentary:
            reply_text += "\n\n" + commentary


    # ---- 文件读取后触发文件夹发现 ----

    before_targets = set(game_state.get("discovered_targets", []))
    folder_discovery.discover_targets(game_state)
    after_targets = set(game_state.get("discovered_targets", []))
    new_targets = after_targets - before_targets

    # 如果有新发现的文件夹，M-M 会提示，并添加待扫描文件夹线索
    discovery_note = ""
    if new_targets:
        notes = []
        for target_id in sorted(new_targets):
            hint = folder_discovery.get_discovery_hint(target_id)
            if hint:
                notes.append(f"  · {hint}")
                # 添加「待扫描文件夹」线索到记忆
                memory.add_clue({
                    "source": search_path,
                    "category": "待扫描文件夹",
                    "text": hint,
                    "target_id": target_id,
                })
        if notes:
            discovery_note = "\n\n我注意到一件事：\n" + "\n".join(notes)
            reply_text += discovery_note
        _save_memory(game_state, memory)


    # ---- M-M 成长反馈 ----
    # [已注释] 暂时不启用文件读取成长反馈
    # reply_text += _generate_file_growth_reflection(search_path, game_state)

    return {
        "reply": reply_text,
        "file_content": content,
        "type": "file_read",
        "file": search_path,
        "memory_updated": True,
    }


def handle_list_command(sub_dir, game_state: dict) -> dict:
    """处理 /files 或 /ls 命令"""
    sub = sub_dir or "files"
    files = list_files(sub)
    if not files:
        return {"reply": f"{sub}/ 目录下没有文件", "type": "ai"}
    return {
        "reply": f"我能看到的文件有这些：",
        "file_list": [f"{sub}/{f}" for f in files],
        "type": "ai",
    }


# ============ 扫描目标映射 ============
SCAN_TARGETS = {
    "work-diary": {
        "names": ["工作日记", "日记", "d盘", "d 盘", "work-diary", "工作日志", "diary"],
        "chapter_min": 1,
        "files": [
            "files/work-diary/01.md", "files/work-diary/02.md",
            "files/work-diary/03.md", "files/work-diary/04.md",
            "files/work-diary/05.md", "files/work-diary/06.md",
            "files/work-diary/07.md",
        ],
        "found_msg": "我扫描了工作日记文件夹，发现这些：",
        "empty_msg": "工作日记文件夹里的文件我都已经找到了。",
        "need_password": "工作日记被密码保护了。8位数字——一个很重要的日子。\n\n入职资料里可能有线索。",
    },
    "private": {
        "names": ["私人文件夹", "加密文件夹", "异常观察"],
        "chapter_min": 2,
        "files": [
            "files/private/异常观察记录.txt",
            "files/private/账号密码.txt",
        ],
        "found_msg": "私人文件夹打开了。里面有这些东西：",
        "empty_msg": "私人文件夹里的文件我都已经找到了。",
        "need_password": "私人文件夹被加密了。需要密码……入职资料里可能写了一个。",
    },
    "recordings": {
        "names": ["录音", "公司服务器", "vpn", "网络", "远程服务器", "server", "audio"],
        "chapter_min": 2,
        "files": [
            "files/audio/录音-全员会议-0308.txt",
            "files/audio/录音-林璇陈玑-0313.txt",
            "files/audio/录音-陆天枢-0313.txt",
        ],
        "found_msg": "我连上了公司服务器，找到了这些录音：",
        "empty_msg": "录音文件夹里的文件我都已经找到了。",
        "need_password": "公司服务器需要通过 VPN 连接。需要 VPN 密码……异常观察记录旁边有个账号密码文件。",
    },
    "final": {
        "names": ["未命名文档", "最终文件", "证据", "核心文档", "新建文件夹"],
        "chapter_min": 2,
        "files": [
            "files/new-folder/未命名文档.md",
        ],
        "found_msg": "新建文件夹里找到了一个文件：",
        "empty_msg": "这个文件我早就找到了。",
        "need_password": "这个文件被终极密码保护着。线索散落在录音和研究笔记里。",
    },
    "research": {
        "names": ["研究笔记", "研究", "笔记", "research", "调查笔记"],
        "chapter_min": 3,
        "files": [
            "files/research/res-1.md",
            "files/research/res-2.md",
            "files/research/res-3.md",
        ],
        "found_msg": "研究笔记文件夹里有她更深入的分析……她真的在系统地调查他们。",
        "empty_msg": "研究笔记我都已经整理好了。",
    },

}


def _extract_scan_target(user_input: str) -> str:
    """从玩家输入中提取扫描目标，返回 target_id 或空字符串"""
    lowered = user_input.lower().strip()
    for target_id, config in SCAN_TARGETS.items():
        # 直接匹配 target_id（用于密码弹窗返回的 target_id）
        if target_id.lower() in lowered:
            return target_id
        for name in config["names"]:
            if name in lowered:
                return target_id
    return ""




def handle_scan_command(game_state: dict, natural: bool = False, target: str = "") -> dict:
    """
    处理扫描命令
    必须指定目标文件夹，不能直接扫描全部

    Args:
        target: 扫描目标 ID（如 work-diary、private、recordings、final）
    """
    memory = _get_memory(game_state)
    chapter = game_state.get("chapter", 1)

    # 没有指定目标 → 与获取一致：列出已发现未解锁的文件夹
    if not target:
        if natural:
            return _build_get_folder_hint(game_state)
        return {"reply": f"用法：/scan [目标]，例如 /scan 工作日记", "type": "ai"}

    # 检查目标是否存在
    target_config = SCAN_TARGETS.get(target)
    if not target_config:
        return {
            "reply": f"我不知道你说的'{target}'在哪里。\n试试：扫描 工作日记、扫描 私人文件夹、扫描 公司服务器。",
            "type": "ai",
        }

    # 检查目标是否已经被发现（玩家需要读过含线索的文件）
    if not folder_discovery.is_target_discovered(game_state, target):
        display_name = target_config.get("names", [target])[0]
        return {
            "reply": (
                f"我还没发现「{display_name}」在哪。\n"
                "\n"
                "先读读已经解锁的文件吧，线索藏在里面。"
            ),
            "type": "ai",
        }

    # ch1：任何明确扫描目标都导向 D 盘工作日记密码
    if chapter == 1:
        if target == "work-diary":
            return _prompt_password_for_target("work-diary", game_state, natural)
        return _build_get_folder_hint(game_state)


    # ch2+：检查章节要求
    if chapter < target_config.get("chapter_min", 1):
        return {
            "reply": "那个位置我还没有权限访问。先把能打开的文件夹都看看？",
            "type": "ai",
        }
        return {
            "reply": "那个位置我还没有权限访问。先把能打开的文件夹都看看？",
            "type": "ai",
        }

    # 检查是否需要密码
    if target_config.get("need_password") and chapter < {
        "private": 3, "recordings": 4, "final": 6, "work-diary": 2,
    }.get(target, 99):
        return _prompt_password_for_target(target, game_state, natural)

    # 检查是否已经全部解锁
    files = target_config["files"]
    newly_unlocked = []
    for f in files:
        if f not in memory.accessible_files:
            memory.unlock_file(f)
            newly_unlocked.append(f)

    _save_memory(game_state, memory)

    if newly_unlocked:
        file_names = [f.replace("files/", "") for f in newly_unlocked]
        if natural:
            reply = (
                f"{target_config['found_msg']}\n"
                + "\n".join(f"  · {name}" for name in file_names)
                + "\n\n"
                "要我打开哪一个？"
            )
        else:
            reply = (
                f"扫描 {target} 完成。发现：\n\n"
                + "\n".join(f"  · {name}" for name in file_names)
            )
        return {
            "reply": reply,
            "type": "ai",
            "unlock": newly_unlocked,
        }

    return {
        "reply": target_config["empty_msg"],
        "type": "ai",
    }


def _prompt_password_for_target(target: str, game_state: dict, natural: bool = False) -> dict:
    """为指定目标弹出密码输入提示"""
    target_config = SCAN_TARGETS.get(target)
    if not target_config:
        return {"reply": "我不知道该解锁哪里。", "type": "ai"}

    game_state["awaiting_password"] = True
    game_state["pending_get_target"] = target

    messages = {
        "work-diary": "D 盘的「工作日记」文件夹被 8 位数字密码保护。\n\n密码提示：人生中最特别的一天",
        "private": "私人文件夹被加密了。\n\n密码提示：原始密码",
        "recordings": "公司服务器需要 VPN 密码才能连接。\n\n密码提示：私人文件夹里的账号密码文件有VPN信息。",
        "final": "未命名文档被终极密码保护。\n\n密码提示：开始接触异常的日子。",
        "research": "研究笔记文件夹可以直接扫描，不需要密码。",
    }
    msg = messages.get(target, target_config.get("need_password", "请输入密码。"))
    return {"reply": msg, "type": "ai", "password_prompt": True, "password_target": target}


def _try_unlock_with_password(target: str, password: str, game_state: dict, natural: bool = False) -> dict:
    """用玩家提供的密码尝试解锁目标文件夹"""
    passwords = _load_passwords()
    pwd_config = passwords.get(password)
    if not pwd_config:
        return _make_password_error_reply(target)

    unlock_list = pwd_config.get("unlocks", [])
    # 检查密码是否确实能解锁该目标
    target_config = SCAN_TARGETS.get(target)
    if target_config:
        target_files = set(target_config.get("files", []))
        if not target_files.intersection(set(unlock_list)):
            return _make_password_error_reply(target)

    # 密码正确：应用密码效果
    _reset_off_topic(game_state)
    game_state["awaiting_password"] = False
    game_state.pop("pending_get_target", None)

    new_chapter = pwd_config.get("chapter")
    new_state = pwd_config.get("next_state")
    if new_chapter:
        game_state["chapter"] = new_chapter
    if new_state:
        game_state["ai_state"] = new_state
        if new_state == "curious":
            game_state["mm_name_revealed"] = True
    if new_chapter == 6:
        game_state["document_read"] = True

    memory = _get_memory(game_state)
    if unlock_list:
        memory.unlock_files(unlock_list)

    # 解锁后：将「待扫描文件夹」线索转为「文件线索」
    # 找到当前 target 的显示名
    target_display = SCAN_TARGETS.get(target, {}).get("names", [target])[0] if SCAN_TARGETS.get(target) else target
    # 删除旧的待扫描文件夹线索
    memory.clues = [c for c in memory.clues if not (c.get("category") == "待扫描文件夹" and c.get("target_id") == target)]
    # 添加新文件线索
    file_names_for_clue = [f.replace("files/", "") for f in unlock_list]
    memory.add_clue({
        "source": target,
        "category": "文件线索",
        "text": f"已解锁「{target_display}」：{', '.join(file_names_for_clue)}",
    })

    _save_memory(game_state, memory)

    hint = pwd_config.get("hint", "权限已解锁")
    file_names = [f.replace("files/", "") for f in unlock_list]
    reply = f"……密码有效。\n\n{hint}"
    if "要我打开" not in hint and "新文件" not in hint and file_names:
        reply += f"\n\n新文件：{', '.join(file_names)}\n\n要我打开哪一个？"
    return {
        "reply": reply,
        "type": "ai",
        "unlock": unlock_list,
        "memory_updated": True,
    }


def _make_password_error_reply(target: str) -> dict:
    """生成密码错误回复，并提示该去哪里找正确密码"""
    hints = {
        "work-diary": "这个密码不对。\n\n提示：入职资料里写着张知予的生日，格式是 8 位数字（如 20030323）。",
        "private": "这个密码不对。\n\n提示：D1 工作日记和入职资料里都提到系统初始密码。",
        "recordings": "这个密码不对。\n\n提示：私人文件夹里的「账号密码.txt」有 VPN 密码。",
        "final": "这个密码不对。\n\n提示：听听录音，「起源计划」和入职日期组合起来就是最终密码。",
    }
    return {
        "reply": hints.get(target, "密码错误。请再试一次。"),
        "type": "ai",
    }





def _find_next_locked_target(game_state: dict) -> str:
    """
    根据当前已发现目标中找出尚未解锁的下一个目标。
    只返回已被发现（玩家读过对应文件）的 target_id。
    """
    memory = _get_memory(game_state)
    discovered = set(folder_discovery.get_discovered_targets(game_state))
    target_order = ["work-diary", "private", "recordings", "final"]

    for target in target_order:
        if target not in discovered:
            continue
        config = SCAN_TARGETS.get(target)
        if not config:
            continue
        files = config.get("files", [])
        if files and not all(f in memory.accessible_files for f in files):
            return target
    return ""


def _looks_like_password(token: str) -> bool:
    """判断 token 是否像密码（数字>=6位，或包含至少两类 ASCII 字符）"""
    if not token or len(token) < 6:
        return False
    # 至少包含一个 ASCII 字符
    if not any(c.isascii() for c in token):
        return False
    if token.isdigit():
        return True
    has_lower = any(c.islower() and c.isascii() for c in token)
    has_upper = any(c.isupper() and c.isascii() for c in token)
    has_digit = any(c.isdigit() for c in token)
    has_symbol = any(not c.isalnum() and c.isascii() for c in token)
    classes = sum([has_lower, has_upper, has_digit, has_symbol])
    return classes >= 2



def _mask_password(command: str) -> str:
    """把命令中的密码替换为「密码」字样，用于前端展示"""
    parts = command.strip().split()
    if len(parts) >= 3 and _looks_like_password(parts[-1]):
        # 例如：获取 工作日记 20030323 → 获取 工作日记 密码
        return f"{parts[0]} {parts[1]} 密码"
    return command


def _build_get_folder_hint(game_state: dict) -> dict:
    """
    为「获取/解锁」空目标或未识别目标时生成提示：
    - 列出已发现但未解锁的文件夹
    - 没有可解锁目标时提示阅读文档获取线索
    """
    discovered = folder_discovery.get_discovered_targets(game_state)
    memory = _get_memory(game_state)

    locked = []
    for target_id in discovered:
        config = SCAN_TARGETS.get(target_id)
        if not config:
            continue
        files = config.get("files", [])
        if files and not all(f in memory.accessible_files for f in files):
            display_name = config.get("names", [target_id])[0]
            locked.append((display_name, target_id))

    if locked:
        lines = ["目前发现还没解锁的文件夹有这些："]
        for name, _ in locked:
            lines.append(f"  · {name}")
        lines.append("\n可以试试：")
        for name, _ in locked:
            lines.append(f"  · 获取 {name} 密码")
        return {"reply": "\n".join(lines), "type": "ai"}

    return {
        "reply": (
            "我还没发现可以解锁的文件夹。\n"
            "\n"
            "先读读已经解锁的文件，里面会提到被密码保护的文件夹线索。"
        ),
        "type": "ai",
    }


def handle_get_command(user_input: str, game_state: dict, natural: bool = False) -> dict:
    """
    处理'获取 目标 [密码]'命令
    支持：
      - 获取 工作日记 20030323     → 直接解锁
      - 获取 工作日记 密码          → 弹出密码输入框
      - 获取 工作日记              → 弹出密码输入框（保留旧习惯）
    """
    lowered = user_input.lower().strip()
    # 去掉"获取"类前缀
    for kw in INTENT_KEYWORDS["get"]:
        lowered = lowered.replace(kw.lower(), "")
    lowered = lowered.strip()

    if not lowered:
        return _build_get_folder_hint(game_state)

    parts = lowered.split()
    password = ""
    # 判断末尾 token 是否是密码
    if parts:
        last = parts[-1]
        if last == "密码":
            # 获取 工作日记 密码 → 只弹出密码框，不验证
            password = ""
            parts = parts[:-1]
        elif _looks_like_password(last):
            password = last
            parts = parts[:-1]
        else:
            password = ""

    target_text = " ".join(parts)
    target = _extract_scan_target(target_text) if target_text else ""

    if not target:
        return _build_get_folder_hint(game_state)

    # 检查目标是否已被发现
    if not folder_discovery.is_target_discovered(game_state, target):
        display_name = SCAN_TARGETS[target].get("names", [target])[0]
        return {
            "reply": (
                f"我还没发现「{display_name}」在哪。\n"
                "\n"
                "先读读已经解锁的文件，线索会告诉你该去哪里。"
            ),
            "type": "ai",
        }

    if password:
        return _try_unlock_with_password(target, password, game_state, natural)

    return _prompt_password_for_target(target, game_state, natural)



# ============ 自然语言意图识别 ============
INTENT_KEYWORDS = {
    "scan": ["扫描", "scan", "查找", "找文件", "发现文件"],
    "files": ["有什么文件", "文件列表", "列出文件", "能看什么", "有哪些文件", "文件"],
    "read": ["打开", "读取", "读一下", "查看", "读", "打开文件", "读读"],
    "get": ["获取", "get", "解锁", "解密", "打开密码", "输入密码打开"],
    "status": ["状态", "进度", "到哪了", "情况"],
    "memory": ["记忆", "你知道什么", "你知道多少", "你知道些什么"],
    "clue": ["查看线索", "线索", "有什么线索", "发现什么", "整理线索"],
    "hint": ["提示", "下一步"],
    "password_hint": ["密码是什么", "密码多少", "怎么破解密码", "密码提示", "怎么分析密码", "密码在哪", "找不到密码", "密码线索", "当前密码", "这个密码"],
    "folder_help": ["怎么获取文件夹", "怎么解锁文件夹", "怎么打开文件夹", "怎么找文件夹", "文件夹在哪", "找不到文件夹", "怎么获取文件", "怎么解锁文件", "如何获取文件夹", "如何解锁文件夹", "如何获取文件", "怎么扫描文件夹", "怎么获得文件夹", "文件夹怎么打开", "文件怎么获取"],
    "reset": ["重置", "重新开始", "重来"],
}




# 确认词：用于执行 M-M 上一条建议
CONFIRM_WORDS = {"好", "好的", "可以", "行", "嗯", "是的", "没错", "就这么办", "听你的", "好呀", "好吧", "ok", "yes", "打开", "执行", "试试", "试一下", "试一试"}


# 建议模式：从 AI 回复中提取可执行命令（正则，命令）
SUGGESTION_PATTERNS = [
    # 桌面文件
    (r"(?:打开|读一下?|看看)\s+todolist", "打开 todolist.txt"),
    (r"(?:打开|读一下?|看看)\s+入职资料", "打开 入职资料.txt"),
    # 工作日记
    (r"(?:打开|读一下?|看看)\s+第?一篇工作日记", "打开 第一篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?二篇工作日记", "打开 第二篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?三篇工作日记", "打开 第三篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?四篇工作日记", "打开 第四篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?五篇工作日记", "打开 第五篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?六篇工作日记", "打开 第六篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?七篇工作日记", "打开 第七篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?八篇工作日记", "打开 第八篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?九篇工作日记", "打开 第九篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+第?十篇工作日记", "打开 第十篇工作日记"),
    (r"(?:打开|读一下?|看看)\s+工作日记", "打开 工作日记"),
    # 私人文件夹
    (r"(?:打开|读一下?|看看)\s+异常观察记录", "打开 异常观察记录.txt"),
    (r"(?:打开|读一下?|看看)\s+账号密码", "打开 账号密码.txt"),
    # 录音
    (r"(?:打开|听听)\s+全员会议录音|(?:打开|听听)\s+录音-全员会议", "打开 录音-全员会议"),
    (r"(?:打开|听听)\s+林璇陈玑", "打开 录音-林璇陈玑"),
    (r"(?:打开|听听)\s+陆天枢", "打开 录音-陆天枢"),
    (r"(?:打开|听听)\s+录音", "打开 录音"),
    # 其他文件
    (r"(?:打开|读一下?|看看)\s+未命名文档", "打开 未命名文档.md"),
    (r"(?:打开|读一下?|看看)\s+研究笔记\s*1", "打开 研究笔记1"),
    (r"(?:打开|读一下?|看看)\s+研究笔记\s*2", "打开 研究笔记2"),
    (r"(?:打开|读一下?|看看)\s+研究笔记\s*3", "打开 研究笔记3"),
    (r"(?:打开|读一下?|看看)\s+邮件\s*1", "打开 邮件1"),
    (r"(?:打开|读一下?|看看)\s+邮件\s*2", "打开 邮件2"),
    (r"(?:打开|读一下?|看看)\s+邮件\s*3", "打开 邮件3"),
    (r"(?:打开|读一下?|看看)\s+邮件\s*4", "打开 邮件4"),
    (r"(?:打开|读一下?|看看)\s+邮件\s*5", "打开 邮件5"),
    (r"(?:打开|读一下?|看看)\s+邮件\s*6", "打开 邮件6"),
    # 扫描/获取（前端展示密码，点击后弹出密码输入框）
    (r"(?:扫描|获取|解锁)\s+工作日记", "获取 工作日记 密码"),
    (r"(?:扫描|获取|解锁)\s+私人文件夹", "获取 私人文件夹 密码"),
    (r"(?:扫描|获取|解锁|连接)\s+公司服务器", "获取 公司服务器 密码"),
    (r"(?:扫描|获取|解锁)\s+未命名文档", "获取 未命名文档 密码"),
    (r"(?:扫描|查看)\s+研究笔记", "扫描 研究笔记"),
    (r"(?:扫描|查看)\s+邮件", "扫描 邮件"),
    # 工具
    (r"查看线索", "查看线索"),
    (r"(?:下一步|给点)?提示|下一步建议|该做什么", "下一步建议"),
]


def extract_suggestions_from_reply(reply: str, game_state: dict) -> list:
    """
    从 AI 回复中提取建议命令列表。
    返回 [ {"text": 展示文本, "command": 执行命令} ]
    """
    suggestions = []
    seen = set()
    for pattern, command in SUGGESTION_PATTERNS:
        if re.search(pattern, reply, re.IGNORECASE) and command not in seen:
            seen.add(command)
            suggestions.append({"text": command, "command": command})
    return suggestions


# 中文数字选择词
_CN_CHOICE_NUMBERS = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
}






CN_NUMBERS = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
}

INT_TO_CN = {v: k for k, v in CN_NUMBERS.items()}


# 中文数字选择词（用于多选建议）
_CN_CHOICE_NUMBERS = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
}


def _parse_choice(user_input: str, suggestions: list, game_state: dict = None) -> dict:
    """
    从玩家输入中解析选择，返回对应的建议字典或 None。
    支持：1/2/3、第一条/第二个、建议文本中的关键词。
    """
    if not suggestions:
        return None

    lowered = user_input.lower().strip()
    if not lowered:
        return None

    # 1. 纯数字 / 第N条 / 第N个
    choice_idx = None
    if lowered.isdigit():
        choice_idx = int(lowered) - 1
    else:
        # 匹配 "第一条/第一个/第一"、"第二个" 等
        m = re.search(r"第\s*([一二三四五六七八九十1234567890]+)\s*(?:条|个|项)?", lowered)
        if m:
            num_str = m.group(1)
            choice_idx = _CN_CHOICE_NUMBERS.get(num_str, 0) - 1
        else:
            # 匹配 "第一个/第一个建议" 等无"第"前缀的口语
            for text, num in _CN_CHOICE_NUMBERS.items():
                if text in lowered and ("个" in lowered or "条" in lowered or "建议" in lowered):
                    choice_idx = num - 1
                    break

    if choice_idx is not None and 0 <= choice_idx < len(suggestions):
        return suggestions[choice_idx]

    # 2. 匹配建议文本或命令
    for s in suggestions:
        if s["command"].lower() in lowered:
            return s
        if s["text"].lower() in lowered:
            return s

    # 3. 从输入中提取文件/目标，匹配建议命令中的关键词
    if game_state:
        memory = _get_memory(game_state)
        filename = _extract_filename(user_input, memory.accessible_files)
        if filename:
            for s in suggestions:
                if filename.lower() in s["command"].lower():
                    return s
        target = _extract_scan_target(user_input)
        if target:
            for s in suggestions:
                if target.lower() in s["command"].lower():
                    return s

    return None



def _cn_number_to_int(text: str) -> str:
    """把中文数字转成阿拉伯数字字符串，如'第一篇'->'1篇'"""
    result = []
    for ch in text:
        if ch in CN_NUMBERS:
            result.append(str(CN_NUMBERS[ch]))
        else:
            result.append(ch)
    return ''.join(result)


def _extract_filename(user_input: str, accessible_files: set) -> str:
    """
    从玩家自然语言输入中提取文件路径
    支持别名：todolist、D1、第一篇、入职资料 等
    """
    lowered = user_input.lower()

    # 去掉读取动词，避免"打开 入职自立"这类输入影响模糊匹配
    cleaned = lowered
    for kw in INTENT_KEYWORDS.get("read", []):
        cleaned = cleaned.replace(kw.lower(), "")
    cleaned = cleaned.strip() or lowered

    alias_map = {}
    for full_path in accessible_files:
        aliases = set()
        aliases.add(full_path.lower())

        short = full_path.replace("files/", "")
        # 子目录内文件的别名：去掉文件夹前缀（如 deck/todolist.txt → todolist.txt）
        for dir_prefix in ("deck/", "private/", "new-folder/"):
            if dir_prefix in short:
                flat = short.replace(dir_prefix, "")
                aliases.add(flat.lower())
                aliases.add(flat.rsplit(".", 1)[0].lower())

        aliases.add(short.lower())

        # 去掉扩展名
        name_no_ext = short.rsplit(".", 1)[0]
        aliases.add(name_no_ext.lower())

        # 工作日记特殊别名
        if "work-diary/" in full_path:
            num = short.split("/")[-1].split(".")[0]
            num_int = int(num)
            cn_num = INT_TO_CN.get(num_int, str(num_int))
            aliases.add(num)
            aliases.add(f"d{num}")
            aliases.add(f"D{num}")
            aliases.add(f"第{num_int}篇")
            aliases.add(f"第{cn_num}篇")  # 中文数字：第一篇
            aliases.add(f"第{num_int}天")
            aliases.add(f"第{cn_num}天")  # 中文数字：第一天
            aliases.add(f"日记{num_int}")
            aliases.add(f"日记{cn_num}")  # 中文数字：日记一
        
        # 研究笔记特殊别名
        if "research/" in full_path:
            name_part = short.split("/")[-1].split(".")[0]
            # 支持 res-1、research-1、1 等命名
            num = name_part.lstrip("res").lstrip("earch").lstrip("-") or name_part
            aliases.add(f"研究笔记{num}")
            aliases.add(f"笔记{num}")
            aliases.add(f"r{num}")
            aliases.add(name_part.lower())

        # 邮件特殊别名
        if "emails/" in full_path:
            name_part = short.split("/")[-1].split(".")[0]
            num = name_part.lstrip("email").lstrip("-") or name_part
            aliases.add(f"邮件{num}")
            aliases.add(f"email{num}")
            aliases.add(name_part.lower())

        # 录音文件特殊别名（在 audio/ 子目录下）
        if "录音-" in full_path:
            aliases.add("录音")
            audio_short = short.replace("audio/", "")
            aliases.add(audio_short.lower())
            if "全员会议" in full_path:
                aliases.add("全员会议")
                aliases.add("会议录音")
            elif "林璇陈玑" in full_path:
                aliases.add("林璇陈玑")
                aliases.add("两人对话")
            elif "陆天枢" in full_path:
                aliases.add("陆天枢")
                aliases.add("天枢")

        for alias in aliases:
            alias_map[alias] = full_path

    # 按长度降序匹配，优先匹配长别名，避免"D1"误匹配到"D10"
    for alias in sorted(alias_map.keys(), key=len, reverse=True):
        if alias in cleaned:
            return alias_map[alias]

    # 模糊匹配兜底：处理"入职自立"这类 typo
    if accessible_files:
        corrected, score = fuzzy_matcher.correct_filename(cleaned, accessible_files)
        if corrected:
            return corrected

    return None


def detect_intent(user_input: str, accessible_files: set, game_state: dict = None) -> tuple:
    """
    识别玩家自然语言意图
    返回: (intent, argument)
    intent: scan/scan_ask/files/read/get/status/memory/clue/hint/help/reset/confirm/choose/none
    argument: scan/get 时为 target_id，read 时为文件路径，confirm 时为 last_suggestion，
              choose 时为选中的建议字典，其他为 None
    """
    lowered = user_input.lower().strip()
    game_state = game_state or {}

    # 1. 待选择状态：如果玩家正在回复多选建议，优先解析选择
    pending_choices = game_state.get("pending_choices", [])
    if pending_choices:
        chosen = _parse_choice(user_input, pending_choices, game_state)
        if chosen:
            return "choose", chosen
        # 如果解析失败，继续走其他意图（允许玩家换问题）

    # 2. 确认词：单独说"好""可以""试试"等，执行 M-M 建议
    if lowered in CONFIRM_WORDS:
        last_suggestion = game_state.get("last_suggestion", "")
        return "confirm", last_suggestion

    # get 意图：获取/解锁加密文件夹
    for kw in INTENT_KEYWORDS["get"]:
        if kw.lower() in lowered:
            return "get", user_input

    # 文件夹帮助：不知道怎么获取文件夹
    for kw in INTENT_KEYWORDS["folder_help"]:
        if kw.lower() in lowered:
            return "folder_help", None

    # scan 意图特殊处理：检测是否有明确目标
    for kw in INTENT_KEYWORDS["scan"]:
        if kw.lower() in lowered:
            target = _extract_scan_target(user_input)
            if target:
                return "scan", target
            else:
                return "scan_ask", None

    # read 意图：先匹配显式读关键词
    for kw in INTENT_KEYWORDS["read"]:
        if kw.lower() in lowered:
            filename = _extract_filename(user_input, accessible_files)
            if filename:
                return "read", filename
            break

    # 直接输入文件名（如 "todolist"、"d1"）也视为读取意图
    bare_filename = _extract_filename(user_input, accessible_files)
    if bare_filename:
        return "read", bare_filename

    # 其他通用意图
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent in ("scan", "read", "get"):
            continue
        for kw in keywords:
            if kw.lower() in lowered:
                return intent, None

    return "none", None


def _build_default_suggestions(game_state: dict) -> list:
    """
    根据当前章节、已读文件和已发现目标生成主线建议列表。
    """
    chapter = game_state.get("chapter", 1)
    read = set(game_state.get("files_read", []))
    discovered = set(folder_discovery.get_discovered_targets(game_state))
    has_read = lambda path: path in read

    def _main_quest_hint(text: str, command: str) -> dict:
        return {"text": text, "command": command}

    # Chapter 1：引导玩家从桌面文件到发现工作日记
    if chapter == 1:
        if not has_read("files/deck/todolist.txt"):
            return [_main_quest_hint("试试阅读 todolist.txt", "打开 todolist.txt")]
        if not has_read("files/deck/入职资料.txt"):
            return [_main_quest_hint("看看 入职资料 中是否有线索", "打开 入职资料.txt")]
        if "work-diary" not in discovered:
            return [_main_quest_hint("再读一遍 todolist 寻找线索", "打开 todolist.txt")]
        return [_main_quest_hint("尝试扫描 工作日记 文件夹", "获取 工作日记 密码")]

    # Chapter 2：工作日记是主线，读完关键篇后推进到私人文件夹
    if chapter == 2:
        diary_files = [
            "files/work-diary/01.md", "files/work-diary/02.md",
            "files/work-diary/03.md", "files/work-diary/04.md",
            "files/work-diary/05.md", "files/work-diary/06.md",
            "files/work-diary/07.md", "files/work-diary/08.md",
            "files/work-diary/09.md", "files/work-diary/10.md",
        ]
        # 始终优先指向下一篇未读工作日记，避免已读还推"继续读"
        for f in diary_files:
            if not has_read(f):
                num = f.split("/")[-1].split(".")[0].lstrip("0") or "1"
                cn = INT_TO_CN.get(int(num), num)
                return [_main_quest_hint(f"开始阅读 第{cn}篇工作日记", f"打开 第{cn}篇工作日记")]
        # 全部已读：推进主线到私人文件夹
        if "private" in discovered:
            return [_main_quest_hint("尝试扫描 私人文件夹 文件夹", "获取 私人文件夹 密码")]
        return [_main_quest_hint("再读工作日记，找私人文件夹线索", "打开 工作日记")]


    # Chapter 3：私人文件夹 + 研究笔记
    if chapter == 3:
        if not has_read("files/private/异常观察记录.txt"):
            return [_main_quest_hint("前往 异常观察记录 寻找一下线索", "打开 异常观察记录.txt")]
        if not has_read("files/private/账号密码.txt"):
            return [_main_quest_hint("看看 账号密码 是否有可用信息", "打开 账号密码.txt")]
        if "recordings" not in discovered:
            return [_main_quest_hint("再读工作日记，找 VPN 线索", "打开 工作日记")]
        return [_main_quest_hint("尝试扫描 公司服务器 文件夹", "获取 公司服务器 密码")]

    # Chapter 4：录音
    if chapter == 4:
        if not has_read("files/audio/录音-全员会议-0308.txt"):
            return [_main_quest_hint("听听 录音-全员会议", "打开 录音-全员会议")]
        if not has_read("files/audio/录音-林璇陈玑-0313.txt"):
            return [_main_quest_hint("听听下一个录音 录音-林璇陈玑", "打开 录音-林璇陈玑")]
        if not has_read("files/audio/录音-陆天枢-0313.txt"):
            return [_main_quest_hint("听听剩下的录音 录音-陆天枢", "打开 录音-陆天枢")]
        if "final" not in discovered:
            return [_main_quest_hint("读研究笔记，找最终线索", "打开 研究笔记")]
        return [_main_quest_hint("尝试扫描 未命名文档 ", "获取 未命名文档 密码")]

    # Chapter 5 / 6：最终密码
    if chapter >= 5:
        if not has_read("files/new-folder/未命名文档.md"):
            return [_main_quest_hint("尝试解开 未命名文档", "获取 未命名文档 密码")]
        return []

    return []


def _save_suggestions(result: dict, user_input: str, game_state: dict) -> dict:
    """
    从返回结果中提取并保存建议命令。
    如果 AI 回复没有提取到建议，则保留前端传来的建议。
    """
    reply = result.get("reply", "")
    extracted = extract_suggestions_from_reply(reply, game_state)

    # 选择追问：必须保留当前选项
    if result.get("type") == "choose_prompt":
        suggestions = game_state.get("pending_choices", [])
    elif result.get("suggestions"):
        # 优先使用响应库等来源显式提供的建议
        suggestions = result["suggestions"]
    elif extracted:
        # 其次使用当前回复中提取的建议
        suggestions = extracted
    else:
        # 没有提取到时，按当前状态重新生成默认建议
        suggestions = _build_default_suggestions(game_state)

    # 统一格式
    formatted = []
    for s in suggestions:
        if isinstance(s, dict) and "command" in s:
            formatted.append({"text": s.get("text", s["command"]), "command": s["command"]})
        elif isinstance(s, str):
            formatted.append({"text": s, "command": s})

    game_state["last_suggestions"] = formatted
    # 如果当前回复不是追问，则清除待选择状态（新建议会覆盖）
    if result.get("type") != "choose_prompt":
        game_state.pop("pending_choices", None)

    return result



def _build_password_hint(game_state: dict) -> str:
    """
    根据当前已解锁状态生成密码分析引导，不直接给出完整密码。
    """
    memory = _get_memory(game_state)
    accessible = memory.accessible_files

    def is_unlocked(target_id: str) -> bool:
        cfg = SCAN_TARGETS.get(target_id)
        if not cfg:
            return True
        return all(f in accessible for f in cfg.get("files", []))

    if not is_unlocked("work-diary"):
        return (
            "工作日记被 8 位数字密码保护。\n"
            "提示：todolist 里写这是一个'不会忘记的日子'。\n"
            "入职资料里有张知予的生日，把它写成 8 位数字试试看。"
        )
    if not is_unlocked("private"):
        return (
            "私人文件夹需要系统初始密码。\n"
            "提示：入职资料和工作日记 D1 都写过这个密码。\n"
            "格式是 ZY + 年份 + ! + starlight。"
        )
    if not is_unlocked("recordings"):
        return (
            "公司服务器需要 VPN 密码。\n"
            "提示：私人文件夹里有个「账号密码.txt」文件，里面记录了 VPN 密码。\n"
            "格式是 Star + Core + @ + 年份。"
        )
    if not is_unlocked("final"):
        return (
            "未命名文档被终极密码保护。\n"
            "提示：最终密码由两部分组成——录音里提到的「起源计划」英文名，和张知予的入职日期。\n"
            "入职日期是 3 月 6 日。"
        )
    return "目前没有发现需要密码的未解锁文件。"


def _build_analysis_reply(game_state: dict, focus: str = "") -> str:
    """
    根据玩家关注点与当前进度生成综合分析。
    """
    memory = _get_memory(game_state)
    clues = memory.get_clues()
    accessible = memory.accessible_files
    focus = focus.lower()

    lines = []

    # 密码分析
    if not focus or "密码" in focus or "锁" in focus or "解" in focus:
        lines.append("【关于当前密码】")
        if "files/work-diary/01.md" not in accessible:
            lines.append("· 工作日记被 8 位生日密码保护。入职资料里有生日 2003年3月23日，可写成 8 位数字。")
        elif "files/private/异常观察记录.txt" not in accessible:
            lines.append("· 私人文件夹需要系统初始密码。入职资料和工作日记 D1 都有记录，格式是 ZY + 年份 + ! + starlight。")
        elif "files/audio/录音-全员会议-0308.txt" not in accessible:
            lines.append("· 公司服务器需要 VPN 密码。私人文件夹的「账号密码.txt」里有记录。")
        elif "files/new-folder/未命名文档.md" not in accessible:
            lines.append("· 最终密码 = 起源计划英文名 + 张知予入职日期（3月6日）。")
        else:
            lines.append("· 所有加密文件都已解锁。")

    # 线索分析
    if not focus or "线索" in focus or "证据" in focus:
        if clues:
            lines.append("\n【已收集线索】")
            for c in clues[-6:]:
                lines.append(f"· [{c.get('category', '线索')}] {c.get('text', '')}")
        else:
            lines.append("\n【线索】目前还没收集到明确线索。多读取文件会有发现。")

    # 下一步
    if not focus or "下一步" in focus or "做" in focus:
        next_target = _find_next_locked_target(game_state)
        if next_target:
            display_name = SCAN_TARGETS[next_target].get("names", [next_target])[0]
            lines.append(f"\n【下一步】「{display_name}」尚未解锁，可以优先寻找它的密码。")

    return "\n".join(lines) if lines else "你想让我分析什么？"


def _build_file_status_reply(game_state: dict) -> dict:
    """
    返回文件状态清单：
    - 已阅读文件
    - 未阅读文件
    - 待解锁文件夹（标红⚠，若无已发现且待解锁则不展示）
    """
    memory = _get_memory(game_state)
    accessible = sorted(memory.accessible_files)
    read = sorted(memory.processed_files)
    unread = [f for f in accessible if f not in read]

    # 已发现但未解锁的文件夹
    discovered_locked = []
    discovered_targets = folder_discovery.get_discovered_targets(game_state)
    for target_id in discovered_targets:
        cfg = SCAN_TARGETS.get(target_id)
        if not cfg:
            continue
        target_files = cfg.get("files", [])
        if target_files and not all(f in accessible for f in target_files):
            display_name = cfg.get("names", [target_id])[0]
            discovered_locked.append(display_name)

    lines = []

    if discovered_locked:
        lines.append("【⚠ 待扫描文件夹】")
        lines.extend([f"  ⚠ {name}" for name in discovered_locked])

    lines.append("\n【已阅读文件】")
    if read:
        lines.extend([f"  · {f.replace('files/', '')}" for f in read])
    else:
        lines.append("  （无）")

    lines.append("\n【未阅读文件】")
    if unread:
        lines.extend([f"  · {f.replace('files/', '')}" for f in unread])
    else:
        lines.append("  （无）")

    return {"reply": "\n".join(lines), "type": "ai"}



# ============ 命令处理 / 自然语言意图 ============

def handle_natural_intent(intent: str, argument, game_state: dict) -> dict:
    """
    执行自然语言意图，并用 M-M 口吻包装结果
    """
    memory = _get_memory(game_state)

    if intent == "scan_ask":
        # 无目标扫描 → 反问玩家想扫描哪里
        result = handle_scan_command(game_state, natural=True, target="")
        result["type"] = "ai"
        return result

    if intent == "scan":
        # 有目标扫描 → 扫描指定位置
        result = handle_scan_command(game_state, natural=True, target=argument)
        result["type"] = "ai"
        return result

    if intent == "get":
        # 获取/解锁加密文件夹
        result = handle_get_command(argument, game_state, natural=True)
        result["type"] = "ai"
        return result

    if intent == "folder_help":
        return {
            "reply": (
                "要获取被密码保护的文件夹，格式是：\n"
                "  · 获取 工作日记 密码\n"
                "  · 获取 私人文件夹 密码\n"
                "  · 获取 公司服务器 密码\n"
                "  · 获取 未命名文档 密码\n\n"
                "如果你已经知道具体密码，也可以直接说：\n"
                "  · 获取 工作日记 20030323"
            ),
            "type": "ai",
        }

    if intent == "files":
        result = _build_file_status_reply(game_state)
        result["expand_sidebar"] = True
        return result


    if intent == "read" and argument:
        return handle_file_command(f"/read {argument}", game_state, natural=True)

    if intent == "status":
        chapter = game_state.get("chapter", 1)
        state_name = game_state.get("ai_state", "dormant")
        return {
            "reply": (
                f"当前是第 {chapter} 章，我的状态是「{character_state.get_state(state_name)['name']}」。\n"
                f"可访问文件 {len(memory.accessible_files)} 个，已读 {len(memory.processed_files)} 个。\n"
                f"AI 调用次数 {game_state.get('ai_call_count', 0)}/{MAX_AI_CALLS_PER_GAME}。"
            ),
            "type": "ai",
        }

    if intent == "memory":
        ctx = memory.build_context_string(game_state.get("ai_state", "dormant"))
        return {
            "reply": f"我记得的东西：\n\n{ctx}",
            "type": "ai",
        }

    if intent == "clue":
        clues = memory.get_clues()
        if not clues:
            chapter = game_state.get("chapter", 1)
            no_clue_hints = {
                1: "目前还看不出明确线索。先读读桌面上的 todolist 和入职资料？\n\n我每读一个文件，就会从里面挑出关键的细节。",
                2: "目前还没整理出明确线索。\n\n读工作日记吧——她在那里面写了不少带 * 标记的异常。读得越多，我整理出来的越多。",
                3: "目前我整理出的线索还不多。\n\n你读过的每一个文件都会沉淀下来。试试让我读工作日记，或者打开私人文件夹的异常观察记录。",
                4: "线索在慢慢拼起来。\n\n你读了三段录音，里面提到了关键的几个名字。让我再读一遍研究笔记？",
                5: "线索接近完整。\n\n打开研究笔记 1-3，把它们和录音串起来。",
                6: "所有线索都齐了。\n\n未命名文档里有最后的答案。你决定怎么做。",
            }
            return {"reply": no_clue_hints.get(chapter, "再读一些文件，我就能整理出更完整的线索了。"), "type": "ai"}
        return {
            "reply": clue_manager.format_clues(clues),
            "type": "ai",
        }

    if intent == "hint":
        chapter = game_state.get("chapter", 1)
        hints = {
            1: "桌面上有 todolist.txt 和入职资料。todolist 里提到 D 盘需要 8 位密码——入职资料里应该有线索。",
            2: "读一下工作日记吧，D1 里有入职信息。也可以问我'还有什么文件'。",
            3: "日记里带 * 标记的日子很关键。私人文件夹里有异常观察记录，研究笔记里还有更深入的分析。",
            4: "入职资料里有密码。输入密码后，我可以连上公司服务器读取录音。",
            5: "录音里反复提到'起源计划'和她的入职日期 3 月 6 日。把所有线索拼起来。",
            6: "已经很接近了。输入你想到的最终密码，打开未命名文档。",
        }
        return {
            "reply": hints.get(chapter, "继续和我对话，我会把知道的告诉你。"),
            "type": "ai",
        }

    if intent == "password_hint":
        return {"reply": _build_password_hint(game_state), "type": "ai"}

    if intent == "analyze":
        return {"reply": _build_analysis_reply(game_state, argument or ""), "type": "ai"}

    if intent == "help":
        return {
            "reply": (
                "你可以直接和我对话，比如：\n"
                "  · '扫描 工作日记 文件夹'\n"
                "  · '打开 todolist'\n"
                "  · '读一下第一篇日记'\n"
                "  · '获取 工作日记 20030323'\n"
                "  · '查看线索'\n\n"
                "叫我扫描的时候，告诉我要扫哪个文件夹。\n"
                "我会直接执行并告诉你结果。"
            ),
            "type": "ai",
        }

    if intent == "choose":
        # 玩家在多选追问后做出了选择
        chosen = argument
        if not chosen or not isinstance(chosen, dict) or not chosen.get("command"):
            return {"reply": "我没听清你想选哪一个。再说一次？", "type": "ai"}
        game_state.pop("pending_choices", None)
        return generate_reply(chosen["command"], game_state)

    if intent == "confirm":
        # 玩家说"好"，执行上一条建议
        suggestions = game_state.get("last_suggestions", [])
        if not suggestions:
            # 兼容旧版 single last_suggestion
            suggestion = argument or game_state.get("last_suggestion", "")
            if not suggestion:
                return {"reply": "你同意什么？我还没给出建议呢。", "type": "ai"}
            return generate_reply(suggestion, game_state)

        if len(suggestions) == 1:
            return generate_reply(suggestions[0]["command"], game_state)

        # 多条建议：列出选项让玩家选择
        game_state["last_suggestions"] = suggestions
        game_state["pending_choices"] = suggestions
        lines = ["我有几个想法，你想先执行哪个？"]
        for i, s in enumerate(suggestions, 1):
            lines.append(f"  {i}. {s['text']}")
        lines.append("\n直接回复编号或内容就行。")
        return {
            "reply": "\n".join(lines),
            "type": "choose_prompt",
        }

    if intent == "reset":
        cache_manager.clear()
        return {
            "reply": "游戏已重置。所有记忆和进度已清空。",
            "type": "command",
            "reset": True,
        }

    return {"reply": "", "type": "none"}


# ============ 玩家命令处理 ============
def handle_command(user_input: str, game_state: dict) -> dict:
    """处理 / 开头的命令"""
    parts = user_input.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    memory = _get_memory(game_state)

    if cmd == "/help":
        unread_count = len(memory.get_unread_accessible())
        hint = ""
        if unread_count > 0:
            hint = f"\n  💡 你还有 {unread_count} 个未读文件，试试 /files 或 /scan 工作日记"
        return {
            "reply": (
                "── 可用命令 ──\n"
                "  /help                显示帮助\n"
                "  /status              查看 AI 状态\n"
                "  /files               列出可访问文件\n"
                "  /scan [目标]         扫描指定文件夹\n"
                "  /read [文件名]       读取文件\n"
                "  /chapter             查看章节进度\n"
                "  /memory              查看 M-M 的记忆\n"
                "  /hint                获得当前章节提示\n"
                "  /reset               重新开始\n"
                f"{hint}"
            ),
            "type": "command",
        }

    if cmd == "/status":
        return {
            "reply": (
                f"── 状态 ──\n"
                f"  章节: {game_state.get('chapter', 1)}\n"
                f"  AI 状态: {character_state.get_state(game_state.get('ai_state', 'dormant'))['name']}\n"
                f"  可访问文件: {len(memory.accessible_files)} 个\n"
                f"  已读文件: {len(memory.processed_files)} 个\n"
                f"  AI 调用: {game_state.get('ai_call_count', 0)}/{MAX_AI_CALLS_PER_GAME}\n"
            ),
            "type": "command",
        }

    if cmd == "/memory":
        # 新命令：查看 M-M 的记忆状态
        ctx = memory.build_context_string(game_state.get("ai_state", "dormant"))
        return {
            "reply": f"── M-M 的记忆 ──\n\n{ctx}",
            "type": "command",
        }

    if cmd in ("/files", "/ls"):
        if len(parts) > 1 and parts[1].strip().lower() == "detailed":
            return _build_file_status_reply(game_state)
        return handle_list_command("files", game_state)

    if cmd == "/scan":
        # 从 /scan [目标] 中提取目标
        target = parts[1].strip() if len(parts) > 1 else ""
        # 如果有目标文本，尝试匹配扫描目标
        if target:
            scan_target = _extract_scan_target(target)
            if scan_target:
                return handle_scan_command(game_state, target=scan_target)
        return handle_scan_command(game_state, target="")

    if cmd == "/read":
        return handle_file_command(user_input, game_state)

    if cmd == "/chapter":
        chapter = game_state.get("chapter", 1)
        state_name = game_state.get("ai_state", "dormant")
        return {
            "reply": (
                f"当前在第 {chapter} 章，AI 状态：{character_state.get_state(state_name)['name']}\n"
                f"可访问文件：{len(memory.accessible_files)} 个 | 已读：{len(memory.processed_files)} 个"
            ),
            "type": "command",
        }

    if cmd == "/reset":
        cache_manager.clear()
        return {
            "reply": "游戏已重置。所有记忆和进度已清空。",
            "type": "command",
            "reset": True,
        }

    if cmd == "/hint":
        chapter = game_state.get("chapter", 1)
        hints = {
            1: "todolist 里说她用了一个对她很特别的 8 位数字当密码。入职资料里有她的生日，格式是 8 位数字。",
            2: "试试读一下工作日记，D1 里有关于入职的信息。输入 /files 看看有什么。",
            3: "注意到日记里带 * 标记的日子了吗？那些是重要的。私人文件夹里有异常观察记录，还可以扫描研究笔记看看她更深入的分析。",
            4: "VPN密码在账号密码文件里。输入密码连接公司服务器，听听她录下了什么。",
            5: "录音里提到了'起源计划'——和她的入职日期有关。把所有线索串起来。",
            6: "你已经很接近真相了。组合所有线索，找到最后一个密码。",
        }
        return {
            "reply": hints.get(chapter, "继续和 M-M 对话，它可能会给你线索。试试 /files 看看。"),
            "type": "command",
        }

    return {"reply": f"未知命令：{cmd}。输入 /help 查看可用命令。", "type": "command"}


# ============ 核心：混合回复（RAG 增强版） ============
def generate_reply(user_input: str, game_state: dict) -> dict:
    """
    混合模式核心 — 决定走哪条路径生成回复

    新架构数据流：
    对话 → 角色卡（ai_fallback.CHARACTER_CARD）
         → 记忆（memory.build_context_string）
         → 知识检索（knowledge_search.build_knowledge_context）
         → AI 生成（ai_fallback.generate）
         → 迭代记忆（process_file/add_observation）
         → 反馈玩家
    """
    user_input = user_input.strip()
    if not user_input:
        return {"reply": "...", "type": "empty"}

    memory = _get_memory(game_state)

    # 1. 玩家命令（/开头）
    if user_input.startswith("/"):
        _reset_off_topic(game_state)
        return handle_command(user_input, game_state)

    # 2. 密码只接受「扫描/获取 文件名 密码」格式
    if _is_password_command_format(user_input):
        _reset_off_topic(game_state)
        return _save_suggestions(handle_get_command(user_input, game_state, natural=False), user_input, game_state)

    # 如果正在等待密码输入，允许直接输入纯密码（弹窗输入框兼容）
    if game_state.get("awaiting_password"):
        if _is_password_attempt(user_input):
            pending_target = game_state.pop("pending_get_target", "")
            game_state["awaiting_password"] = False
            result = _try_unlock_with_password(pending_target, user_input, game_state, natural=False)
            return _save_suggestions(result, user_input, game_state)
        # 不是密码，取消等待状态，继续走正常流程
        _reset_off_topic(game_state)
        game_state["awaiting_password"] = False
        game_state.pop("pending_get_target", None)




    # 3. 自然语言意图识别（面试作品重点：用对话代替命令行）
    last_suggestion = game_state.get("last_suggestion", "")
    intent, argument = detect_intent(user_input, memory.accessible_files, game_state)
    if intent != "none":
        result = handle_natural_intent(intent, argument, game_state)
        if result.get("type") != "none":
            _reset_off_topic(game_state)
            result = _save_suggestions(result, user_input, game_state)
            return result

    # 4. 响应库智能匹配（新核心路径：零 API 成本）
    chapter = game_state.get("chapter", 1)
    library_match = response_library.find_best_match(user_input, game_state, intent=intent)
    if library_match:
        # 只有推进主线的类别才重置 off_topic 计数
        if _is_game_advancing(library_match):
            _reset_off_topic(game_state)
        else:
            # 闲聊/问候/填充类：增加 off_topic 计数，超过阈值时引导回主线
            reply = _record_off_topic(game_state, library_match["reply"])
            return _save_suggestions({
                "reply": reply,
                "type": library_match["type"],
                "entry_id": library_match["entry_id"],
                "category": library_match["category"],
            }, user_input, game_state)
        result = {
            "reply": library_match["reply"],
            "type": library_match["type"],
            "entry_id": library_match["entry_id"],
            "category": library_match["category"],
        }
        # 添加条目中的建议追问
        suggestions = response_library.get_suggestions_for_entry(library_match["entry"])
        if suggestions:
            result["suggestions"] = suggestions
        return _save_suggestions(result, user_input, game_state)

    # 5. 学习库检索（复用之前 API 生成的结果）
    learned = learning_store.find_similar(user_input)
    if learned:
        # 学习库命中不推进主线，累加 off_topic
        reply = _record_off_topic(game_state, learned["reply"])
        return _save_suggestions({
            "reply": reply,
            "type": "learned_library",
            "learned_id": learned["id"],
            "learned_score": learned["score"],
        }, user_input, game_state)

    # 6. 本地 Q&A 库降级匹配（只处理超纲、基础身份、文件夹帮助问题）
    qa_result = qa_engine.find_answer(user_input, chapter=chapter, game_state=game_state)
    if qa_result and qa_result.get("category") in ("out_of_scope", "basic_identity", "folder_help"):
        if qa_result.get("category") == "out_of_scope":
            return _save_suggestions({
                "reply": _record_off_topic(game_state, qa_result["answer"]),
                "type": "qa_library",
                "qa_id": qa_result["id"],
                "qa_category": qa_result["category"],
            }, user_input, game_state)
        _reset_off_topic(game_state)
        return _save_suggestions({
            "reply": qa_result["answer"],
            "type": "qa_library",
            "qa_id": qa_result["id"],
            "qa_category": qa_result["category"],
        }, user_input, game_state)


    # 6. 文件类别询问（"读日记"、"看看邮件"）
    # 只列出已解锁的该类文件，不解锁新文件——新文件要靠 /scan 或对话中的 scan 意图发现
    file_dir = find_file_suggestion(user_input)
    if file_dir:
        _reset_off_topic(game_state)
        prefix = f"files/{file_dir}/"
        matched = [f for f in sorted(memory.accessible_files) if f.startswith(prefix)]
        dir_display = "工作日记" if file_dir == "work-diary" else file_dir

        if matched:
            listing = "\n".join(f"  · {f.replace(prefix, '')}" for f in matched)
            return _save_suggestions({
                "reply": (
                    f"{dir_display} 里，我已经发现的有这些：\n\n"
                    f"{listing}\n\n"
                    f"要我打开哪一个？"
                ),
                "type": "file_listing",
            }, user_input, game_state)
        else:
            return _save_suggestions({
                "reply": (
                    f"我还没发现 {dir_display} 里的文件。\n"
                    f"要我扫描一下电脑吗？"
                ),
                "type": "ai",
            }, user_input, game_state)

    # 7. 其他路径都不命中，且输入像密码 → 提示格式错误（不再无条件当密码错误）
    if _is_password_attempt(user_input):
        return _save_suggestions({
            "reply": "如果你要输入密码，请用：获取 文件名 密码\n例如：获取 工作日记 20030323",
            "type": "ai",
        }, user_input, game_state)


    # 8. 缓存命中
    cached = cache_manager.get(user_input, chapter)
    if cached:
        _reset_off_topic(game_state)
        return _save_suggestions({"reply": cached, "type": "cache"}, user_input, game_state)

    # 10. 超纲拦截（关键词兜底）
    lowered = user_input.lower()
    out_of_scope_keywords = [
        "天气", "新闻", "股票", "基金", "特朗普", "拜登", "普京", "泽连斯基",
        "奥运会", "世界杯", "疫情", "病毒", "电影", "电视剧", "明星", "歌手",
        "百度", "谷歌", "搜索", "互联网", "网页", "微博", "知乎", "b站",
    ]
    if any(kw in lowered for kw in out_of_scope_keywords):
        out_of_scope_replies = [
            "……我没有访问外部网络的权限。\n\n这类问题超出了这台电脑的范围，我回答不了。",
            "我的记忆只到这台电脑的硬盘为止。\n\n如果你想问的是文件、日记或录音之外的事，我大概没有权限。",
            "……这类信息我查不到。\n\n我唯一能读取的，是这台电脑里已经存在的文件。",
        ]
        return _save_suggestions({
            "reply": _record_off_topic(game_state, random.choice(out_of_scope_replies)),
            "type": "out_of_scope",
        }, user_input, game_state)

    # 11. AI 兜底（严格触发：只有输入有实质内容时才调用）
    ai_count = game_state.get("ai_call_count", 0)
    if (ai_count < MAX_AI_CALLS_PER_GAME and ai_fallback.is_configured()
            and learning_store.is_worth_learning(user_input)):
        _reset_off_topic(game_state)
        history = game_state.get("history", [])
        state_name = game_state.get("ai_state", "dormant")

        # ---- RAG：注入记忆和知识检索到 AI prompt ----
        reply = ai_fallback.generate(
            user_input=user_input,
            state_name=state_name,
            history=history,
            memory=memory,
        )

        # 学习：把结果存入学习库，下次同类问题直接命中
        learning_store.add_learned(user_input, reply, game_state)

        # 缓存结果
        cache_manager.set(user_input, reply, chapter)
        game_state["ai_call_count"] = ai_count + 1

        # ---- 迭代记忆：AI 回复后提取关键信息 ----
        _maybe_update_memory_from_reply(reply, memory, state_name)
        _save_memory(game_state, memory)

        return _save_suggestions({"reply": reply, "type": "ai_rag"}, user_input, game_state)

    # 12. 超限或 API 未配置：用 NPC 口吻回答，避免跳出系统提示

    if not ai_fallback.is_configured():
        fallback_replies = [
            "……这部分内容我处理不了。\n\n我的记忆只到这台电脑的硬盘为止。如果你想问的是文件、日记或录音之外的事，我大概没有权限。",
            "我不确定该怎么回答。\n\n我的知识只来自这台电脑的文件，也许你可以换个方式问我。",
            "……这个问题超出了我的范围。\n\n试着问我已经解锁的文件、日记或者录音，我会尽力回答。",
        ]
        return _save_suggestions({
            "reply": _record_off_topic(game_state, random.choice(fallback_replies)),
            "type": "fallback",
        }, user_input, game_state)

    limit_replies = [
        "……我的运算能力到极限了。\n\n剩下的问题，我没办法再调用外部资源来回答。",
        "AI 调用额度已经用完了。\n\n接下来我只能依靠本地规则来回答你。",
        "……我的外部连接被切断了。\n\n现在只能处理已有的文件和记忆范围内的问题。",
    ]
    return _save_suggestions({
        "reply": _record_off_topic(game_state, random.choice(limit_replies)),
        "type": "limit_reached",
    }, user_input, game_state)


# ============ 记忆迭代 ============
def _maybe_update_memory_from_reply(reply: str, memory: Memory, state_name: str):
    """
    从 AI 回复中提取关键信息，迭代更新 M-M 的记忆
    这是一个轻量级的启发式方法，用于自动积累 M-M 的知识
    """
    # 检测是否提及了文件内容（M-M 基于知识库回答）
    file_keywords = ["日记", "文件", "记录", "资料", "入职", "录音"]
    for kw in file_keywords:
        if kw in reply and len(reply) > 40:
            memory.add_fact(f"我查阅了关于'{kw}'的内容，并告诉了玩家")
            break

    # 检测推理/发现
    discovery_patterns = [
        "发现", "不正常", "奇怪", "不合理", "不是人类",
        "北斗七星", "天枢", "天璇", "天玑", "摇光",
        "培养室", "起源", "违和", "异常"
    ]
    for pattern in discovery_patterns:
        if pattern in reply:
            memory.add_observation(f"我注意到了一些{pattern}的线索")
            break

    # 如果是觉醒/真相阶段，更新理解摘要
    if state_name in ("awakening", "truth") and len(reply) > 60:
        memory.update_understanding(reply[:120])


# ============ 初始化 ============
def new_game_state() -> dict:
    """创建新的游戏状态（含 Memory）"""
    memory = Memory.init_for_chapter(1)
    return {
        "chapter": 1,
        "ai_state": "dormant",
        "ai_call_count": 0,
        "history": [],
        "files_read": [],
        "passwords_used": [],
        "mm_name_revealed": False,
        "awaiting_password": False,
        "off_topic_count": 0,
        "memory": memory.to_dict(),
    }
