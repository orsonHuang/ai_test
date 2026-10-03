from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
W, H = 2700, 2100
BG = '#f5f3ee'
INK = '#243641'
BLUE = '#45798a'
GOLD = '#ac762a'
GREEN = '#38765e'
RED = '#ad5655'
FONT = 'C:/Windows/Fonts/msyh.ttc'
BOLD = 'C:/Windows/Fonts/msyhbd.ttc'
im = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(im)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="{BG}"/>']

def text(x, y, value, size=32, color=INK, bold=False, align='center'):
    font = ImageFont.truetype(BOLD if bold else FONT, size)
    anchor = 'mm' if align == 'center' else 'lm'
    d.text((x, y), value, font=font, fill=color, anchor=anchor)
    svg.append(f'<text x="{x}" y="{y}" text-anchor="{"middle" if align == "center" else "start"}" dominant-baseline="central" font-family="Microsoft YaHei, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')

def rect(x, y, w, h, fill, stroke=None, radius=20, width=3):
    d.rounded_rectangle((x,y,x+w,y+h), radius=radius, fill=fill, outline=stroke, width=width)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"/>')

def node(x,y,w,h,lines,fill='#ffffff',stroke=BLUE,size=32):
    rect(x,y,w,h,fill,stroke)
    lines = lines.split('\n')
    gap = size * 1.45
    for i,line in enumerate(lines):
        assert d.textlength(line, font=ImageFont.truetype(FONT,size)) <= w-28, line
        text(x+w/2,y+h/2+(i-(len(lines)-1)/2)*gap,line,size,bold=(len(lines)==1))

def diamond(cx,cy,rx,ry,label,size=31):
    pts=[(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)]
    d.polygon(pts,fill='#fff2d9',outline=GOLD,width=3)
    svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="#fff2d9" stroke="{GOLD}" stroke-width="3"/>')
    text(cx,cy,label,size,bold=True)

def arrow(pts,color=BLUE,width=4):
    d.line(pts,fill=color,width=width,joint='curve')
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
    x,y=pts[-1]; px,py=pts[-2]; a=math.atan2(y-py,x-px)
    tri=[(x,y),(x-17*math.cos(a)+8*math.sin(a),y-17*math.sin(a)-8*math.cos(a)),(x-17*math.cos(a)-8*math.sin(a),y-17*math.sin(a)+8*math.cos(a))]
    d.polygon(tri,fill=color)
    svg.append(f'<polygon points="{" ".join(f"{xx},{yy}" for xx,yy in tri)}" fill="{color}"/>')

def badge(x,y,label,color=BLUE):
    d.ellipse((x-27,y-27,x+27,y+27),fill='#ffffff',outline=color,width=3)
    svg.append(f'<circle cx="{x}" cy="{y}" r="27" fill="white" stroke="{color}" stroke-width="3"/>')
    text(x,y,label,30,color,True)

text(100,72,'迷雾远征 · 游戏流程图',62,bold=True,align='left')
text(103,143,'Godot / Steam  ·  全自动回合制战斗  ·  玩法讨论稿',28,'#6a777c',align='left')

for x,w,title,sub in [(65,690,'01  出发与路线规划','先看目标，再决定如何前进'),(850,1000,'02  区域探索循环','有限时段，分配收益与风险'),(1910,725,'03  魔王挑战与局后','整局构筑的最终检验')]:
    rect(x,205,w,1710,'#ffffff','#dcded9',28,2)
    text(x+35,245,title,35,bold=True,align='left')
    text(x+35,286,sub,23,'#758086',align='left')

# Main route: arrows are painted before boxes.
for y1,y2 in [(410,460),(580,640),(740,800),(890,980),(1100,1185)]:
    arrow([(410,y1),(410,y2)])
arrow([(630,1280),(805,1280),(805,370),(945,370)])
text(716,1238,'普通区域',25,BLUE)
arrow([(410,1375),(410,1415),(730,1415),(730,1840),(1865,1840),(1865,370),(1980,370)],GOLD,5)
rect(880,1813,480,55,'#fff7e7',None,12)
text(1120,1840,'进入魔王城：最终挑战',29,GOLD,True)

# Region loop.
arrow([(1300,430),(1300,490)])
arrow([(1300,690),(1300,760)])
text(1345,725,'是',25,GREEN)
arrow([(1065,590),(922,590)])
text(983,537,'用尽／主动离开',24,BLUE)
arrow([(1300,905),(1300,970)])
arrow([(1110,1050),(1055,1050),(1055,1190)])
text(1030,1124,'否',25,BLUE)
arrow([(1490,1050),(1500,1050),(1500,1190)])
text(1544,1118,'是',25,BLUE)
arrow([(1500,1305),(1500,1345)])
arrow([(1055,1320),(940,1320),(940,1712),(1000,1712)])
arrow([(1500,1495),(1500,1580),(1320,1580),(1320,1650)],GREEN)
text(1460,1534,'是',25,GREEN)
arrow([(1645,1420),(1718,1420)],RED)
text(1690,1380,'否',25,RED)
arrow([(1640,1712),(1805,1712),(1805,590),(1535,590)],GREEN,5)
rect(1630,1583,182,54,'#eaf4ec',None,12)
text(1721,1610,'继续探索',28,GREEN,True)

