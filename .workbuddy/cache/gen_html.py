# -*- coding: utf-8 -*-
"""Generate a single-file HTML AI daily dashboard from aihot daily JSON."""
import json, html, datetime, os

CACHE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(CACHE, "aihot_daily.json")
OUT_DIR = r"D:/_WorkFile/_Daily/Ai_test"
os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC, "r", encoding="utf-8") as f:
    d = json.load(f)

# ---- meta ----
date_str = d.get("date", "")            # 2026-06-25
gen_iso = d.get("generatedAt", "")      # 2026-06-25T00:00:08.479Z
ws_iso = d.get("windowStart", "")
we_iso = d.get("windowEnd", "")

def beijing_human(iso):
    """ISO UTC -> Beijing time human string."""
    if not iso:
        return ""
    try:
        t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        bj = t.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        h = bj.hour
        if 0 <= h < 6:
            period = "凌晨"
        elif 6 <= h < 12:
            period = "上午"
        elif 12 <= h < 14:
            period = "中午"
        elif 14 <= h < 18:
            period = "下午"
        else:
            period = "晚上"
        hh = h if h <= 12 else h - 12
        if hh == 0:
            hh = 12
        return f"{bj.month}月{bj.day}日 {period} {hh:02d}:{bj.minute:02d}"
    except Exception:
        return ""

def beijing_short(iso):
    if not iso:
        return ""
    try:
        t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        bj = t.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        return f"{bj.year}年{bj.month}月{bj.day}日"
    except Exception:
        return ""

def weekday_cn(date_str):
    try:
        t = datetime.date.fromisoformat(date_str)
        names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return names[t.weekday()]
    except Exception:
        return ""

# hero date
hero_date = beijing_short(gen_iso or (date_str + "T00:00:00Z"))
hero_weekday = weekday_cn(date_str)
hero_gen = beijing_human(gen_iso)
win_start = beijing_human(ws_iso)
win_end = beijing_human(we_iso)

# ---- sections (fixed order) ----
FIXED_ORDER = ["模型发布/更新", "产品发布/更新", "行业动态", "论文研究", "技巧与观点"]
SECTION_META = {
    "模型发布/更新": {"icon": "🧠", "color": "#6366f1", "slug": "models"},
    "产品发布/更新": {"icon": "🚀", "color": "#0ea5e9", "slug": "products"},
    "行业动态":     {"icon": "📊", "color": "#f59e0b", "slug": "industry"},
    "论文研究":     {"icon": "📄", "color": "#10b981", "slug": "papers"},
    "技巧与观点":   {"icon": "💡", "color": "#ec4899", "slug": "tips"},
}

# reorder sections to fixed order, append any unexpected at end
sec_map = {s["label"]: s for s in d.get("sections", [])}
sections = []
for label in FIXED_ORDER:
    if label in sec_map:
        sections.append(sec_map.pop(label))
for s in sec_map.values():  # any leftover
    sections.append(s)

# global continuous numbering
total = 0
all_sections = []
for s in sections:
    items = s.get("items", [])
    numbered = []
    for it in items:
        total += 1
        numbered.append((total, it))
    all_sections.append((s["label"], numbered))

def trunc_summary(text, limit=60):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"

def esc(s):
    return html.escape(s or "", quote=True)

# ---- build cards html ----
cards_html_parts = []
nav_parts = []
stat_parts = []
for label, numbered in all_sections:
    meta = SECTION_META.get(label, {"icon": "📌", "color": "#64748b", "slug": "other"})
    slug = meta["slug"]
    color = meta["color"]
    icon = meta["icon"]
    cnt = len(numbered)
    # nav
    nav_parts.append(
        f'<a class="nav-link" href="#{slug}" style="--c:{color}">'
        f'<span class="nav-ico">{icon}</span>'
        f'<span class="nav-txt">{esc(label)}</span>'
        f'<span class="nav-cnt">{cnt}</span></a>'
    )
    # stat
    stat_parts.append(
        f'<a class="stat-chip" href="#{slug}" style="--c:{color}">'
        f'<div class="stat-ico">{icon}</div>'
        f'<div class="stat-meta"><div class="stat-num">{cnt}</div>'
        f'<div class="stat-label">{esc(label)}</div></div></a>'
    )
    # section header + cards
    cards_html_parts.append(
        f'<section class="section" id="{slug}">'
        f'<div class="sec-head" style="--c:{color}">'
        f'<span class="sec-ico">{icon}</span>'
        f'<h2 class="sec-title">{esc(label)}</h2>'
        f'<span class="sec-count">{cnt} 条</span>'
        f'<a class="sec-top" href="#top" title="回到顶部">↑</a>'
        f'</div><div class="card-grid">'
    )
    for num, it in numbered:
        title = esc(it.get("title", ""))
        summ = esc(trunc_summary(it.get("summary", ""), 60))
        src_name = esc(it.get("sourceName", "来源"))
        url = esc(it.get("sourceUrl", "#"))
        cards_html_parts.append(
            f'<article class="card" style="--c:{color}">'
            f'<div class="card-top">'
            f'<span class="card-num">{num}</span>'
            f'<span class="card-src" title="{src_name}">{src_name}</span>'
            f'</div>'
            f'<h3 class="card-title">{title}</h3>'
            f'<p class="card-summary">{summ}</p>'
            f'<a class="card-link" href="{url}" target="_blank" rel="noopener noreferrer">'
            f'阅读原文 <span class="arrow">↗</span></a>'
            f'</article>'
        )
    cards_html_parts.append("</div></section>")

