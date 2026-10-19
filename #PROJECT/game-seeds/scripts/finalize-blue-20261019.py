from pathlib import Path
import json
root=Path(__file__).resolve().parents[3]/'#Game-TearDown'/'永远的蔚蓝星球-App'
def read(p): return (root/p).read_text(encoding='utf-8-sig')
def write(p,t): (root/p).write_text(t.strip()+'\n',encoding='utf-8')
def save(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2))

# Reuse only the media declarations; do not rerun editorial insertions.
source=Path(__file__).with_name('expand-blue-20261019.py')
ns={'__file__':str(source)}
exec(compile(source.read_text(encoding='utf-8').split("insert('召唤")[0],str(source),'exec'),ns)
r=json.loads(read('reader.json'));r['referenceMedia']=ns['media']
summaries={
'heroes':'英雄与国王双线成长：天赋、披风、技能孔位和材料成本',
'equipment':'六部位、强化、图腾与洗炼，区分晶石和炼器石',
'levels':'主线与S1战役、神器技能树、重置和追赶边界',
'coop':'普通合作与赛季计分，原界面、局部图与准备原型',
'recruitment':'获取资格、招募入口、周兑换与重复结果的证据边界',
'territory':'矿场、矿鼠、食堂与图鉴，资源去向和历史规则表',
'social':'好友、公会首领与赛季公会，个人贡献与团体结算',
'liveops':'配置成本、功能性外观、效率权益与运营减负',
}
for s in r['systems']:
    key=s['id'].removeprefix('blue-planet-')
    if key in summaries:s['summary']=summaries[key]
r['ui']['heroes']['title']='英雄与国王成长 · 信息线框'
r['ui']['heroes']['blocks']=['① 对象｜英雄 / 国王天赋','② 节点｜属性与行为变化','③ 费用｜持有 / 需要 / 缺口','④ 方案｜本局生效范围']
save('reader.json',r)

sources=json.loads(read('sources.json'))
for s in sources:
    if s['id'] not in ['BP-S07','BP-S08']:
        s['accessedAt']='2026-10-19'
    else:s['limitations']+='；2026-10-19网页读取失败，沿用2026-10-16核读记录。'
new=[
('BP-S11','国王系统专项攻略','682325002019669229','文和／官方整理','2025-06-12',['武器双天赋','披风与材料','装备入口历史截图'],'历史玩家攻略；不代表当前全等级成本'),
('BP-S12','App国王时装第4孔位','757642898178050495','蔚蓝球球／官方',None,['开服184天与祝福圣杯','功能性外观与配置'],'页面01/06未显示年份；明确APP端包全部区服，作为历史公告，不猜当前开放状态'),
('BP-S13','首发活动及招募商店周兑换','676570310949996421','蔚蓝球球／官方','2025-05-27',['周限购','折扣与价格阶梯'],'上线前历史公告；当前价格及兑换币待核'),
('BP-S14','剑仙与获取资格调整','713730740449184709','蔚蓝球球／官方','2025-09-10',['开服与招募等级门槛','先锋服与正式服区分','成长节点预览'],'正文含0906及0909研发日志；不是当前概率公示'),
('BP-S15','S1 App更新与赛季规则','843595257361730767?group_id=803344','蔚蓝球球／官方','2026-08-31',['战役难度与首通','共战计分','神器重置','公会与追赶'],'原页08/31，年份依据S1同系列2026活动期限；公告指定区服，不覆盖小游戏'),
('BP-S16','神器技能树预告','https://www.wlxq.cn/article/417/','球球／官方网站','2026-08-26',['同层互斥','前置技能','免费重置'],'测试环境预告；上线部分由S1更新交叉支持，不当当前实测'),
('BP-S17','赛季战役机制预告','841069082835944939','蔚蓝球球／官方','2026-08-24',['换位','复活源头','击杀成长'],'预告样本，不是现行全关卡配置'),
('BP-S18','赛季合作玩法预告','841420547534359475','蔚蓝球球／官方','2026-08-25',['双人计分','首领及场地变化'],'预告，实际上线范围以S1 App更新为准'),
('BP-S19','装备与合作历史迭代','671814364314994839','蔚蓝球球／官方','2025-05-14',['移除装备升品','特效锁定','合作阶段奖励'],'早于App上线，作为演进背景，不直接断言当前App细则'),
]
for ident,title,url,author,date,supports,limits in new:
    sources.append(dict(id=ident,title=title,url=url if url.startswith('https:') else 'https://www.taptap.cn/moment/'+url,author=author,publishedAt=date,accessedAt='2026-10-19',platform='App研究资料；适用范围见scope',scope=limits,read='正文已核读；配图仅登记并检查的选定图片',supports=supports,limitations=limits))
