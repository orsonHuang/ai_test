#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate PDF from mock interview transcript"""

from fpdf import FPDF
import os

FONT_PATH = "C:/Windows/Fonts/simhei.ttf"

class PDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font("cn", "", FONT_PATH, uni=True)
        self.add_font("cn", "B", FONT_PATH, uni=True)
        self.set_auto_page_break(True, 20)

    def header_block(self, text):
        self.set_font("cn", "B", 15)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(80, 120, 200)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def sub_header(self, text):
        self.set_font("cn", "B", 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("cn", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def interviewer_text(self, text):
        self.set_font("cn", "B", 10.5)
        self.set_text_color(20, 80, 160)
        self.multi_cell(0, 7, "\u5f20\u8001\u5e08\uff1a" + text)
        self.ln(2)

    def candidate_text(self, text, prefix="\u9ec4\u5b9d\u80b2"):
        self.set_font("cn", "", 10)
        self.set_text_color(80, 130, 50)
        self.multi_cell(0, 6, prefix + "\uff1a" + text)
        self.ln(2)

    def ref_text(self, text):
        self.set_font("cn", "", 10)
        self.set_text_color(180, 120, 0)
        self.set_fill_color(255, 250, 235)
        self.multi_cell(0, 6, text, fill=True)
        self.ln(2)

    def comment_text(self, text):
        self.set_font("cn", "", 9.5)
        self.set_text_color(150, 50, 50)
        self.set_fill_color(255, 240, 240)
        self.multi_cell(0, 5.5, text, fill=True)
        self.ln(2)

    def bullet(self, text):
        self.set_font("cn", "", 10)
        self.set_text_color(50, 50, 50)
        self.cell(6, 6, "\u00b7")
        self.multi_cell(0, 6, text)
        self.ln(0.5)

    def note_box(self, title, lines):
        n = len(lines)
        box_h = 8 + 6.5 * n
        self.set_fill_color(235, 245, 255)
        self.set_draw_color(80, 120, 200)
        y0 = self.get_y()
        if y0 + box_h > self.h - self.b_margin:
            self.add_page()
            y0 = self.get_y()
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, box_h, style="DF")
        self.set_xy(self.l_margin + 3, y0 + 2.5)
        self.set_font("cn", "B", 10)
        self.set_text_color(20, 80, 160)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        for line in lines:
            self.set_x(self.l_margin + 5)
            self.set_font("cn", "", 9.5)
            self.set_text_color(50, 50, 50)
            self.cell(0, 6.5, line, new_x="LMARGIN", new_y="NEXT")
        self.set_y(y0 + box_h + 3)
        self.ln(4)

    def cn(self, text):
        """Safely handle Chinese text with quotes"""
        return text


def build_pdf():
    pdf = PDF()
    pdf.set_margin(15)

    # ============ PAGE 1: COVER ============
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("cn", "B", 26)
    pdf.set_text_color(20, 60, 140)
    pdf.cell(0, 14, "\u4e3b\u7b56\u5c97\u6a21\u62df\u9762\u8bd5\u5168\u8bb0\u5f55", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("cn", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "\u9ec4\u5b9d\u80b2 \u2192 \u6df1\u5733\u5149\u6c47\u77f3\u6cb9\u96c6\u56e2", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "\u4f11\u95f2\u6e38\u620f\u7cfb\u7edf\u7b56\u5212\uff08\u4e3b\u7b56\u5c97\uff0915-25K", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(80, 120, 200)
    pdf.set_line_width(1)
    y = pdf.get_y()
    pdf.line(50, y, pdf.w - 50, y)
    pdf.ln(10)
    pdf.set_font("cn", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "\u9762\u8bd5\u5b98\uff1a\u5236\u4f5c\u4eba\u300c\u5f20\u8001\u5e08\u300d", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "\u5236\u4f5c\u65f6\u95f4\uff1a2026.07.24", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "\u573a\u666f\uff1a\u9879\u76ee\u6025\u9700\u4e3b\u7b56\uff0c\u8282\u594f\u504f\u5feb\uff0c\u538b\u529b\u9762", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "\u5de5\u5177\uff1aWorkBuddy\uff08\u5c0f\u4e03\uff09AI \u8f85\u52a9\u6a21\u62df", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("cn", "", 10)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 7, "\u672c\u6587\u6863\u5305\u542b\uff1a4\u9053\u9762\u8bd5\u9898\u5b8c\u6574\u95ee\u7b54\u94fe + \u539f\u59cb\u56de\u7b54 + \u6539\u8fdb\u7248\u672c + \u8003\u5b98\u70b9\u8bc4 + Monopoly Go\u901f\u8bb0\u5361", align="C", new_x="LMARGIN", new_y="NEXT")

    # ============ Q1 ============
    pdf.add_page()
    pdf.header_block("Q1\uff1a\u81ea\u6211\u4ecb\u7ecd\uff08\u5f00\u573a\u5b9a\u751f\u6b7b\uff09")
    pdf.ln(2)
    pdf.interviewer_text("我是光汇这边负责休闲游戏项目的制作人，叫我张老师就行。项目现在是欧美市场紧急需要主策，所以我直接聊重点，不绕弯子。你先简单介绍下自己吧，控制在两分钟内。")

    pdf.sub_header("\u539f\u59cb\u56de\u7b54")
    pdf.candidate_text("您好，我是黄宝育，负责过回合制rpg、消除+卡牌rpg、3d足球游戏、休闲游戏的项目，之前的工作类型接触过游戏用户增长、游戏运营、游戏系统策划、游戏执行主策，在系统、战斗、玩法方面的设计都具备一定经验；上一家公司担任游戏执行主策，主要负责指导团队方案输出，协助跟进落地。")

    pdf.sub_header("\u8003\u5b98\u70b9\u8bc4")
    pdf.comment_text("太泛了。虽然列举了所有项目类型和角色，但听完不知道你最拿手的是什么，也没提到任何具体成果。面主策岗，开场需要让面试官在60秒内记住你的核心标签。")
    pdf.comment_text("缺失：没有抛出具体项目名、没有量化结果、没有连接JD需求（欧美休闲）。")

    pdf.sub_header("\u6539\u8fdb\u7248\u672c")
    pdf.ref_text("您好，我叫黄宝育，Orson。9年游戏行业经验，前3年做腾讯系KA运营（懂投放+数据），后6年做策划，从系统策划做到执行主策。最近5年在奕兆科技负责两个海外项目：《Hero of Taslinia》回合制RPG和《Zodiac Heroes》海外三消卡牌，两个都是欧美主发，我主要负责战斗框架、英雄系统、好友系统、社交+休闲子玩法（画册收集、飞船派遣）。最近也在用业余时间做一个AI-NPC对话解谜独立游戏，持续学习新技术。这次看到贵司欧美休闲赛道在招主策，我对复合类型休闲（消除+养成+社交）这个方向很感兴趣，希望加入。")
    pdf.note_box("关键技巧", [
        "前3年腾讯KA运营 = 隐藏加分（JD要数据思维）",
        "提到「欧美主发」= 精准踩JD",
        "AI-NPC独立项目一笔带过 = 证明自驱力但不喧宾夺主",
        "结尾「复合类型休闲」= 展示你对JD的理解",
    ])

    # ============ Q2 ============
    pdf.add_page()
    pdf.header_block("Q2：系统设计深挖 — 竞技场系统")
    pdf.ln(2)
    pdf.interviewer_text("你提到负责过'消除+卡牌RPG'——这个叫Zodiac Heroes对吧？你在里面具体设计过哪些系统？能不能挑一个讲透的，从头到尾说一遍，你做了什么、改了哪些、上线后数据什么样？")

    pdf.sub_header("黄宝育回答（核心内容）")
    pdf.body_text("选择讲竞技场系统。背景：大量玩家反馈匹配不公平。发现异步竞技场错误使用实时匹配机制，改成让玩家匹配3个对手，提供战前信息让玩家自选对手。")
    pdf.body_text("设计了ELO匹配机制——3个对手分别低于、相近、高于玩家，满足保底得分、公平竞技、快速上分三种需求。同时设计了机器人生成逻辑（难度机制 + 生成链路：从阵容人数 -> 位置 -> 职业 -> 技能装备），并嵌套了机器人生成概率算法（低分/连败易匹配机器人，高分/连胜难匹配）。")
    pdf.body_text("调整了短中长期目标：每日挑战宝箱、竞技场商店、段位奖励、赛季排行榜。最终结果：竞技场参与率从60%提升到80%，新玩家胜率控制在95%，老玩家胜率控制在60%。")

    pdf.note_box("做得好的地方", [
        "用了STAR结构：背景 -> 问题 -> 方案 -> 结果",
        "给出了具体数据（参与率60%->80%，新老胜率）",
        "讲了匹配算法+机器人链路两条线，展示系统架构能力",
    ])
    pdf.note_box("可改进的地方", [
        "开场应该先给一句话定位：'我讲最能体现代码+数学+设计三者结合的竞技场。'",
        "新玩家95%胜率应该主动解释'前3场'的定义边界",
        "结果可以再加一层反思：'如果重来，我会在机器人难度曲线加AB测试'",
    ])

    # Q2.1
    pdf.ln(2)
    pdf.sub_header("追问1：异步匹配 vs 实时匹配的差异")
    pdf.interviewer_text("异步竞技场本身就是离线对打，实时匹配是指什么？是匹配等待超时太长？还是匹配池太小？你说这是核心问题，能不能展开说清楚？")
    pdf.ref_text("异步竞技场有更多容错空间，允许玩家同时匹配复数玩家供自行选择。实时匹配是同步战斗的方式，在某一刻由系统确定对手。前者的好处是：玩家打不过的责任一部分能让玩家自己承担（因为是自己选的）；后者是全责，玩家打不过容易将全部责任怪罪匹配系统。这个设计哲学的关键是「把挫败感从系统的责任变成玩家的选择」——这对休闲游戏至关重要。")

    # Q2.2
    pdf.ln(2)
    pdf.sub_header("追问2：机器人生成逻辑")
    pdf.interviewer_text("机器人是从玩家数据复制的还是从0构造的？怎么保证生成的机器人像真人？玩家能看出来对面是机器人吗？")
    pdf.ref_text("从0构造。设计了完整的生成链路：阵容人数 -> 根据位置赋予职业 -> 根据职业+难度赋予应有技能和装备。真实感有两层保障：1) 阵容合理性（奶妈/脆皮不在前排，肉盾不在后排）；2) AI决策树（奶妈不会给满血角色治疗，刺客不会不斩杀去打满血角色，输出角色不会不放普攻）。回合制游戏的「真实感」核心在AI行为合理，而不在数值。")

    # Q2.3
    pdf.ln(2)
    pdf.sub_header("追问3：新玩家胜率95%是否过高")
    pdf.interviewer_text("新玩家95%是不是有点高了？会不会导致他们很快失去挑战感？这个数据是你主动定下来的，还是上线后自然跑出来的？")
    pdf.ref_text("新玩家目前定义是前3场战斗。这是我主观判断——玩家碾压3局带来的爽感不会让他在前3场感到乏味。根据模拟，第4场基本匹配真实玩家，玩家会发现挑战性。另外如果玩家乏味，他也可以主动选择高难度的挑战对象，匹配规则上已经提供了这个选项。")
    pdf.comment_text("追问3处理得合格——给出了「前3场」的定义边界和设计理由。但如果能补一句「我们后续看了第4-10场的留存率来验证这个假设」会更好。")

    # Q2.4
    pdf.ln(2)
    pdf.sub_header("追问4：角色边界（关键题）")
    pdf.interviewer_text("你在里面有什么几次需要跟主策/制作人对齐的决策节点？")
    pdf.ref_text("这个方案的设计，我仅接收到一开始的玩家反馈，如何解决如何设计全权交由我负责。当时环境中缺少数值支持工作，匹配算法都是我独立推演完成的匹配公式。当时我是系统策划，中间有了解项目问过几次主策，剩下基本写完方案和他们对了——原本想的是可能推翻我就重写，不过结果上他们对我的设计基本满意。")
    pdf.comment_text("核心信息：独立方案输出能力 + 主动算法推演 + 方案一次过。这展示了「不是只执行，能独立输出完整方案」的潜质。但从执行主策到主策，还需要补充一句「这个经验让我意识到我缺的是定方向+扛KPI的经验，这正是我来这里的原因」——可惜没说。")

    # ============ Q3 ============
    pdf.add_page()
    pdf.header_block("Q3：为什么做休闲不做中重度？（核心价值观题）")
    pdf.ln(2)
    pdf.interviewer_text("你看你的简历——Zodiac是三消RPG，Hero是回合制RPG，3D足球是竞技模拟。我现在这个项目要做的是欧美休闲游戏，不是三消卡牌那种复合型，是更纯粹的休闲：合成、消除、放置、模拟经营。你简历里休闲游戏经验只有满天星那5个月，还是2020年的。那你告诉我——为什么我觉得你应该来做休闲，而不是继续做中重度？你对欧美休闲玩家和欧美中重度玩家，到底看到了什么本质差异？")

    pdf.sub_header("参考回答（三层递进结构）")
    pdf.ref_text("对，我过去主要做中重度——回合制RPG、三消卡牌这些。休闲游戏纯经验确实只有满天星那几个月。但我发现我在中重度积累的三样东西，恰恰是很多纯休闲团队缺的。")

    pdf.sub_header("第一层：三个中重度带来的能力，休闲很需要")
    pdf.bullet("数据驱动的方法论：腾讯KA运营出身，天天看ROI、留存漏斗、LTV。休闲游戏没有剧情拉着你走，玩家每一下点击、每一个流失节点，全靠数据告诉你该调什么。")
    pdf.bullet("系统架构能力：中重度让我习惯了一个系统怎么和十个系统耦合。休闲看起来简单，但要做长线——合成-产出-消耗-变现的链，光靠「好玩」撑不住6个月。")
    pdf.bullet("社交设计的经验：我在Zodiac参考Monopoly Go做了好友时间线，画册也要通过社交产生交互。欧美休闲的趋势就是社交化——Monopoly Go一年20亿靠的不是消除手感，是好友互偷互炸的社交盘。")

    pdf.sub_header("第二层：我对休闲 vs 中重度玩家的本质理解")
    pdf.note_box("核心洞察", [
        "中重度：「我要变强」——愿意刷50次装备，输了想「再来一局」",
        "休  闲：「我想舒服」——点3次没爽到就跑了，输了想「换个游戏吧」",
        "中重度设计逻辑：目标 -> 挑战 -> 成就感",
        "休闲设计逻辑：舒服 -> 惊喜 -> 还想来",
    ])
    pdf.body_text("这其实回到了我优化Zodiac竞技场时的核心洞察——让玩家自己选对手，把挫败感从系统责任变成玩家选择。在休闲游戏里，每一个流失节点都应该是玩家自己的选择，不是被系统逼走的。为什么我想做休闲？中重度在卷数值、卷深度，但休闲在卷「让人开心的效率」——怎么用最少的系统和最多的快乐让玩家留下来。这件事更有挑战性，也更适合我这种喜欢抠数据和玩家心理的人。")

    # ============ Q4 ============
    pdf.add_page()
    pdf.header_block("Q4：第一周数据分析（主策决策力考察）")
    pdf.ln(2)
    pdf.interviewer_text("我们目前项目在欧美市场跑了一段时间，DAU还行但留存曲线前高后低，3日活跃不错但7日之后掉得很快。我怀疑是中期内容不够，也可能是社交系统没做起来。你现在来做主策，第一周你会先看什么数据、先做什么事？我不要大纲，我要你具体到指标名和你第一周每天的安排。")

    pdf.sub_header("原始回答")
    pdf.candidate_text("先查看3日解锁的玩法中的数据，了解目标人群在我们游戏中获取的体验核心来源。然后查看4日的流失数据，主要流失点在哪。查看好友系统相关数据，玩家好友添加情况，互动情况，好友系统是否健康，交互是否便捷，体验是否好。根据结果决定是否优化好友系统。确定了这个社交基础，然后回到核心玩法是否具备社交相关内容，具备的话分析数据和体验，玩家的参与度如何，体验方面感知、趣味性是否具备，根据结果决定是否优化玩法。")

    pdf.sub_header("考官点评")
    pdf.comment_text("方向对，但问题在于：1) 说的全是定性方向，一个具体指标名都没出（DAU/D3/D7/渗透率/漏斗全没说）；2)「根据结果决定是否优化」——这句话主策不能说，主策要在没数据的时候先有预判和假设。")

    pdf.sub_header("追问：具体指标 + 第一判断")
    pdf.interviewer_text("第一，你说的都是定性方向，具体的指标名你说不出。第三天你要从后台拉什么表？第二，你在拿到数据之前，心里有没有预判？你的假设是什么？如果预判错了备选是什么？我不要「看数据再决定」——我要知道在没有数据的情况下，你赌的第一刀砍哪里。")

    pdf.sub_header("参考回答：预判先行")
    pdf.ref_text("在没看到数据之前，我的预判是：问题大概率不在核心玩法本身——如果3日留存没问题，说明核心loop是成立的。7日掉，最可能是两个原因：一是中期目标感断了，二是社交系统没形成「我每天要回来看看」的惯性。我赌第一刀砍的是「中期目标+社交触发」。")

    pdf.sub_header("第一天：拉三张表")
    pdf.bullet("新用户D1/D3/D7留存曲线，按渠道（自然量vs买量）拆分看有没有渠道偏差")
    pdf.bullet("关卡/等级分布漏斗——新用户在哪个关卡/等级节点流失最集中，看「到达率」不是通过率")
    pdf.bullet("核心系统渗透率——D3玩家有多少碰过社交功能，D7玩家有多少")

    pdf.sub_header("第二天：事件埋点漏斗 + 社区反馈")
    pdf.bullet("社交相关：好友添加率、首次互动触发节点（第几关引导加好友的）、互动后D1回访率")
    pdf.bullet("社区反馈：欧美商店评分、Discord/Reddit高频关键词")
    pdf.bullet("确认用户是「没发现社交功能」还是「发现了但觉得无聊」")

    pdf.sub_header("第三天：体验 + 访谈")
    pdf.bullet("自己用新号从第1天玩到第7天，记录疲劳点")
    pdf.bullet("找3-5个核心玩家或老员工聊：「你觉得玩家D7之后还回来的理由是什么」")

    pdf.sub_header("如果预判错了")
    pdf.ref_text("如果数据告诉我社交渗透率不低、互动率也还行，但玩家就是第7天不回来了——说明不是社交的问题，是核心玩法到了中期的目标梯度出了问题。前期建房子的成就感很强，但建到第五栋之后体验趋同。那我第二刀砍的是中期新目标系统——类似Monopoly Go的「新城市棋盘解锁」或者Royal Match的「新装修区域」，给玩家一个「再玩三天就能解锁新东西」的期待。")

    pdf.note_box("核心方法论", [
        "预判：赌社交是主因，备选是中期目标梯度",
        "四指标：D3->D7留存断崖、社交渗透率、互动后回访率、等级分布漏斗",
        "目标：一周内给出诊断结论+第一个优化方向",
    ])

    # ============ Monopoly Go ============
    pdf.add_page()
    pdf.header_block("附：Monopoly Go 速记卡（面试弹药）")
    pdf.ln(2)
    pdf.sub_header("一句话定位")
    pdf.body_text("Monopoly Go 不是一个棋盘游戏——它是一个「掷骰子驱动的社交破坏+收集引擎」，核心不靠玩法深度，靠的是社交摩擦+随机奖励+限时焦虑的循环。")

    pdf.note_box("核心数据（面试张口就来）", [
        "2023.4上线 -> 不到两年 $60亿 IAP收入",
        "DAU 1000万+，70% 周留存（比营收更重要的数字）",
        "ARPPU 是同类休闲的 3-5 倍",
        "35岁以上用户占 40-60%（高净值人群）",
        "开发7年，中途推翻2个版本（太竞技 / 太复杂）",
    ])

    pdf.sub_header("核心循环")
    pdf.body_text("掷骰子 -> 移动 -> 落地触发事件 -> 获取资源/触发社交\n  -> 建造/升级/破坏/偷窃/收租 -> 骰子耗尽 -> 等恢复 or 氪 -> 继续掷")

    pdf.sub_header("四大设计引擎 & Zodiac 连接点")
    pdf.bullet("社交破坏：好友互炸、偷银行、社区宝箱 -> Zodiac好友时间线（你参考Monopoly Go做的）")
    pdf.bullet("收集系统：贴纸相册（稀缺+交易）、限时卡册 -> Zodiac画册收集（卡包节奏、周期性收集）")
    pdf.bullet("事件驱动LiveOps：每天换活动类型（竞速/掉落/合作/联赛）、多活动叠加 -> Zodiac活动规划经验")
    pdf.bullet("骰子经济学：倍率系统（x1->x100）、临界点触发、损失厌恶 -> 腾讯KA出身的ROI思维")

    pdf.sub_header("面试可用的连接语")
    pdf.body_text("我在Zodiac做好友时间线的时候主要参考的就是Monopoly Go。我注意到它为什么比Coin Master更进一步——Coin Master是老虎机转盘，玩家被动等结果；Monopoly Go是掷骰子+棋盘可视化，玩家有「我在往前走」的错觉。这个「可控的随机」是我设计好友时间线时的核心思路——让玩家觉得社交不是被系统逼迫的，而是自己选择去互动。")

    pdf.sub_header("如果被追问「Monopoly Go有什么缺点」")
    pdf.body_text("核心风险是内容消耗速度。Scopely靠高频活动对冲，但活动一多新玩家理解成本飙升。倍率系统虽然刺激付费，但也加速了骰子消耗，长期对核心循环有磨损。如果让我做同类产品，我会在骰子消耗和恢复之间加更多免费小循环——比如每天送三次不看广告直接给骰子的福利节点，让非付费玩家也能维持节奏感。")

    # ============ 总结 ============
    pdf.add_page()
    pdf.header_block("面试总结 & 你的下一步行动计划")
    pdf.ln(2)

    pdf.sub_header("本次模拟面试暴露的3个短板")
    pdf.bullet("自我介绍太泛：60秒内没让面试官记住一个标签。需要把「腾讯KA运营+海外项目+数据思维」三个词钉进开场。")
    pdf.bullet("数据语言不精确：回答时说了很多「玩家添加情况、互动情况、体验是否好」但没说出具体指标名。面试用词要换成：留存率、渗透率、到达率、回访率、ARPPU。")
    pdf.bullet("预判力不够：面试官问到「数据之前你的假设是什么」时卡住了。主策的核心能力不是「看完数据再决策」，而是「没数据时也敢下判断，错了能快速掉头」。")

    pdf.sub_header("面试中展示出来的3个加分项")
    pdf.bullet("竞技场系统讲得深：匹配算法+机器人链路+数据结果，展示了独立输出完整方案的能力。")
    pdf.bullet("设计哲学清晰：「把挫败感从系统责任变成玩家选择」——这句话会留下印象，继续用。")
    pdf.bullet("Monopoly Go做了功课：能从行业视角讲设计逻辑，不是只看表面玩法。")

    pdf.sub_header("面试前30分钟最终检查表")
    pdf.bullet("把简历里每个数字背熟（DAU、留存、团队人数、版本周期）")
    pdf.bullet("准备1段90秒自我介绍（含：腾讯KA运营 + 海外项目 + AI自驱力 + 休闲方向兴趣）")
    pdf.bullet("准备3个深度项目案例：竞技场系统 / 画册收集 / 好友时间线 — 全用STAR+数据")
    pdf.bullet("了解光汇石油集团的休闲游戏产品（查官网/应用商店）")
    pdf.bullet("背3个反向提问：项目阶段 / 3个月目标 / 核心KPI是DAU还是ARPPU")
    pdf.bullet("衣着得体，提前10分钟到")

    pdf.note_box("一句话总评", [
        "优势：9年经验+海外+腾讯KA+AI自驱力+ENFJ——很适合做「复合类型休闲」主策",
        "风险：纯休闲经验偏短、数据分析描述偏弱——面试中主动把休闲设计能力往上拔",
        "制作人最想听到的三个词：结果、数据、节奏——埋进每个回答里",
    ])

    # ============ SAVE ============
    output_path = r"D:\_WorkFile\_Daily\Ai_test\mock-interview-2026-07-24.pdf"
    pdf.output(output_path)
    print(f"PDF saved: {output_path}")


if __name__ == "__main__":
    build_pdf()