nav_html = "".join(nav_parts)
stat_html = "".join(stat_parts)
body_html = "".join(cards_html_parts)
total_str = str(total)

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 晨报 · {hero_date} {hero_weekday}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --bg:#f6f7fb; --card:#ffffff; --ink:#0f172a; --sub:#64748b;
  --line:#e6e8ef; --accent:#6366f1; --shadow:0 1px 3px rgba(15,23,42,.06),0 4px 16px rgba(15,23,42,.05);
}}
html{{scroll-behavior:smooth}}
body{{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.6;
  -webkit-font-smoothing:antialiased;
}}
a{{text-decoration:none;color:inherit}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 20px}}

/* hero */
.hero{{
  background:linear-gradient(135deg,#1e1b4b 0%,#4338ca 55%,#6d28d9 100%);
  color:#fff;padding:34px 0 26px;position:relative;overflow:hidden;
}}
.hero::after{{
  content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;
  background:radial-gradient(circle,rgba(255,255,255,.14),transparent 70%);
}}
.hero-inner{{position:relative;z-index:1}}
.hero-tag{{display:inline-flex;align-items:center;gap:6px;font-size:12px;
  background:rgba(255,255,255,.18);padding:4px 12px;border-radius:999px;margin-bottom:12px;
  letter-spacing:.5px}}
.hero-tag .dot{{width:7px;height:7px;border-radius:50%;background:#34d399;box-shadow:0 0 8px #34d399}}
.hero h1{{font-size:26px;font-weight:800;letter-spacing:-.5px}}
.hero-date{{font-size:15px;opacity:.92;margin-top:5px}}
.hero-win{{font-size:12.5px;opacity:.78;margin-top:4px}}
.hero-total{{
  display:flex;align-items:baseline;gap:8px;margin-top:16px;
}}
.hero-total .big{{font-size:34px;font-weight:800;line-height:1}}
.hero-total .lbl{{font-size:13px;opacity:.85}}

/* stats */
.stats{{
  display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:18px;
}}
.stat-chip{{
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);
  border-radius:12px;padding:11px 12px;display:flex;align-items:center;gap:9px;
  transition:background .2s,transform .2s;
}}
.stat-chip:hover{{background:rgba(255,255,255,.22);transform:translateY(-2px)}}
.stat-ico{{font-size:18px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;
  background:rgba(255,255,255,.18);border-radius:8px;flex-shrink:0}}
.stat-num{{font-size:19px;font-weight:700;line-height:1.1}}
.stat-label{{font-size:11px;opacity:.85;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}

/* nav */
.nav{{
  position:sticky;top:0;z-index:50;background:rgba(255,255,255,.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
  box-shadow:0 1px 0 rgba(15,23,42,.03);
}}
.nav-inner{{display:flex;gap:6px;overflow-x:auto;padding:10px 20px;max-width:1100px;margin:0 auto;
  scrollbar-width:none}}
.nav-inner::-webkit-scrollbar{{display:none}}
.nav-link{{
  display:inline-flex;align-items:center;gap:6px;white-space:nowrap;
  padding:7px 13px;border-radius:999px;font-size:13px;font-weight:500;color:var(--sub);
  border:1px solid transparent;transition:all .18s;
}}
.nav-link:hover{{background:#f1f0fb;color:var(--ink);border-color:var(--line)}}
.nav-link.active{{background:color-mix(in srgb,var(--c) 12%,transparent);color:var(--c);border-color:color-mix(in srgb,var(--c) 30%,transparent)}}
.nav-ico{{font-size:14px}}
.nav-cnt{{font-size:11px;background:#eef0f5;color:var(--sub);padding:1px 7px;border-radius:999px;font-weight:600}}
.nav-link.active .nav-cnt{{background:var(--c);color:#fff}}

/* sections */
.main{{padding:24px 0 40px}}
.section{{margin-bottom:30px;scroll-margin-top:64px}}
.sec-head{{display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:10px;
  border-bottom:2px solid color-mix(in srgb,var(--c) 22%,transparent)}}
.sec-ico{{font-size:20px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;
  background:color-mix(in srgb,var(--c) 14%,#fff);border-radius:9px}}
.sec-title{{font-size:18px;font-weight:700;color:var(--ink)}}
.sec-count{{font-size:12px;color:var(--c);background:color-mix(in srgb,var(--c) 12%,#fff);
  padding:3px 10px;border-radius:999px;font-weight:600}}
.sec-top{{margin-left:auto;font-size:13px;color:var(--sub);width:26px;height:26px;
  display:flex;align-items:center;justify-content:center;border-radius:7px;border:1px solid var(--line);transition:all .15s}}
.sec-top:hover{{color:var(--c);border-color:var(--c);background:#fff}}

/* card grid */
.card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
.card{{
  background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 16px 14px;
  display:flex;flex-direction:column;position:relative;transition:transform .18s,box-shadow .18s,border-color .18s;
  box-shadow:var(--shadow);
}}
.card::before{{content:"";position:absolute;left:0;top:14px;bottom:14px;width:3px;
  background:var(--c);border-radius:0 3px 3px 0;opacity:.85}}
.card:hover{{transform:translateY(-3px);box-shadow:0 6px 24px rgba(15,23,42,.1);border-color:color-mix(in srgb,var(--c) 40%,var(--line))}}
.card-top{{display:flex;align-items:center;gap:8px;margin-bottom:9px}}
.card-num{{
  font-size:12px;font-weight:700;color:#fff;background:var(--c);
  min-width:24px;height:24px;padding:0 6px;border-radius:7px;display:flex;align-items:center;justify-content:center;flex-shrink:0
}}
.card-src{{
  font-size:11px;color:var(--sub);background:#f4f5f9;padding:3px 9px;border-radius:999px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;
}}
.card-title{{font-size:14.5px;font-weight:600;line-height:1.45;margin-bottom:7px;color:var(--ink)}}
.card-summary{{font-size:13px;color:var(--sub);line-height:1.6;flex:1;margin-bottom:11px}}
.card-link{{
  font-size:12.5px;font-weight:600;color:var(--c);display:inline-flex;align-items:center;gap:4px;
  align-self:flex-start;padding:4px 0;transition:gap .15s;
}}
.card-link:hover{{gap:7px}}
.card-link .arrow{{font-size:14px}}

/* footer */
.footer{{text-align:center;padding:28px 20px 36px;color:var(--sub);font-size:12.5px;border-top:1px solid var(--line);background:#fff}}
.footer .f-total{{font-size:15px;font-weight:700;color:var(--ink);margin-bottom:5px}}
.footer a{{color:var(--accent)}}

/* responsive */
@media (max-width:760px){{
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .hero h1{{font-size:22px}}
  .hero-total .big{{font-size:28px}}
  .card-grid{{grid-template-columns:1fr}}
}}
@media (max-width:420px){{
  .stats{{grid-template-columns:1fr 1fr}}
}}
</style>
</head>
<body>
<div id="top"></div>

<header class="hero">
  <div class="wrap hero-inner">
    <div class="hero-tag"><span class="dot"></span> AI 晨报仪表盘 · 每日自动聚合</div>
    <h1>AI HOT 日报</h1>
    <div class="hero-date">{hero_date} {hero_weekday} · {hero_gen} 生成（北京时间）</div>
    <div class="hero-win">数据窗口：{win_start} — {win_end}（北京时间，过去 24 小时）</div>
    <div class="hero-total"><span class="big">{total_str}</span><span class="lbl">条精选动态 · 覆盖 5 大版块</span></div>
    <div class="stats">{stat_html}</div>
  </div>
</header>

<nav class="nav">
  <div class="nav-inner">{nav_html}</div>
</nav>

<main class="main">
  <div class="wrap">
    {body_html}
  </div>
</main>

<footer class="footer">
  <div class="f-total">本期共 {total_str} 条 · 5 个版块</div>
  <div>数据源：AI HOT（aihot.virxact.com）· 生成于 {hero_gen}（北京时间）</div>
  <div style="margin-top:4px">本仪表盘为公开资讯聚合，版权归原作者所有</div>
</footer>

<script>
// active nav highlight on scroll
(function(){{
  const links=document.querySelectorAll('.nav-link');
  const secs=[];
  links.forEach(l=>{{const id=l.getAttribute('href').slice(1);const s=document.getElementById(id);if(s)secs.push({{s,link:l}})}});
  const obs=new IntersectionObserver((entries)=>{{
    entries.forEach(e=>{{
      if(e.isIntersecting){{
        links.forEach(x=>x.classList.remove('active'));
        const hit=secs.find(o=>o.s===e.target);
        if(hit)hit.link.classList.add('active');
      }}
    }});
  }},{{rootMargin:'-80px 0px -65% 0px',threshold:0}});
  secs.forEach(o=>obs.observe(o.s));
  // default first active
  if(links[0])links[0].classList.add('active');
}})();
</script>
</body>
</html>
"""

out_path = os.path.join(OUT_DIR, f"ai-daily-{date_str}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print("WROTE:", out_path)
print("TOTAL:", total_str, "items")