save('sources.json',sources)
g=json.loads(read('game.json'));g['asOf']='2026-10-19'
g['scope']='中国大陆手机App，公开资料与历史截图研究；含S1指定区服及预告边界。原作未知与可开发参考v2分开，无当前完整账号实机验证。'
extra={
'heroes':('英雄与国王成长','BP-S11','国王武器双天赋与披风资源关系有历史攻略和截图'),
'equipment':('装备图腾与洗炼','BP-S19','历史迭代曾移除升品并加入特效锁定，不能拼接早期规则'),
'levels':('关卡与赛季规则','BP-S15','S1战役、计分合作与神器重置有App公告'),
'recruitment':('招募与角色获取','BP-S14','获取资格受服务器与招募入口条件影响'),
'coop':('合作准备与挑战','BP-S18','赛季合作与普通通关型合作目标不同'),
'social':('社交公会与排行榜','BP-S15','S1公会积分与合作队长行为相关'),
}
for idx,s in enumerate(g['systems']):
    s['revision']+=1;s['depth']='deep'
    k=s['id'].removeprefix('blue-planet-')
    if k in extra:
        title,sid,claim=extra[k];s['title']=title
        s['facts'].append(dict(id='BP-F'+str(20+idx),claim=claim,sources=[sid],scope='按来源日期与区服，仅已描述范围'))
g['discovery']['summary']='随机合成塔防，拆解英雄与国王成长、装备资源、竞技合作及S1赛季神器。'
save('game.json',g)

for role in ['策划','开发','美术']:
    p='roles/'+role+'阅读.md';t=read(p)
    t=t.replace('原图为研究引用，不自动纳入公开素材包。','经核读的11张原图及局部以editorial-reference登记公开引用；出处与裁切范围见reader.json。')
    t=t.replace('所有T用例目前是设计，未冒充执行通过。','参考玩法T用例仍为待实现设计；费用表算术与网页测试单独记录，不冒充玩法验收通过。')
    t+='\n\n## 2026-10-19 本轮重点\n\n'+{
    '策划':'先读整游的资源对照与版本修正，再读英雄/国王成本、普通/赛季合作差别、神器重置。优先判断机制、资源和玩家目标能否对应；历史费用与参考值分别评审。',
    '开发':'成长v2定义英雄1—35、国王两树完整费用，装备v2扩至六槽；各模块v2覆盖v1同名默认规则。联调必须使用模式覆盖表，普通合作/赛季合作/竞技/公会不可共享默认终局。3演示英雄和有限内容集不等于还原原作全内容。',
    '美术':'国王全图→天赋双树→费用局部，合作全图→规则局部→开始按钮，矿鼠全图→晶石局部。原图为研究依据，UI线框与开发资产清单才是原创参考方案。优先核验小图可读、材料不混、禁用原因常驻。'}[role]
    write(p,t)

# Explicit rule priority and integration constraints at the beginning of each appendix.
for p in (root/'systems').glob('*.md'):
    t=p.read_text(encoding='utf-8-sig');a=t.split('\n',1)
    notice='\n\n> 2026-10-19 参考规格：v2章节覆盖前文同名配置；未覆盖条款保留。原作规则见作者正文及对应日期来源。参考服务端尚未实现，网页原型只验证所注明的界面状态。\n'
    p.write_text(a[0]+notice+a[1],encoding='utf-8')

print('Metadata: 19 sources, 11 reference media, stable 10 system IDs')
