"""
CLI 测试脚本 - 验证响应库、密码系统、章节流转
不依赖 Flask，直接调用 hybrid_reply.generate_reply
"""
import sys
import json
from pathlib import Path

# 添加引擎路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine import hybrid_reply, cache_manager


def color(text: str, code: str) -> str:
    colors = {"green": "92", "red": "91", "yellow": "93", "blue": "94", "cyan": "96", "bold": "1"}
    return f"\033[{colors.get(code, '0')}m{text}\033[0m"


def test_case(name: str, inputs: list, chapter_hint: int = 1):
    """运行一组测试，每条输入对应一次 generate_reply"""
    print(f"\n{'=' * 60}")
    print(f"  {color(name, 'cyan')}")
    print(f"{'=' * 60}")

    gs = hybrid_reply.new_game_state()
    # 章节作弊
    if chapter_hint > 1:
        gs["chapter"] = chapter_hint
    gs.setdefault("files_read", [])

    results = []
    for i, user_input in enumerate(inputs, 1):
        result = hybrid_reply.generate_reply(user_input, gs)
        gs = result.get("game_state", gs)

        entry_id = result.get("entry_id", "")
        category = result.get("category", "")
        rtype = result.get("type", "???")
        score = result.get("score", None)
        reply = result.get("reply", "")

        # 格式化输出
        tag = f"[{rtype}]"
        if score is not None:
            tag += f" score={score}"
        if entry_id:
            tag += f" id={entry_id}"
        if category:
            tag += f" cat={category}"

        reply_preview = reply.replace("\n", "\\n")[:100]

        print(f"\n  {color(f'[{i}]', 'yellow')} 玩家: {user_input[:60]}")
        print(f"      {color(tag, 'blue')}")
        print(f"      → {reply_preview}...")

        results.append({
            "input": user_input,
            "type": rtype,
            "score": score,
            "entry_id": entry_id,
            "category": category,
            "chapter": gs.get("chapter", 1),
            "ai_state": gs.get("ai_state", "dormant"),
        })

    return results


def summary(results: list, test_name: str):
    """统计结果"""
    total = len(results)
    lib_hits = sum(1 for r in results if r["type"] == "response_library")
    intent_hits = sum(1 for r in results if r["type"] in ("ai", "file_read", "file_listing"))
    other = total - lib_hits - intent_hits

    print(f"\n  ── {test_name} 统计 ──")
    print(f"  总输入: {total}")
    pct = lib_hits * 100 // max(total, 1)
    print(f"  响应库命中: {color(str(lib_hits), 'green')}/{total} ({pct}%)")
    print(f"  意图引擎: {intent_hits}")
    print(f"  其他路径: {other}")
    return lib_hits, total


# ============================================
# 测试套件
# ============================================

def test_ch1_basics():
    """第1章：基础对话，响应库应覆盖本体身份、问候、帮助"""
    return test_case("第1章 - 基础对话", [
        "你是谁？",
        "你好",
        "你能做什么？",
        "你叫什么名字？",
        "帮我",
        "你是谁，你是机器人吗？",
        "你在哪里？",
        "你现在是什么感觉？",
    ])


def test_ch1_file_ops():
    """第1章：文件相关指令"""
    return test_case("第1章 - 文件操作", [
        "/files",
        "看看文件",
        "打开 todolist",
        "看看邮件",
        "有什么文件",
        "读一下入职资料",
        "打开 todolist.txt",
    ])


def test_ch2_diary():
    """第2章：工作日记相关对话"""
    return test_case("第2章 - 工作日记", [
        "打开第一篇工作日记",
        "你感觉张知予是什么样的人？",
        "张知予为什么要写日记？",
        "林璇是谁？",
        "林璇和张知予什么关系？",
        "这个日记有点奇怪",
        "你觉得林璇正常吗？",
    ], chapter_hint=2)


def test_passwords():
    """密码系统测试"""
    return test_case("密码系统", [
        "alpha-7",
        "X-7-final",
        "输入密码看看",
        "密码是什么",
        "密码提示",
        "20030323",
    ])


def test_ch3_private_anomaly():
    """第3章：私人文件夹 + 异常观察"""
    return test_case("第3章 - 私人文件夹", [
        "扫描私人文件夹",
        "打开 异常观察记录",
        "这些异常是什么意思？",
        "张知予发现了什么？",
        "北斗七星是什么意思？",
        "天枢是什么？",
        "这是什么培养室？",
    ], chapter_hint=3)


def test_ch4_recordings():
    """第4章：录音"""
    return test_case("第4章 - 录音", [
        "扫描公司服务器",
        "听听全员会议",
        "林璇和陈玑说了什么？",
        "陆天枢是什么人？",
        "起源计划是什么？",
    ], chapter_hint=4)


def test_ch6_ending():
    """第6章：终局"""
    return test_case("第6章 - 终局", [
        "未命名文档写了什么？",
        "张知予还活着吗？",
        "我该怎么办？",
        "我选择发出去",
        "我选择删除",
    ], chapter_hint=6)


def test_edge_cases():
    """边界测试"""
    return test_case("边界测试 - 无关问题", [
        "",
        "天气怎么样？",
        "特朗普是谁？",
        "百度搜索一下",
        "你叫什么名字呀小可爱？",
        "现在是几点？",
    ])


def test_response_variety():
    """验证变体不重复"""
    print(f"\n{'=' * 60}")
    print(f"  {color('变体重读测试', 'cyan')}")
    print(f"{'=' * 60}")

    gs = hybrid_reply.new_game_state()
    replies = []
    for _ in range(5):
        result = hybrid_reply.generate_reply("你是谁？", gs)
        gs = result.get("game_state", gs)
        reply = result.get("reply", "")
        replies.append(reply[:60])
        print(f"  [{len(replies)}] {reply[:80]}...")

    unique = len(set(replies))
    print(f"\n  唯一变体: {color(str(unique), 'green' if unique >= 3 else 'red')}/5")
    return [] if unique >= 2 else [{"input": "你是谁？x5", "type": "ERROR", "score": 0}]


# ============================================
# 主入口
# ============================================
if __name__ == "__main__":
    cache_manager.clear()

    all_tests = [
        ("第1章-基础对话", test_ch1_basics),
        ("第1章-文件操作", test_ch1_file_ops),
        ("第2章-工作日记", test_ch2_diary),
        ("密码系统", test_passwords),
        ("第3章-私人文件夹", test_ch3_private_anomaly),
        ("第4章-录音", test_ch4_recordings),
        ("第6章-终局", test_ch6_ending),
        ("边界测试", test_edge_cases),
    ]

    total_lib = 0
    total_all = 0

    for name, test_func in all_tests:
        print(f"\n... 运行 {name}")
        try:
            res = test_func()
            lib, all = summary(res, name)
            total_lib += lib
            total_all += all
        except Exception as e:
            print(f"  {color(f'[ERR] 异常: {e}', 'red')}")

    # 变体测试
    try:
        test_response_variety()
    except Exception as e:
        print(f"  {color(f'变体测试异常: {e}', 'red')}")

    # 总览
    rate = total_lib * 100 // max(total_all, 1)
    print(f"\n{'=' * 60}")
    print(f"  {color('全局统计', 'bold')}")
    print(f"{'=' * 60}")
    print(f"  总测试数: {total_all}")
    print(f"  响应库命中: {color(str(total_lib), 'green')} ({rate}%)")
    print(f"  无 API 调用: {color('[OK]' if rate >= 60 else '[WARN]', 'green' if rate >= 60 else 'yellow')}")
    print()
