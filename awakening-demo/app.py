"""
Awakening Demo - Flask 后端
AI对话解谜游戏 - 30分钟单局
"""
import os
import sys
from pathlib import Path

# 设置 HuggingFace 国内镜像，避免首次下载 embedding 模型失败
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, send_from_directory

from engine import hybrid_reply, character_state

app = Flask(__name__, static_folder=".", static_url_path="")

# ====== 预加载 embedding 模型（后台异步，避免阻塞服务启动） ======
print("正在后台加载 embedding 模型...")
try:
    from engine.sentence_matcher import load_model_async

    load_model_async()
    print("embedding 模型后台加载任务已启动")
except Exception as e:
    print(f"embedding 模型后台加载失败: {e}")

# ====== 页面路由 ======
@app.route("/")
def index():
    """主页 - 前端对话界面"""
    return send_from_directory(".", "index.html")


# ====== API路由 ======
@app.route("/api/chat", methods=["POST"])
def chat():
    """核心对话API"""
    data = request.get_json(force=True, silent=True) or {}
    user_input = data.get("user_input", "").strip()
    game_state = data.get("game_state") or hybrid_reply.new_game_state()

    if not user_input:
        return jsonify({"error": "user_input 不能为空"}), 400

    # 模型尚未加载完成时给出友好提示
    from engine.sentence_matcher import get_load_status

    model_status = get_load_status()
    if not model_status.get("loaded"):
        msg = model_status.get("message", "模型加载中...")
        progress = model_status.get("progress", 0)
        return jsonify(
            {
                "reply": f"[系统初始化中] {msg}（{progress}%）\n\n请稍等片刻，助理核心仍在启动。",
                "type": "system",
                "game_state": game_state,
            }
        )

    result = hybrid_reply.generate_reply(user_input, game_state)

    # 更新历史
    if result.get("type") not in ("empty", "command"):
        game_state.setdefault("history", []).append(
            {"role": "user", "content": user_input}
        )
        if result.get("reply"):
            game_state["history"].append(
                {"role": "assistant", "content": result["reply"]}
            )

    return jsonify(
        {
            "reply": result.get("reply", ""),
            "type": result.get("type", "unknown"),
            "game_state": game_state,
            "ai_state": game_state.get("ai_state", "dormant"),
            "chapter": game_state.get("chapter", 1),
            "unlock": result.get("unlock"),
            "file": result.get("file"),
            "file_content": result.get("file_content"),
            "file_list": result.get("file_list"),
            "password_prompt": result.get("password_prompt", False),
            "password_target": result.get("password_target"),
        }
    )


@app.route("/api/status", methods=["GET", "POST"])
def status():
    """查看游戏状态"""
    if request.method == "POST":
        game_state = request.get_json(force=True, silent=True) or {}
    else:
        game_state = hybrid_reply.new_game_state()

    return jsonify(
        {
            "chapter": game_state.get("chapter", 1),
            "ai_state": game_state.get("ai_state", "dormant"),
            "ai_state_name": character_state.get_state(
                game_state.get("ai_state", "dormant")
            )["name"],
            "ai_call_count": game_state.get("ai_call_count", 0),
            "files_read": game_state.get("files_read", []),
        }
    )


@app.route("/api/reset", methods=["POST"])
def reset():
    """重置游戏"""
    from engine import cache_manager

    cache_manager.clear()
    return jsonify(
        {
            "ok": True,
            "game_state": hybrid_reply.new_game_state(),
        }
    )


@app.route("/health")
def health():
    """健康检查"""
    from engine import ai_fallback, cache_manager

    return jsonify(
        {
            "ok": True,
            "ai_configured": ai_fallback.is_configured(),
            "cache": cache_manager.stats(),
        }
    )


@app.route("/api/model-status")
def model_status():
    """embedding 模型加载状态（前端开机进度条用）"""
    from engine.sentence_matcher import get_load_status

    status = get_load_status()
    return jsonify(status)


# ====== 启动 ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("DEBUG", "0") == "1"
    print(f"=== Awakening Demo 启动 ===")
    print(f"端口: {port}")
    print(f"AI配置: {'已配置' if __import__('engine.ai_fallback', fromlist=['is_configured']).is_configured() else '未配置（设置 DEEPSEEK_API_KEY）'}")
    print(f"浏览器打开: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