# Finale and outcome.
arrow([(2270,430),(2270,520)],GOLD)
arrow([(2070,610),(2070,790)],GREEN)
text(2020,705,'胜利',25,GREEN)
arrow([(2470,610),(2470,790)],RED)
text(2520,705,'战败',25,RED)
arrow([(2075,880),(2075,1000),(2270,1000),(2270,1100)],GREEN)
arrow([(2475,880),(2475,1000),(2270,1000)],RED)
arrow([(1947,1162),(1980,1162)],RED)
arrow([(2270,1225),(2270,1300)])
arrow([(2270,1425),(2270,1500)])

# Nodes: planning.
node(160,310,500,100,'开始新冒险',fill='#eaf1f3')
node(120,460,580,120,'生成本局地图\n公开部分 Boss 与套装掉落',size=30)
node(160,640,500,100,'选择主角与起手技能',size=32)
node(160,800,500,90,'从新手村出发')
node(150,980,520,120,'选择前进的相邻区域\n不可后退',size=32)
badge(103,1040,'A')
arrow([(130,1040),(150,1040)])
diamond(410,1280,220,95,'进入魔王城？')
rect(113,1470,587,267,'#f5f7f7',None,18)
text(148,1515,'选路与信息',29,bold=True,align='left')
for i,line in enumerate(['从当前区域选择前方相邻区域','相邻迷雾揭开，提供选路信息','Boss 地标与掉落目标提前可见','离开后不能返回原区域']):
    text(148,1565+i*44,line,26,'#596b73',align='left')

# Nodes: regional budget and activities.
node(945,310,740,120,'进入区域，揭开相邻迷雾并确定内容\n获得本区探索时段（示例 6 点）',fill='#eaf1f3',size=30)
diamond(1300,590,235,100,'继续探索？')
text(1300,622,'有可用点数，并选择留下',18,'#85682d')
badge(895,590,'A')
text(947,645,'回到选路',24,BLUE)
node(955,760,730,145,'选择可支付的行动，并扣除时段\n宝藏／事件／休整／招募：1 点\n小怪战：1 点  ·  副本挑战：2 点',size=30)
diamond(1300,1050,190,80,'战斗行动？')
node(905,1190,300,130,'处理非战斗行动\n宝藏／事件\n休整／招募',size=27)
node(1280,1190,440,115,'全自动回合制战斗\n主角＋最多 2 名随从',size=30)
diamond(1500,1420,145,75,'获胜？',30)
badge(1745,1420,'B',RED)
text(1715,1483,'战败结算',23,RED)
node(1000,1650,640,125,'获得奖励并整理构筑\n换装／调整队伍与技能',fill='#edf6ee',stroke=GREEN,size=32)
text(1290,1798,'副本可重复挑战；每次均消耗时段',25,GREEN)

# Nodes: final battle and meta loop.
node(1980,310,580,120,'攻打魔王城\n全自动回合制战斗',fill='#fff4df',stroke=GOLD,size=32)
diamond(2270,610,200,90,'击败魔王？')
node(1940,790,270,90,'本局通关',fill='#edf6ee',stroke=GREEN,size=31)
node(2340,790,270,90,'本局失败',fill='#fbefed',stroke=RED,size=31)
node(1980,1100,580,125,'本局结算\n奖励与冒险记录',size=33)
badge(1920,1162,'B',RED)
node(1980,1300,580,125,'局外解锁（规划）\n扩展职业、技能与装备内容',size=30)
node(2020,1500,500,110,'再次冒险\n返回开始，生成新地图',fill='#eaf1f3',size=30)
rect(1980,1680,580,132,'#f5f7f7',None,18)
text(2015,1724,'图中 A、B 为跨区域连接标记',25,align='left')
text(2015,1768,'同字母表示流程在此处衔接',25,'#596b73',align='left')

text(100,1981,'示意约定：每区 6 点、普通行动 1 点、副本 2 点；仅用于讨论，非最终数值。',28,'#64727a',align='left')
text(100,2030,'当前按“战败结束本局”绘制；撤退、复活与局外奖励细则待定。换装与选路不耗点。',28,'#64727a',align='left')
svg.append('</svg>')
OUT.mkdir(parents=True,exist_ok=True)
im.save(OUT/'game-flow-v1.png')
(OUT/'game-flow-v1.svg').write_text('\n'.join(svg),encoding='utf-8')
print(str(OUT/'game-flow-v1.png'))
print(str(OUT/'game-flow-v1.svg'))
