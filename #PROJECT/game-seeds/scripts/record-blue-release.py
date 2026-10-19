from pathlib import Path
root=Path(__file__).resolve().parents[3]
def prepend(relative,text):
    p=root/relative;old=p.read_text(encoding='utf-8-sig');head,rest=old.split('\n',1)
    p.write_text(head+'\n\n'+text.strip()+'\n'+rest,encoding='utf-8')

section='''## 蔚蓝星球整游与十系统修订 · 2026-10-19

按最新拆解工作流深化整游＋10系统：国王双天赋/披风/技能孔位，装备资源分流，S1战役/神器重置/赛季合作，招募资格、周兑换、领地四设施和赛季公会。19来源、11新增原图或局部，历史与当前未知分开；64行参考成长费用及各模块v2配置/异常/接口/验收明确标为自设。原作全等级费用、完整概率与全账号实机仍缺，参考服务器未实现。

发布game-ideas-20261019T032208Z：82文件/12,395,747字节，公网hash及线上10系统/图片/流程图/三屏专项通过；本地57文档、样稿和返回定位回归通过。主站保持、旧版备份。全库4游戏38系统57文档49SVG＋21PNG；既有阴阳师已验收养成保持。

验收：https://orson.games/game-ideas/?v=20261019-blue#library/blue-planet-app 。建议先看英雄与国王、关卡赛季、合作和领地。生产脚本expand/specify/finalize-blue-20261019.py是一次性记录，勿重复执行；日常只运行build-catalog与build-library。用户内容待验收。
'''
for p in ['#PROJECT/game-seeds/README.md','#Game-TearDown/永远的蔚蓝星球-App/README.md']:
    prepend(p,section)
prepend('#Game-TearDown/README.md','''## 蔚蓝星球全面修订 · 2026-10-19

整游及10系统按最新工作流补深：英雄与国王、资源成本、六部位装备、S1战役/神器/合作、获取资格、领地与公会。新增9来源、11原图/局部；64条独立参考费用、模式与资源交接。来源事实、历史变化、未知与开发补充分开。全库仍4游戏38系统57文档，公开49SVG＋21PNG。

发布game-ideas-20261019T032208Z，82公网hash及线上十系统三屏验收通过；用户内容待反馈。详情见_framework/validation/蔚蓝整游优化-2026-10-19.md。''')
prepend('#PROJECT/game-seeds/DEPLOY.md','''## 蔚蓝星球全文修订（北京时间2026-10-19）

- 发布game-ideas-20261019T032208Z，82公开文件、12,395,747字节；服务器及公网逐文件SHA256一致。
- 备份/var/www/game-ideas-20261019T032208Z-previous；只更新game-ideas，主站首页不变。
- 线上tests/blue-full.cjs覆盖整游和10系统、11原图、64费用表、流程图、链接与1440/390/320；本地library、reader-sample、reader-navigation通过。
- 验收 https://orson.games/game-ideas/?v=20261019-blue#library/blue-planet-app 。默认游戏库、目录高亮、收藏、双返回保持；参考玩法服务与当前原作全流程未实现/实测。''')
prepend('AI_INDEX.md','- 蔚蓝星球全面修订（2026-10-19）：整游＋10系统、11原图局部、64参考费用行；S1神器/赛季合作与国王成长补齐。入口`#Game-TearDown/永远的蔚蓝星球-App/reader/游戏分析.md`，验收`_framework/validation/蔚蓝整游优化-2026-10-19.md`。82文件发布032208Z，线上图文三屏通过，用户待验收。')

# Required closing order; preserve every other project's current entries.
prepend('memory.md','- 2026-10-19 蔚蓝星球App按最新工作流全面优化并发布game-ideas-20261019T032208Z：整游＋10系统，英雄/国王双线、六部位/材料分流、S1神器/战役/计分合作、获取资格/周兑换、领地四设施/赛季公会；新增9来源共19、11原图局部、64参考成长费用行。独立v2费用/状态/接口/异常及集成表补齐，原作全概率和逐级费用仍缺，未实机全流程或实现服务端。4游戏38系统57文档49SVG＋21PNG；82公网hash、线上10系统三屏、图片/流程/链接和本地57文档/双返回/样稿通过。主页保持、旧版备份、阴阳师已验收养成保持。用户新内容待验；一次性作者脚本不可重跑。仅提交本轮，无push。')
prepend('NOW.md','- 2026-10-19 蔚蓝星球整游＋10系统新版已上线待内容验收：https://orson.games/game-ideas/?v=20261019-blue#library/blue-planet-app 。先看英雄与国王（原图/材料/64参考费用）、关卡赛季（神器重置）、合作（普通与计分）、领地（四设施）。82文件线上hash与10系统三屏专项、本地全库/导航通过。原作未知保留、参考参数另列，非当前全量实机还原；报告_framework/validation/蔚蓝整游优化-2026-10-19.md。')
prepend('heartbeat-state.md','- 2026-10-19 蔚蓝星球全文优化收尾：整游10系统＋11引用图/局部＋64参考费用行，19来源；v2模式/资源契约同步。发布game-ideas-20261019T032208Z，82公网hash、线上图文/附录/三屏及本地57文档/返回定位通过。memory→NOW同步；用户待验，原作当前未知保留，参考服务未实现。仅提交本轮内容/网页/验证与记录，不push；无关简历PDF未触碰。')
print('Project records and memory → NOW → heartbeat updated')
