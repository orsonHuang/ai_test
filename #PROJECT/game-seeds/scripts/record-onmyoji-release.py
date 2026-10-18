from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];W=P.parents[1];G=W/'#Game-TearDown'/'阴阳师-国服App'
def prepend(p,text):
 s=p.read_text(encoding='utf-8-sig')
 if text.strip() in s:return
 head,rest=s.split('\n',1);p.write_text(head+'\n\n'+text.strip()+'\n'+rest,encoding='utf-8')
release=json.loads((P/'validation/release.json').read_text(encoding='utf-8'))['release']
overview='https://orson.games/game-ideas/?v=20261018-full#library/onmyoji-cn-app'
prepend(P/'README.md',f'''## 阴阳师整游扩展与默认入口 · 2026-10-18

默认和未知路由现在进入游戏拆解库 `#games`，品牌与“返回主页”同向；显式 `#library` 仍为系统案例库。目录仅高亮当前/父章节，移除“读到”声明，底部阅读线与位置恢复保留。

阴阳师扩展整游与九篇既有系统正文/参考附录，新增独立契灵与术印；系统地图共11入口。补阵容、六位置御魂、召唤计数、副本路线、斗技、结界寄养、资源、任务回流和叙事外观；新增3张经核读历史原图/局部和1张原创图。已验收养成正文、附录、JSON/CSV/计算器均未改。全部参考参数明确自设，完整账号服务和原作全量内容未实现。

当前4游戏、38系统（默认32）、57文档、49SVG＋10PNG；发布 `{release}`，71文件/7,261,071字节。HTTPS逐文件hash与线上整游专项通过；本地57文档、三屏导航/原型/图片/成本、419养成计算和旧工作台回归通过。新增 `tests/onmyoji-full.cjs`，验收入口 {overview} 。

`scripts/expand-onmyoji.py`、`specify-onmyoji.py`等为本次一次性内容生产记录，不是常规构建链；后续直接编辑内容库后执行build-catalog与build:library，勿重复运行作者脚本。''')
prepend(P/'DEPLOY.md',f'''## 阴阳师整游扩展（北京时间2026-10-18）

- 发布 `{release}`：71公开文件、7,261,071字节，HTTPS逐文件SHA256一致；备份 `/var/www/{release}-previous`，主站首页保持。
- 默认入口 `https://orson.games/game-ideas/` → `#games`；目录只保留高亮；阴阳师整游11系统详页及契灵图文已上线。已验收养成页和下载配置未改。
- 验收入口：{overview} 。`tests/onmyoji-full.cjs`覆盖全部11路由与附录、图片、内部引用、材料表算术和1440/390/320无溢出；线上专项与71文件校验通过。''')
prepend(G/'README.md','''## 整游扩展 · 2026-10-18

本轮已扩展整游与九篇既有系统，新增契灵与术印，合计11个独立系统入口。战斗补阵容与执行、御魂补位置/强化/保护、获取补独立计数、PVE补模式路线/协作、社交补结界寄养；运营覆盖任务/成就/回流，叙事补回看/外观交付。各系统附录有参数、规则、状态、消耗、接口与验收；与已验收growth配置核对了材料、技能、经验池和剧情标记交接。

养成reader/systems及三份reference文件保持用户验收版本；新内容待用户评审，不将自动检查当内容验收。新增契灵3图（含探查消耗局部）与原创关系图，来源2023-05-26历史上线资料。所有自设数值明确标注，不称为当前原作全量配置。

参考内容覆盖功能框架，不是现行客户端全部菜单、所有角色/技能和每期活动的实机枚举；百鬼棋、现世交互、各赛季和全量原作数值仍为专项缺口。真实账号服务、数据库、支付和完整客户端未实现。''')
prepend(W/'#Game-TearDown'/'README.md','''## 阴阳师整游扩展 · 2026-10-18

阴阳师已扩至11系统，新增契灵独立入口与3张历史引用图片；其余九系统正文/开发附录加深，已验收养成文件保持。全库4游戏38系统57文档，公开49SVG＋10PNG。网页默认`#games`，目录仅高亮、无“读到”声明。本轮新内容待用户验收，原作未知与补充设计仍分开。''')
report='''# 阴阳师整游扩展验收 · 2026-10-18

## 内容范围

整游补系统关系、前中后期循环和逐模块覆盖索引；九篇系统增量深化，契灵新增独立路由；十一份系统附录包含已验收养成页。新增参考规格覆盖常用完整状态和自设默认参数，保持原作公开事实、历史界面、分析与补充设计分离。已验收养成正文/附录/三下载文件的git差异为空。

契灵历史探查与技能表现原图已实际查看；探查按钮按原像素截取，三图片通过来源台账和显式媒体白名单发布。御魂Wiki内容来自检索正文摘录，直接打开受限，台账已明确，不标记全文实机核实。2025首领变更只保留采证线索，没有当成完整当前规则写入。

## 检查与结果

- 原有engine、browser、library（57文档）、reader-navigation、visual-reader（11地图入口）、illustrated-growth、game-discovery均通过；养成计算419项通过。
- 新onmyoji-full：11独立路由及参考附录、全部本地图片解码、内链存在、默认和未知路由到games、目录无reading-position、三宽度无页面横向溢出通过。
- 御魂15级费用表逐行累计、金币关系和72000总经验已复算；契灵2—20级四段序列及20900总经验已复算。卡池概率总和与PVE效率算例核对。此类检查不是服务端事务或真实概率采样测试。
- 人读1440契灵局部图、390御魂消耗表截图：正文间距、目录高亮、短图注、固定返回与表格内部滚动可用。
- 71公开文件HTTPS SHA256与发布包一致，首页和awakening可访问；部署脚本核对主站首页未改变。线上11系统专项通过。

## 实现与证据边界

参考战斗不是原作全式神引擎；召唤样例19种身份共用两套成长模板；原型仍仅演示御魂四候选约束与蔚蓝合作准备状态。成长计算器独立验证过，新增账号服务/事务/随机服务未实现。2026当前全量活动、技能优先级、奖励表与客户端设置没有逐项实测，未把完整框架称作完整源码或原作配置还原。
'''
(W/'#Game-TearDown'/'_framework'/'validation'/'阴阳师整游扩展-2026-10-18.md').write_text(report,encoding='utf-8')
prepend(W/'AI_INDEX.md','- 阴阳师整游扩展（2026-10-18）：`#Game-TearDown/阴阳师-国服App/reader/游戏分析.md` → 11系统；契灵独立，养成已验收版本保持。全库38系统57文档；网页默认`#games`，目录仅高亮。新增测试`#PROJECT/game-seeds/tests/onmyoji-full.cjs`。')
# Required final state order; preserve any pre-existing concurrent task entries.
entry=f'- 2026-10-18 阴阳师整游扩展已发布{release}：默认游戏拆解库#games，品牌/返回主页同向；目录仅高亮、不再声明读到。整游＋11系统，九既有模块深化、新增契灵；已验收养成正文/附录/参考配置未改。补流程、UI、材料/数值表、状态/异常/验收与成长模块交接；3历史契灵图含局部，1原创关系图。全库4游戏38系统57文档49SVG+10PNG，71HTTPS hash与线上11系统专项通过，三屏导航/原型/图片/成本及419计算回归通过。主页保持、旧版备份；当前全量原作规则/角色和真实后台未复原，新内容待用户评审。'
prepend(W/'memory.md',entry)
prepend(W/'NOW.md',f'- 2026-10-18 游戏种子默认游戏拆解库、目录纯高亮和阴阳师整游11系统已上线待验：{overview} 。可重点看御魂、召唤、PVE、契灵与各开发附录；材料表、局部原图、状态规则已补，已验收养成页保持。71公网hash与线上专项通过；历史事实和补充设计分开，非现行全量实机还原。')
prepend(W/'heartbeat-state.md',f'- 2026-10-18 阴阳师整游扩展收尾：11系统/57文档与纯高亮、默认games发布{release}；71公网hash、线上11系统、三屏旧功能及数值检查通过。memory→NOW同步；养成验收版本保持、新内容待用户评审、服务未实现。仅提交本轮内容/网页/记录，不push；既有晚安小屋memory改动保持未暂存。')
# Stage only our new memory entry, leaving the unrelated existing change unstaged.
patch='diff --git a/memory.md b/memory.md\n--- a/memory.md\n+++ b/memory.md\n@@ -1,2 +1,4 @@\n # MEMORY · 活跃工作集\n \n+'+entry+'\n+\n'
(P/'validation'/'memory-this-turn.patch').write_text(patch,encoding='utf-8')
print('Release documentation and final state records written; memory staging patch prepared.')
