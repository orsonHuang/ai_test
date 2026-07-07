# Automation Memory — 每日 AI 晨报仪表盘

## 执行历史

| 日期 | 状态 | 数据来源 | 总条数 | 版块分布 | 产出文件 |
|------|------|----------|--------|----------|----------|
| 2026-06-28 | ✅ 成功 | `/api/public/daily/2026-06-28` | 10 | 模型0 / 产品2 / 行业5 / 论文1 / 技巧2 | ai-daily-2026-06-28.html |
| 2026-06-27 | ✅ 成功 | `/api/public/daily/2026-06-27` | 12 | 模型1 / 产品1 / 行业3 / 论文2 / 技巧5 | ai-daily-2026-06-27.html |
| 2026-06-26 | ✅ 成功 | `/api/public/daily/2026-06-26` | 25 | 模型1 / 产品8 / 行业5 / 论文4 / 技巧7 | ai-daily-2026-06-26.html |
| 2026-06-25 | ✅ 成功 | `/api/public/daily/2026-06-25` | 21 | 5版块齐全 | ai-daily-2026-06-25.html |

## 关键参数
- API: `https://aihot.virxact.com/api/public/daily/{YYYY-MM-DD}`
- 必须带浏览器 User-Agent，否则 403
- 生成脚本: `.workbuddy/cache/gen_html.py`
- JSON缓存: `.workbuddy/cache/aihot_daily.json`
- 产出目录: 工作目录根 `ai-daily-{日期}.html`
