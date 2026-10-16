"""Build first-batch manifests and navigation from explicitly authored seed metadata.

This is the 2026-10-16 seed migration, not the ongoing content update workflow.
Refuses to overwrite a manifest after its asOf changes or revision rises above 1.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def read_json(p):
    return json.loads(p.read_text(encoding='utf-8'))
def save_json(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

# slug, title, filename, type, fact IDs, source IDs, evidence applicability,
# original fact tags, authored reference diagram nodes.
BP = [
 ('combat','召唤合成与战斗','召唤合成与战斗','combat',[3,4],[1,8],'App公开资料',['二合一','随机召唤'],['召唤占空格','同类同星合并','自动战斗','升级选择']),
 ('heroes','英雄与永久成长','英雄与永久成长','progression',[5],[8],'App玩家档案',['功能性成长节点'],['获得角色','资源升级','行为节点','阵容快照']),
 ('equipment','装备图腾与洗炼','装备图腾与洗炼','equipment',[6,7],[6,9],'App历史攻略与公告',['条件词条','分解回收'],['选择装备','付费洗炼','新旧比较','保留或替换']),
 ('levels','关卡与赛季规则','关卡与赛季规则','level',[10,11],[7,10],'App赛季资料',['关卡规则变体'],['查看特殊规则','阵容准备','波次验证','首通与重复奖励']),
 ('arena','竞技场','竞技场','arena',[8,9],[3,9,2],'App历史攻防公告',['防守AI','击杀施压'],['对手快照','双方防线','怪物压力转移','唯一结果结算']),
 ('coop','合作准备与挑战','合作准备与挑战','coop',[1,2],[2,3],'明确App正式服',['队员准备','队长发起'],['选择方案','双方准备','原子开始','结算后取消准备']),
 ('territory','领地资源与收集','领地资源与收集','economy',[12],[5],'App历史玩家攻略',['时间产出','派遣'],['矿场金币','派遣材料','食堂体力','图鉴一次奖励']),
 ('social','社交公会与排行榜','社交公会与排行榜','social',[13,14],[3,9,5],'App历史公告',['公会首领','多维榜单'],['关系与成员','个人首领伤害','公会贡献','周榜展示']),
 ('recruitment','招募与重复转化','招募与重复转化','progression',[15],[4],'App历史券奖励线索',['玩法奖励招募券'],['展示概率','抽取与保底','重复转碎片','成长投入']),
 ('liveops','商业化与运营减负','商业化与运营减负','liveops',[16,17],[9,10],'App历史公告与计划',['数值性皮肤','运营减负计划'],['活动资格','有效期判定','权益快照','奖励分项展示']),
]
HN = [
 ('combat','刷宝战斗与混沌石','刷宝战斗与混沌石','combat',[1,2],[5,2],'historical-wechat',['放置刷宝'],['消耗混沌石','自动战斗','冻结掉落','装备处理']),
 ('inventory','装备处理与背包','装备处理与背包','inventory',[3],[2],'shared-unverified',[],['掉落待处理','穿戴或保留','锁定与筛选','确认分解']),
 ('progression','祝福等级与头衔','祝福等级与头衔','progression',[4],[2],'shared-unverified',[],['分解得结晶','祝福计时','品质分布变化','头衔扩大上限']),
 ('build','技能符文与构筑','技能符文与构筑','build',[5],[5,2],'historical-wechat',['技能符文构筑'],['选择技能','装配兼容符文','自动优先级','观察触发结果']),
 ('companions','侍从招募与主协战','侍从招募与主协战','progression',[6],[2],'shared-unverified',[],['招募或转碎片','一主战二协战','固化能力','技能与光环']),
 ('dark-energy','暗能与套装','暗能与套装','equipment',[7],[5],'historical-wechat',['后期暗能成长'],['秘境获取','两个装配槽','同套计数','激活独立效果']),
 ('challenges','主线日常与挖矿','主线日常与挖矿','level',[8],[2,3],'shared-unverified',[],['资源缺口','选择副本','次数与权威结果','投入成长']),
 ('offline','离线收益与回流','离线收益与回流','economy',[9],[4],'shared-unverified',[],['暂停在线战斗','权威时间累积','容量封顶','一次领取']),
 ('liveops','运营活动与社交边界','运营活动与社交边界','liveops',[10],[3,2],'shared-unverified',[],['权威成长事件','活动进度','完成验证','幂等奖励']),
]
fact_claims = {
 'BP':{1:'App公告新增队员准备与队长发起',2:'历史合作聊天、奖励预览与狂暴调整',3:'官方描述召唤、合成、强化随机性',4:'玩家档案描述复制与成长节点',5:'英雄成长节点可改变局内功能',6:'历史靴子图腾条件词条样本',7:'官方曾调整装备分解资源产出',8:'历史公告支持防守AI与击杀转移',9:'App扫荡券周清理及不足购买入口',10:'S1关卡机制差异的玩家攻略',11:'官方区分减负已做与计划项',12:'历史领地攻略列矿场派遣食堂图鉴',13:'历史公会Boss与好友功能更新',14:'历史资料列多维榜单',15:'竞技场历史奖励含招募券',16:'历史公告存在数值性皮肤与合作特权',17:'减负计划不是已上线证明'},
 'HN':{1:'微信首发报道描述放置刷宝与构筑',2:'共用早期图稿描述混沌石刷宝循环，微信适用待核',3:'共用图稿装备分解产结晶，微信背包细则待核',4:'共用图稿祝福与头衔成长，微信细则待核',5:'微信首发报道提到技能符文构筑',6:'共用图稿侍从主协战，微信适用待核',7:'微信首发报道提到后期暗能成长',8:'共用官方图稿列多类日常资源玩法',9:'共用产品介绍承诺离线收益，微信细则待核',10:'共用攻略提及活动公会，微信具体机制待核'}
}
fact_sources={
 'BP':{1:[2],2:[3],3:[1],4:[8],5:[8],6:[6],7:[9],8:[3,9],9:[2],10:[7],11:[10],12:[5],13:[3,9],14:[5],15:[4],16:[9],17:[10]},
 'HN':{1:[5],2:[2],3:[2],4:[2],5:[5,2],6:[2],7:[5],8:[2,3],9:[4],10:[3,2]}}
games = [
 ('永远的蔚蓝星球-App','blue-planet-app','永远的蔚蓝星球 · 手机App','App','BP',BP,['solo','coop','pvp'],['iap'],['live-service','seasonal']),
 ('英雄没有闪-微信小游戏','hero-no-dodge-wechat','英雄没有闪 · 微信小游戏','WeChat Mini Game','HN',HN,['solo'],[],['live-service'])
]
details={
 'BP':{
  'combat':['有币且有空格','同类同星且未满星','攻击不打死亡目标','暂停选择后恢复'],
  'heroes':['未拥有消耗碎片','费用与碎片一起扣','数值与行为分开','进行中战斗不变'],
  'equipment':['实例与槽位分开','扣材料并保存候选','明确失去与获得','确认才改变词条'],
  'levels':['开战前告知限制','英雄装备固化','复活不等于清场','奖励按唯一战果发'],
  'arena':['异步防守为P选型','180秒判定胜败','转移怪不递归转移','积分与奖励一次写'],
  'coop':['修改方案取消准备','双方资源都须足够','同请求只建一局','再次挑战重新确认'],
  'territory':['每日次数控制','到点才能领取','满仓不继续积累','发现与领奖分开'],
  'social':['双方关系原子建立','60秒权威累计','归开战时所属公会','同分按达成时间'],
  'recruitment':['P权重60/30/10','先保底再随机','同请求不重复扣券','碎片交给英雄模块'],
  'liveops':['活动有效时间','领奖另有宽限','有效性在开战固定','基础与额外分开']},
 'HN':{
  'combat':['每行动先校验资源','后台暂停不双算','品质等级生成时定','未处理不继续耗石'],
  'inventory':['不立即占正式格','满包保留掉落','方案引用也受保护','整批校验原子回收'],
  'progression':['材料和时间双门槛','完成后手动确认','旧掉落不重新抽取','溢出经验保留'],
  'build':['每类别有限槽位','符文改变行为代价','终极核心基础顺序','显示冷却与触发'],
  'companions':['已拥有则给碎片','同角色不能重复上','下一敌人读取方案','只有主战释放技能'],
  'dark-energy':['冻结类型与套装','装配不复制实例','反复换装不叠加','普通与暗能分开'],
  'challenges':['缺哪类资源','成本收益并列','跨日不重复扣次数','不同材料不同用途'],
  'offline':['在线离线互斥','只信权威时钟','到上限丢弃溢出','未领取可稍后回来'],
  'liveops':['重复事件要去重','固定截止不滚动','取消不扣额度','模拟不等于SDK接入']}}
role_focus={
 'combat':('局内决策与资源效率','战斗tick、目标去重、暂停边界','危险、掉落和状态反馈的层次'),
 'heroes':('数值与功能节点的成长区别','等级成本事务与开战快照','等级前后、解锁节点、方案状态'),
 'equipment':('洗炼选择、回收流量与风险','候选保存、保留/替换、批量原子性','新旧词条、保护角标、结果动效'),
 'levels':('机制教学与首通/重打节奏','复活、双召唤、赛季归属','规则卡、复活提示、清场反馈'),
 'arena':('压力转移、成长带入与匹配','防守AI、时间上限、void退款','双路压力、积分变化、真实对手标签'),
 'coop':('准备成本、身份奖励与伙伴负担','房间版本、双人扣券、断线接管','未准备原因、身份、AI接管与结果'),
 'territory':('多资源来源与登录负担','离线计时、容量、跨日次数','设施可领/满仓/进行中状态'),
 'social':('个人贡献与团体目标关系','双向关系事务、榜单同分与周切','本人排名、关系权限、空态'),
 'recruitment':('目标获取分布与重复转化','保底优先级、记录与重复请求','概率、当前计数、碎片结果'),
 'liveops':('基础收益、权益与限时任务区别','有效期、事件去重、模拟器边界','截止时间、权益分项和取消反馈'),
 'inventory':('物品吞吐、保留决策与误操作','满包、方案引用保护、实例事务','容量、筛选、批量确认、新旧比较'),
 'progression':('材料等待、时间等待、头衔门槛','计时、XP溢出、冻结掉落版本','概率前后、可领升级、条件缺口'),
 'build':('符文取舍与构筑可解释性','动作优先级、DOT、冷却继承','冷却单位、兼容提示、效果归因'),
 'companions':('主战与协战的不同价值','光环合并、主战触发、重复转化','主副槽、盾血分离、招募结果'),
 'dark-energy':('第二成长线的独有决策','套装去重、来源标签、材料隔离','件数、生效条件、独立回收资源'),
 'challenges':('日常预算与资源分工','跨日计数、固定矿盘、唯一结算','模式成本、挖掘状态、作废反馈'),
 'offline':('回归价值与领取负担','服务端计时、多端互斥、上限余秒','有效时长、产量、满仓解释')}
for directory,gid,title,platform,prefix,records,play,business,operation in games:
    folder=ROOT/directory
    manifest_path=folder/'game.json'
    if manifest_path.exists():
        old=read_json(manifest_path)
        if old['asOf']!='2026-10-16' or any(s['revision']>1 for s in old['systems']):
            raise RuntimeError(f'Refusing to overwrite newer content: {manifest_path}')
    systems=[]; diagrams=[]
    for slug,label,filename,kind,fids,sids,applicability,tags,nodes in records:
        sid=('blue-planet-' if prefix=='BP' else 'hero-no-dodge-')+slug
        source_ids=[f'{prefix}-S{i:02}' for i in sids]
        system={'id':sid,'title':label,'type':kind,'presence':'unknown' if applicability=='shared-unverified' else 'present',
          'status':'researched','depth':'deep' if slug in ['combat','inventory','progression','coop','arena','build'] else 'overview',
          'path':f'systems/{filename}.md','revision':1,'specStatus':'reviewable','referenceStatus':'specified-slice-unimplemented',
          'platformApplicability':applicability,'tags':tags,
          'facts':[{'id':f'{prefix}-F{i:02}','claim':fact_claims[prefix][i],'sources':[f'{prefix}-S{n:02}' for n in fact_sources[prefix][i]],'scope':('shared-unverified' if prefix=='HN' and i==2 else applicability)} for i in fids],
          'media':[{'id':sid+'-reference-diagram','path':f'assets/{slug}.svg','kind':'original-diagram','caption':'P参考实现总览；原作F及U边界见正文','sources':[],'publication':'original'}],
          'related':[]}
        if prefix=='HN' and slug=='inventory':
            system['attributes']={'capacityModel':None,'locking':None,'batchDismantle':None,'paidExpansion':None}
            system['referenceAttributes']={'capacityModel':'instance-count','locking':True,'batchDismantle':True,'paidExpansion':False}
        systems.append(system)
        diagrams.append({'file':slug+'.svg','title':label+' · 参考流程','subtitle':'P 独立参考方案；数字、状态和异常处理详见模块正文','flow':slug not in ['territory'],
          'nodes':[{'title':n,'lines':['P 参考设计',details[prefix][slug][i]]} for i,n in enumerate(nodes)],
          'question':'此模块的输入、状态变化与输出，是否都能通过用例核验？',
          'caption':'非原作界面或内部实现；原作证据单独标记 F，未知项标记 U。'})
        body_path=folder/system['path']; body=body_path.read_text(encoding='utf-8')
        image=f'![{label}参考流程](../assets/{slug}.svg)'
        if image not in body:
            lines=body.splitlines(); insert=next((i+1 for i,l in enumerate(lines) if l.startswith('> ')),2)
            lines[insert:insert]=['',image,'','原创P参考流程概览；下文F证据与此图分开阅读，不能据图推定原作规则。']
            body_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    byslug={s['id'].split('blue-planet-')[-1] if prefix=='BP' else s['id'].split('hero-no-dodge-')[-1]:s for s in systems}
    for s in systems:
        s['related']=[x['id'] for x in systems if x['id']!=s['id'] and x['type'] in ('combat','progression','equipment')][:4]
    if prefix=='BP':
        for slug,asset,src in [('coop','coop-leader-20260305.jpg','BP-S02'),('equipment','totem-boots-20251229.jpg','BP-S06')]:
            byslug[slug]['media'].append({'id':byslug[slug]['id']+'-source-image','path':'assets/'+asset,'kind':'original-screenshot','caption':'官方刊载原图，已核读；不等于自行实机验证','sources':[src],'publication':'reference-only'})
    else:
        for s in systems:
            if any('HN-S02' in f['sources'] for f in s['facts']):
                s['media'].append({'id':s['id']+'-official-reference','path':'assets/official-overview-20250212.png','kind':'official-promo','caption':'2025-02-12共用官方攻略长图，微信适用性待核','sources':['HN-S02'],'publication':'reference-only'})
    manifest={'schemaVersion':1,'id':gid,'title':title,'platform':platform,'region':'中国大陆简体中文','build':None,'asOf':'2026-10-16',
      'scope':'公开资料及历史样本；无当前构建实机验证。P为明确范围的可开发参考切片，非原作源码还原。'+('共用早期攻略不确认微信适用性，presence unknown的案例默认不进入已证实系统筛选。' if prefix=='HN' else '商店登记Android 3.0.7(66)，不代表已核验热更或iOS。'),
      'excluded':['其他平台细则','未验证当前概率','完整支付渠道实现'],'playModes':play,'businessModels':business,'operationModels':operation,
      'evidenceStatus':'researched','unknowns':['当前构建与服务器阶段','未公开数值与概率','完整当前系统数量']+(['微信广告及内购商品细则','多端机制一致性'] if prefix=='HN' else []),'systems':systems}
    save_json(manifest_path,manifest); save_json(folder/'assets/diagrams.json',diagrams)
    # Preserve the authored scope and system map; navigation is explicitly generated.
    readme=folder/'README.md'; content=readme.read_text(encoding='utf-8').split('\n<!-- FIRST-BATCH-NAV -->')[0]
    nav='\n<!-- FIRST-BATCH-NAV -->\n## 本批模块文档与岗位入口\n\n'
    nav+='P参考切片已明确规则、配置、接口、UI和验收；尚未开发或运行玩法测试。原作证据缺口不因参考方案补齐而消失。\n\n'
    nav+='| 模块 | 原作适用性 | 参考交付 |\n|---|---|---|\n'
    nav+='\n'.join(f"| [{s['title']}]({s['path']}) | {s['platformApplicability']} | 有限范围规格，待实现验收 |" for s in systems)+'\n\n'
    nav+='[策划阅读](roles/策划阅读.md) · [开发阅读](roles/开发阅读.md) · [美术阅读](roles/美术阅读.md) · [来源台账](sources.json) · [结构化索引](game.json)\n'
    readme.write_text(content+nav,encoding='utf-8')
    (folder/'roles').mkdir(exist_ok=True)
    for role,intro in [('策划','先读原作F和设计解释，再评估P方案的范围、资源闭环与取舍。参考数字仅供原型，不能当作原作数值或已验证商业平衡。'),('开发','先读公共契约，再按核心战斗→配置与成长→资源→运营的顺序联调。每模块P规则与T用例是实现依据；U只约束原作研究，不需要开发者猜原作后端。'),('美术','先核对原图范围，再按每模块UI-ID和资产状态表制作。P流程图不代表原作界面；原图为研究引用，不自动纳入公开素材包。')]:
        rolepath=folder/'roles'/f'{role}阅读.md'
        if rolepath.exists(): rolepath.read_text(encoding='utf-8')
        text=f'# {role}阅读入口 · {title}\n\n{intro}\n\n[参考公共契约](../../_framework/参考实现公共契约.md)\n\n'
        text+='| 模块 | 本岗阅读重点 |\n|---|---|\n'
        role_index={'策划':0,'开发':1,'美术':2}[role]
        text+='\n'.join(f"| [{s['title']}](../{s['path']}) | {role_focus[records[i][0]][role_index]} |" for i,s in enumerate(systems))+'\n\n'
        if role=='美术' and prefix=='HN':
            text+='## 已核读官方长图\n\n![官方共用攻略，微信适用待核](../assets/official-overview-20250212.png)\n\n来源[2025-02-12官网图解](https://www.37.com/yxmys/article.html?cate=gonglue&id=37)。从上向下看混沌石/战斗、祝福、头衔、技能、侍从、日常区域；它支持当时的共用介绍，不能证明当前微信布局或概率。长图保留完整上下文，各模块的SVG负责简明解释参考流程。\n\n[另一张已核读的新手图](../assets/official-beginner-20250212.png)仅作阶段指引线索，不作为必走路线。\n'
        if role=='美术' and prefix=='BP':
            text+='## 关键原图\n\n![队长视角的合作准备](../assets/coop-leader-20260305.jpg)\n\n来源[App官方公告](https://www.taptap.cn/moment/778714788971675862)。观察灰色挑战按钮、未准备原因、方案与队长权限；未见准备后的界面，不推断断线和战后行为。\n\n![历史词条小图](../assets/totem-boots-20251229.jpg)\n\n来源[历史靴子图腾攻略](https://www.taptap.cn/moment/754639971863759829)。仅支持该局部词条，不据此推定全套UI。\n'
        text+='\n## 交付与验收边界\n\n每个模块至少有一张本地SVG和详细规则图/流程文字。所有T用例目前是设计，未冒充执行通过。原作当前平台与数值缺口见各正文末尾；新增证据必须带来源、日期、平台和账号阶段。\n'
        rolepath.write_text(text,encoding='utf-8')

warm=ROOT/'暖雪-Steam/game.json'; data=read_json(warm)
for s in data['systems']:
    s['specStatus']='reviewable';s['referenceStatus']='specified-slice-unimplemented'
save_json(warm,data)
bp=ROOT/'永远的蔚蓝星球-App/sources.json'; data=read_json(bp)
for s in data:
    if s['id'] in ['BP-S02','BP-S06']:s['read']='正文与相关原图已核读'
    if s['id'] in ['BP-S09','BP-S10']:s['read']='直达页面正文已复核'
    if s['id']=='BP-S09':s['limitations']='历史配置，不代表当前所有服务器规则'
save_json(bp,data)
hn=ROOT/'英雄没有闪-微信小游戏/sources.json'; data=read_json(hn)
for s in data:
    if s['id']=='HN-S05':
        s['url']='https://finance.sina.com.cn/stock/relnews/cn/2025-04-10/doc-inesrwyy3327215.shtml'
        s['read']='新浪桌面版直达正文已复核；配图未作为规则证据'
    if s['id']=='HN-S06':s['read']='搜索线索已读，直达多次失败；未作为本批事实唯一依据'
save_json(hn,data)
print('Generated 19 module manifests, diagrams metadata and 6 role indexes; updated Warm Snow specification status.')
