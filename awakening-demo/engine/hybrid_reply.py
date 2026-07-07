"""
hybrid_reply.py - 混合回复核心
整合规则、缓存、AI、密码等所有回复路径
"""
import json
from pathlib import Path

from engine import ai_fallback, cache_manager, character_state
from engine.rule_engine import match_keyword_template, find_file_suggestion
from engine.file_reader import (
    read_knowledge_file,
    list_files,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRIGGERS_DIR = PROJECT_ROOT / "knowledge" / "triggers"
PASSWORD_FILE = TRIGGERS_DIR / "passwords.json"

# AI调用上限
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


def _check_password(user_input: str) -> dict | None:
    """检测玩家输入是否为密码"""
    passwords = _load_passwords()
    user_clean = user_input.strip().lower()

    for pwd, config in passwords.items():
        if pwd.lower() == user_clean:
            return {"password": pwd, "config": config}
    return None


# ============ 状态切换 ============
def _transition_state(game_state: dict, new_state: str) -> dict:
    """切换AI状态"""
    game_state["ai_state"] = new_state
    return game_state


# ============ 文件读取 ============
def handle_file_command(command: str, game_state: dict) -> dict:
    """
    处理 /read 命令
    """
    parts = command.strip().split(maxsplit=1)
    if len(parts) < 2:
        return {
            "reply": "用法：/read [文件名]，例如 /read welcome.txt",
            "type": "command",
        }

    filename = parts[1].strip()
    # 补全路径
    if "/" not in filename:
        filename = f"files/{filename}"

    content = read_knowledge_file(filename)
    if content is None:
        return {
            "reply": f"找不到文件：{filename}",
            "type": "command",
        }

    return {
        "reply": f"── {filename} ──\n\n{content}",
        "type": "file_read",
        "file": filename,
    }


def handle_list_command(sub_dir: str | None, game_state: dict) -> dict:
    """处理 /ls 或 /files 命令"""
    sub = sub_dir or "files"
    files = list_files(sub)
    if not files:
        return {"reply": f"{sub}/ 目录下没有文件", "type": "command"}
    listing = "\n".join(f"  {f}" for f in files)
    return {
        "reply": f"── {sub}/ ──\n\n{listing}",
        "type": "command",
    }


# ============ 玩家命令处理 ============
def handle_command(user_input: str, game_state: dict) -> dict:
    """
    处理 / 开头的命令
    """
    parts = user_input.strip().split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd == "/help":
        return {
            "reply": (
                "── 可用命令 ──\n"
                "  /help           显示帮助\n"
                "  /status         查看AI状态\n"
                "  /files          列出可访问文件\n"
                "  /read [文件名]  读取文件\n"
                "  /chapter        查看章节进度\n"
                "  /hint           获得当前章节提示\n"
                "  /reset          重新开始\n"
            ),
            "type": "command",
        }

    if cmd == "/status":
        return {
            "reply": (
                f"── 状态 ──\n"
                f"  章节: {game_state.get('chapter', 1)}\n"
                f"  AI状态: {character_state.get_state(game_state.get('ai_state', 'dormant'))['name']}\n"
                f"  AI调用: {game_state.get('ai_call_count', 0)}/{MAX_AI_CALLS_PER_GAME}\n"
            ),
            "type": "command",
        }

    if cmd in ("/files", "/ls"):
        return handle_list_command("files", game_state)

    if cmd == "/read":
        return handle_file_command(user_input, game_state)

    if cmd == "/chapter":
        chapter = game_state.get("chapter", 1)
        state_name = game_state.get("ai_state", "dormant")
        return {
            "reply": f"当前在第 {chapter} 章，AI状态：{character_state.get_state(state_name)['name']}",
            "type": "command",
        }

    if cmd == "/reset":
        cache_manager.clear()
        return {
            "reply": "游戏已重置。",
            "type": "command",
            "reset": True,
        }

    if cmd == "/hint":
        return {
            "reply": "[FILL:章节提示 - 后续在GDD/05-flow.md填写]",
            "type": "command",
        }

    return {"reply": f"未知命令：{cmd}。输入 /help 查看可用命令。", "type": "command"}


# ============ 核心：混合回复 ============
def generate_reply(user_input: str, game_state: dict) -> dict:
    """
    混合模式核心：决定走哪条路径生成回复
    """
    user_input = user_input.strip()
    if not user_input:
        return {"reply": "...", "type": "empty"}

    # 1. 玩家命令（/开头）
    if user_input.startswith("/"):
        return handle_command(user_input, game_state)

    # 2. 密码匹配
    pwd_result = _check_password(user_input)
    if pwd_result:
        new_chapter = pwd_result["config"].get("chapter")
        new_state = pwd_result["config"].get("next_state")
        if new_chapter:
            game_state["chapter"] = new_chapter
        if new_state:
            game_state["ai_state"] = new_state
        return {
            "reply": (
                f"……\n\n"
                f"[密码 '{pwd_result['password']}' 被识别]\n"
                f"[系统响应：{pwd_result['config'].get('hint', '权限已解锁')}]\n\n"
                f"……"
            ),
            "type": "password",
            "unlock": pwd_result["config"].get("unlocks", []),
        }

    # 3. 关键词模板
    chapter = game_state.get("chapter", 1)
    template_reply = match_keyword_template(user_input, chapter)
    if template_reply:
        return {"reply": template_reply, "type": "rule_template"}

    # 4. 文件建议检测（玩家要求查看某类文件）
    file_dir = find_file_suggestion(user_input)
    if file_dir:
        files = list_files(f"files/{file_dir}")
        if files:
            listing = "\n".join(f"  {f}" for f in files)
            return {
                "reply": (
                    f"我在 {file_dir}/ 目录下找到这些文件：\n\n"
                    f"{listing}\n\n"
                    f"输入 `/read {files[0]}` 可以查看第一封。"
                ),
                "type": "file_listing",
            }

    # 5. 缓存命中
    cached = cache_manager.get(user_input, chapter)
    if cached:
        return {"reply": cached, "type": "cache"}

    # 6. AI兜底（限制次数）
    ai_count = game_state.get("ai_call_count", 0)
    if ai_count < MAX_AI_CALLS_PER_GAME and ai_fallback.is_configured():
        history = game_state.get("history", [])
        state_name = game_state.get("ai_state", "dormant")
        reply = ai_fallback.generate(user_input, state_name, history)
        cache_manager.set(user_input, reply, chapter)
        game_state["ai_call_count"] = ai_count + 1
        return {"reply": reply, "type": "ai"}

    # 7. 超限或API未配置
    if not ai_fallback.is_configured():
        return {
            "reply": "（系统提示：AI未配置，规则模板未命中。请设置 DASHSCOPE_API_KEY 环境变量）",
            "type": "fallback",
        }

    return {
        "reply": "……（已达到AI调用上限，本局剩余对话将使用规则模板，请节约提问）",
        "type": "limit_reached",
    }


# ============ 初始化 ============
def new_game_state() -> dict:
    """创建新的游戏状态"""
    return {
        "chapter": 1,
        "ai_state": "dormant",
        "ai_call_count": 0,
        "history": [],
        "files_read": [],
        "passwords_used": [],
    }
