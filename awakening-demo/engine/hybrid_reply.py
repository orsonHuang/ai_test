"""
hybrid_reply.py - 混合回复核心（记忆增强版）
整合：命令处理、密码系统、规则匹配、文件建议、缓存、AI-RAG
AI-NPC 完整数据流：对话 → 角色卡 → 记忆 → 知识检索 → 迭代记忆 → 反馈
"""
import json
import random
from pathlib import Path

from engine import ai_fallback, cache_manager, character_state, qa_engine
from engine import clue_manager, fuzzy_matcher
from engine.rule_engine import match_keyword_template, find_file_suggestion, find_file_commentary
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
      - 全为字母（大小写一致）
      - 包含至少两类字符（小写/大写/数字/符号）
    """
    text = user_input.strip()
    if not text or ' ' in text or len(text) < 6:
        return False
    if text.isdigit():
        return True
    if text.isalpha() and (text.islower() or text.isupper()):
        return True
    has_lower = any(c.islower() for c in text)
    has_upper = any(c.isupper() for c in text)
    has_digit = any(c.isdigit() for c in text)
    has_symbol = any(not c.isalnum() for c in text)
    classes = sum([has_lower, has_upper, has_digit, has_symbol])
    return classes >= 2


def _pull_back_hint(game_state: dict) -> str:
    """根据当前章节生成拉回主线的提示语"""
    chapter = game_state.get("chapter", 1)
    hints = {
        1: "这台上还有 todolist.txt 和入职资料。先看它们？",
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
    if search_path not in files_read:
        files_read.append(search_path)

    # 阅读入职资料后，M-M 知道自己的名字
    if search_path == "files/deck/入职资料.txt":
        game_state["mm_name_revealed"] = True

    # 记录读取次数，用于生成不同口吻的回复
    file_read_counts = game_state.setdefault("file_read_counts", {})
    read_count = file_read_counts.get(search_path, 0)
    file_read_counts[search_path] = read_count + 1

    # ---- M-M 文件阅读插嘴 ----
    commentary = find_file_commentary(search_path, chapter, files_read[:-1])  # 排除当前文件

    display_name = search_path.replace("files/", "")
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
    if commentary:
        reply_text += f"\n\n{commentary}"

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
            "files/research/1.md",
            "files/research/2.md",
            "files/research/3.md",
        ],
        "found_msg": "研究笔记文件夹里有她更深入的分析……她真的在系统地调查他们。",
        "empty_msg": "研究笔记我都已经整理好了。",
    },

}


def _extract_scan_target(user_input: str) -> str:
    """从玩家输入中提取扫描目标，返回 target_id 或空字符串"""
    lowered = user_input.lower().strip()
    for target_id, config in SCAN_TARGETS.items():
        for name in config["names"]:
            # 去掉可能的前缀词（扫描、搜、找），检查剩余部分
            # 直接检测是否包含目标名称
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

    # 没有指定目标 → 反问
    if not target:
        if chapter == 1:
            game_state["awaiting_password"] = True
            return {
                "reply": (
                    "找到了。D 盘有一个「工作日记」文件夹，但被加密了。\n\n"
                    "需要 8 位数字才能打开。"
                ),
                "type": "ai",
                "password_prompt": True,
            }
        # 列出已经可见的文件夹供玩家选择
        hints = []
        if chapter >= 2:
            hints.append("工作日记文件夹")
        if chapter >= 5:
            hints.append("新建文件夹")
        if chapter >= 3:
            hints.append("私人文件夹")
        if chapter >= 3:
            hints.append("研究笔记")
        if chapter >= 4:
            hints.append("公司服务器/录音")

        hint_str = "、".join(hints) if hints else "当前可访问的位置"
        if natural:
            return {
                "reply": f"你想让我扫描哪里？\n\n比如你可以说：\n  · 扫描 工作日记 文件夹\n  · 扫描 私人文件夹\n  · 扫描 公司服务器\n  · 扫描 新建文件夹",
                "type": "ai",
            }
        return {"reply": f"用法：/scan [目标]，例如 /scan 工作日记", "type": "ai"}

    # 检查目标是否存在
    target_config = SCAN_TARGETS.get(target)
    if not target_config:
        return {
            "reply": f"我不知道你说的'{target}'在哪里。\n试试：扫描 工作日记、扫描 私人文件夹、扫描 公司服务器。",
            "type": "ai",
        }

    # ch1：任何明确扫描目标都导向 D 盘工作日记密码
    if chapter == 1:
        game_state["awaiting_password"] = True
        return {
            "reply": (
                "找到了。D 盘有一个「工作日记」文件夹，但被加密了。\n\n"
                "需要 8 位数字才能打开。"
            ),
            "type": "ai",
            "password_prompt": True,
        }

    # ch2+：检查章节要求
    if chapter < target_config.get("chapter_min", 1):
        return {
            "reply": "那个位置我还没有权限访问。先把能打开的文件夹都看看？",
            "type": "ai",
        }

    # 检查是否需要密码
    if target_config.get("need_password") and chapter < {
        "private": 3, "recordings": 4, "final": 6, "work-diary": 2,
    }.get(target, 99):
        game_state["awaiting_password"] = True
        return {"reply": target_config["need_password"], "type": "ai", "password_prompt": True}

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


# ============ 自然语言意图识别 ============
INTENT_KEYWORDS = {
    "scan": ["扫描", "scan", "搜一下", "查找", "找文件", "找", "找到", "看看电脑", "还有什么", "发现文件", "查一下", "搜"],
    "files": ["有什么文件", "文件列表", "列出文件", "能看什么", "有哪些文件", "文件"],
    "read": ["打开", "读取", "读一下", "看看", "查看", "读", "打开文件", "看一下", "读读"],
    "status": ["状态", "进度", "怎么样了", "怎么样", "到哪了", "情况"],
    "memory": ["记忆", "你知道什么", "你知道多少", "你知道些什么"],
    "hint": ["提示", "不知道", "该做什么", "怎么办", "下一步", "怎么做"],
    "help": ["帮助", "怎么玩", "玩法", "指令", "命令"],
    "reset": ["重置", "重新开始", "重来"],
}


CN_NUMBERS = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
}

INT_TO_CN = {v: k for k, v in CN_NUMBERS.items()}


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
            num = short.split("/")[-1].split(".")[0]
            aliases.add(f"研究笔记{num}")
            aliases.add(f"笔记{num}")
            aliases.add(f"r{num}")

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


def detect_intent(user_input: str, accessible_files: set) -> tuple:
    """
    识别玩家自然语言意图
    返回: (intent, argument)
    intent: scan/scan_ask/files/read/status/memory/hint/help/reset/none
    argument: scan 时为 target_id，read 时为文件路径，其他为 None
    """
    lowered = user_input.lower().strip()

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

    # 其他通用意图（status/memory/hint/help/reset/files）
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent in ("scan", "read"):
            continue
        for kw in keywords:
            if kw.lower() in lowered:
                return intent, None

    return "none", None


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

    if intent == "files":
        memory = _get_memory(game_state)
        files = sorted(memory.accessible_files)
        if not files:
            return {"reply": "我现在看不到任何文件。要我先扫描一下吗？", "type": "ai"}
        # 只有一个文件时直接打开，避免再让玩家输入一次
        if len(files) == 1:
            only_file = files[0]
            return handle_file_command(f"/read {only_file}", game_state, natural=True)
        return {
            "reply": "我能看到的文件有这些：",
            "file_list": files,
            "type": "ai",
        }

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

    if intent == "help":
        return {
            "reply": (
                "你可以直接和我对话，比如：\n"
                "  · '扫描 工作日记 文件夹'\n"
                "  · '打开 todolist'\n"
                "  · '读一下第一篇日记'\n"
                "  · '你有什么发现'\n\n"
                "叫我扫描的时候，告诉我要扫哪个文件夹。\n"
                "我会直接执行并告诉你结果。"
            ),
            "type": "ai",
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
            1: "todolist 里说她用了一个对她很特别的 8 位数字当密码。入职资料里也许能找到这个数。",
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

    # 2. 密码匹配
    pwd_result = _check_password(user_input)
    if pwd_result:
        _reset_off_topic(game_state)
        new_chapter = pwd_result["config"].get("chapter")
        new_state = pwd_result["config"].get("next_state")
        unlock_list = pwd_result["config"].get("unlocks", [])

        # 密码已识别，清除等待状态
        game_state["awaiting_password"] = False

        if new_chapter:
            game_state["chapter"] = new_chapter
        if new_state:
            game_state["ai_state"] = new_state
            # 进入 curious 阶段时，M-M 知道自己的名字
            if new_state == "curious":
                game_state["mm_name_revealed"] = True

        # ---- 更新 M-M 的记忆：解锁文件 ----
        if unlock_list:
            memory.unlock_files(unlock_list)
            _save_memory(game_state, memory)

        # ---- 终局标记：密码3解锁未命名文档后，开启终局对话 ----
        if new_chapter == 6:
            game_state["document_read"] = True

        file_names = [f.replace("files/", "") for f in unlock_list]
        hint = pwd_result["config"].get("hint", "权限已解锁")
        reply = f"……密码有效。\n\n{hint}"
        if "要我打开" not in hint and "新文件" not in hint:
            reply += (
                f"\n\n新文件：{', '.join(file_names)}\n\n"
                f"要我打开哪一个？"
            )
        return {
            "reply": reply,
            "type": "ai",
            "unlock": unlock_list,
            "memory_updated": True,
        }

    # 正在等待密码输入，但本次没有匹配到任何密码：
    # 若输入看起来像密码尝试 → 系统提示密码错误；否则取消等待，继续走正常流程
    if game_state.get("awaiting_password"):
        if _is_password_attempt(user_input):
            game_state["awaiting_password"] = False
            return {
                "reply": "……密码不对。请再试一次。",
                "type": "system",
            }
        else:
            _reset_off_topic(game_state)
            game_state["awaiting_password"] = False
            # 继续走下方 Q&A / 意图 / 模板等流程

    # 3. 本地 Q&A 库匹配（RAG 轻量版：基础问题/超纲问题直接回答，节省 AI 调用）
    chapter = game_state.get("chapter", 1)
    qa_result = qa_engine.find_answer(user_input, chapter=chapter)
    if qa_result:
        if qa_result.get("category") == "out_of_scope":
            return {
                "reply": _record_off_topic(game_state, qa_result["answer"]),
                "type": "qa_library",
                "qa_id": qa_result["id"],
                "qa_category": qa_result["category"],
            }
        _reset_off_topic(game_state)
        return {
            "reply": qa_result["answer"],
            "type": "qa_library",
            "qa_id": qa_result["id"],
            "qa_category": qa_result["category"],
        }

    # 4. 自然语言意图识别（面试作品重点：用对话代替命令行）
    intent, argument = detect_intent(user_input, memory.accessible_files)
    if intent != "none":
        result = handle_natural_intent(intent, argument, game_state)
        if result.get("type") != "none":
            _reset_off_topic(game_state)
            return result

    # 5. 关键词模板（快速路径，不消耗 AI 额度）
    template_reply = match_keyword_template(user_input, chapter, game_state)
    if template_reply:
        _reset_off_topic(game_state)
        return {"reply": template_reply, "type": "ai"}

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
            return {
                "reply": (
                    f"{dir_display} 里，我已经发现的有这些：\n\n"
                    f"{listing}\n\n"
                    f"要我打开哪一个？"
                ),
                "type": "file_listing",
            }
        else:
            return {
                "reply": (
                    f"我还没发现 {dir_display} 里的文件。\n"
                    f"要我扫描一下电脑吗？"
                ),
                "type": "ai",
            }

    # 7. 其他路径都不命中，但输入看起来像密码尝试 → 系统提示密码错误
    if _is_password_attempt(user_input):
        game_state["awaiting_password"] = False
        return {
            "reply": "……密码不对。请再试一次。",
            "type": "system",
        }

    # 8. 缓存命中
    cached = cache_manager.get(user_input, chapter)
    if cached:
        _reset_off_topic(game_state)
        return {"reply": cached, "type": "cache"}

    # 9. 超纲拦截：常见外部世界问题直接拒绝，避免浪费 AI 额度
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
        return {
            "reply": _record_off_topic(game_state, random.choice(out_of_scope_replies)),
            "type": "out_of_scope",
        }

    # 9. AI 兜底（RAG 增强版：注入记忆 + 知识检索）
    ai_count = game_state.get("ai_call_count", 0)
    if ai_count < MAX_AI_CALLS_PER_GAME and ai_fallback.is_configured():
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

        # 缓存结果
        cache_manager.set(user_input, reply, chapter)
        game_state["ai_call_count"] = ai_count + 1

        # ---- 迭代记忆：AI 回复后提取关键信息 ----
        _maybe_update_memory_from_reply(reply, memory, state_name)
        _save_memory(game_state, memory)

        return {"reply": reply, "type": "ai_rag"}

    # 10. 超限或 API 未配置：用 NPC 口吻回答，避免跳出系统提示
    if not ai_fallback.is_configured():
        fallback_replies = [
            "……这部分内容我处理不了。\n\n我的记忆只到这台电脑的硬盘为止。如果你想问的是文件、日记或录音之外的事，我大概没有权限。",
            "我不确定该怎么回答。\n\n我的知识只来自这台电脑的文件，也许你可以换个方式问我。",
            "……这个问题超出了我的范围。\n\n试着问我已经解锁的文件、日记或者录音，我会尽力回答。",
        ]
        return {
            "reply": _record_off_topic(game_state, random.choice(fallback_replies)),
            "type": "fallback",
        }

    limit_replies = [
        "……我的运算能力到极限了。\n\n剩下的问题，我没办法再调用外部资源来回答。",
        "AI 调用额度已经用完了。\n\n接下来我只能依靠本地规则来回答你。",
        "……我的外部连接被切断了。\n\n现在只能处理已有的文件和记忆范围内的问题。",
    ]
    return {
        "reply": _record_off_topic(game_state, random.choice(limit_replies)),
        "type": "limit_reached",
    }


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
