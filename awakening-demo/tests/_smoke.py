import sys
sys.path.insert(0, '.')
from engine import hybrid_reply, cache_manager
cache_manager.clear()

# 模拟截图里那 3 个问题（ch=1）
gs = hybrid_reply.new_game_state()
tests = [
    '你的主人是谁',
    '你想念她吗',
    '你觉得她是怎样的人',
    '今天天气怎么样',
    '你能为我做些什么',
    '你好',
    '看看线索',
    '你能做什么',
    '我现在该做什么',
]
for q in tests:
    r = hybrid_reply.generate_reply(q, gs)
    gs = r.get('game_state', gs)
    print(f'Q: {q}')
    print(f'  type={r.get("type")} entry={r.get("entry_id", "")}')
    print(f'  reply: {r.get("reply", "")[:100]}')
    print()
