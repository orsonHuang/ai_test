(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SeedEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const METHODS = { demand: '需求切口', transfer: '机制迁移', constraint: '限制反转' };
  const STATUSES = ['待研究', '做原型', '已验证', '暂搁置'];
  const DEFAULT_BRIEF = { platform: 'PC / Steam', team: '1–2 人', budget: '1 周', topic: '', method: 'all' };
  const RULES = [
    { id: 'short', label: '时间与中断', color: 'mint', keywords: ['时间','中断','短','通勤','碎片','暂停','time','session','pause'], audience: '希望在碎片时间里获得完整体验的玩家',
      titles: ['十分钟侦探社','口袋里的远征','只能行动十步'], genre: '轻量解谜',
      pitches: ['把一桩案件装进一个房间，让每次短暂停留都能推进一条推理。','把长线冒险拆成可随时暂停的路线选择，下一次回来从上一条决定继续。','每个小关只有十次行动，让有限步数成为推理与取舍的核心。'],
      loop: ['观察线索','形成假设','选择行动','获得反馈','保存进展'], prototype: '一个房间、六条线索、两种可检验的解释；加入中断后的事实回顾。', test: '让目标玩家在中途离开后继续，记录恢复思路需要的时间，以及能否说明自己的判断。', risk: '时间短并不自动带来满足感；检查推理是否过于简单，或回顾是否泄露答案。', counter: '寻找喜欢长篇沉浸体验的反馈，确认短时需求属于哪个玩家群体。' },
    { id: 'information', label: '信息与推理', color: 'lilac', keywords: ['线索','信息','推理','情报','猜','侦探','谜','clue','information','mystery'], audience: '享受发现联系、判断真假与信息博弈的玩家',
      titles: ['午夜线索邮局','情报交易夜市','不许提问的侦探'], genre: '推理经营',
      pitches: ['整理来信里的矛盾与遗漏，把正确的消息送到正确的人手中。','在夜市收集、验证和出售消息，情报的流向会改变下一轮交易。','只能观察行动和物件，不能直接询问，用环境中的证据完成推理。'],
      loop: ['收集消息','判断可信度','选择接收者','观察后果','修正判断'], prototype: '三个角色、六条消息、一个能回溯的因果链；先用固定文本事件。', test: '请玩家解释一次选择的证据，并观察其是否愿意用不同的信息策略重玩。', risk: '规则不透明时，推理会变成猜作者；所有关键结论都应有可见线索。', counter: '检查是否已有同类信息交易玩法，以及玩家是否把阅读负担当作劝退点。' },
    { id: 'chores', label: '重复与负担', color: 'peach', keywords: ['重复','杂务','刷','肝','负担','累','grind','repetitive','chore'], audience: '喜欢规划与成长，但对重复执行感到疲倦的玩家',
      titles: ['周末小小工坊','会自己营业的店','每天只能改一件事'], genre: '轻量经营',
      pitches: ['把工作台的布局作为主要决策，让每次改造改变整条制作流程。','把解谜里的因果安排带进经营：设定流程，再观察小店如何自动运作。','每天只能调整一个环节，用最少干预寻找让系统顺畅运作的方法。'],
      loop: ['观察瓶颈','安排流程','启动生产','比较结果','局部调整'], prototype: '三道工序、两种资源、一条能看见瓶颈的流程；不要先做庞大配方表。', test: '观察玩家是在比较方案，还是机械重复同一个操作；记录主动调整的理由。', risk: '删掉杂务后也可能删掉节奏与成就感，需留下有意义的反馈。', counter: '保留喜欢重复劳动或收集节奏的反馈，区分解压需求与效率需求。' },
    { id: 'cozy', label: '放松与陪伴', color: 'rose', keywords: ['放松','陪伴','治愈','温暖','焦虑','压力','cozy','relax','stress'], audience: '希望获得安静陪伴与可控节奏的玩家',
      titles: ['打烊后的修理铺','心情花园','不能催促的旅店'], genre: '温暖叙事',
      pitches: ['修复带着生活痕迹的小物件，在不紧迫的节奏里了解来客的故事。','把情绪变化映射成花园的环境，玩家通过布置回应角色的需要。','客人自行安排日常，玩家只能改变空间，让陪伴在观察中发生。'],
      loop: ['观察来客','理解需要','选择回应','看到变化','留下纪念'], prototype: '一位来客、一件旧物、三次能产生不同回应的选择。', test: '观察玩家是否愿意停留并主动描述角色的感受，同时询问哪里无聊或有压力。', risk: '温暖美术不能替代互动；避免把所有反馈都做成没有差别的赞美。', counter: '查找同类作品中关于内容浅、缺少目标的反馈，确认舒缓与参与感的平衡。' },
    { id: 'environment', label: '系统与间接控制', color: 'sky', keywords: ['天气','环境','生态','种田','农场','系统','模拟','weather','farm','simulation'], audience: '喜欢观察因果、实验系统与间接管理的玩家',
      titles: ['一平方米生态箱','天气管理员','不许碰作物的农场'], genre: '系统模拟',
      pitches: ['在一小块土地上调整环境，观察植物如何互相影响。','把关卡解谜的有限操作带进生态模拟，每轮只有少量天气干预。','玩家只能改变雨与阳光，依靠环境因果让农场慢慢生长。'],
      loop: ['观察环境','预测变化','选择干预','等待反馈','修正模型'], prototype: '一块田、三种作物、雨和阳光两种干预，所有反馈都可直接看见。', test: '让玩家先预测再操作，观察其能否逐步理解因果，以及是否主动尝试新组合。', risk: '反馈太慢会变成等待，规则过多会让结果看似随机。', counter: '确认玩家需要间接控制还是直接操作；核查已有生态和天气玩法。' },
    { id: 'strategy', label: '策略与构筑', color: 'sand', keywords: ['策略','卡牌','组合','构筑','选择','决策','build','deck','strategy'], audience: '享受少量规则产生丰富组合与取舍的玩家',
      titles: ['九格探险队','背包里的城市','每回合少一张牌'], genre: '策略构筑',
      pitches: ['把队伍能力压缩成九格布局，位置变化会改变整个探险方案。','把空间收纳的约束放进城市经营，建筑组合决定资源的流动。','每回合必须舍弃一张牌，在越来越小的工具箱中重新安排策略。'],
      loop: ['获得资源','安排组合','执行方案','观察代价','调整构筑'], prototype: '六张功能不同的牌、一个固定目标、三轮选择；先验证是否存在多种可行解。', test: '记录玩家是否比较过两种方案，以及失败后能否提出具体调整。', risk: '容易出现唯一最优解；随机性不能掩盖决策深度不足。', counter: '检查同类玩法的上手成本与平衡问题，明确自己的规则差异。' }
  ];
  const DEMO_SOURCES = [
    { id:'demo-time', title:'通勤玩家 · 演示访谈', type:'访谈观察', content:'我喜欢解谜，但通勤只有十分钟。中断之后经常忘记线索，希望能很快接着推理。', topic:'short' },
    { id:'demo-info', title:'情报交换 · 演示观察', type:'现实观察', content:'在交易中，信息的可信度与传播顺序会改变选择。别人知道什么，有时比手里的资源更重要。', topic:'information' },
    { id:'demo-chores', title:'经营节奏 · 演示反馈', type:'玩家反馈', content:'规划工坊的时候很有趣，但每天重复领取、补货和刷材料很累。我更想调整流程而不是做杂务。', topic:'chores' },
    { id:'demo-cozy', title:'安静陪伴 · 演示访谈', type:'访谈观察', content:'下班后想放松，不想被倒计时追着走。喜欢慢慢修东西和听故事，有一点温暖的陪伴就好。', topic:'cozy' },
    { id:'demo-farm', title:'间接控制 · 演示观察', type:'现实观察', content:'雨、阳光和土壤之间存在因果。我想观察一个小小的生态系统，通过天气影响农场而不是逐个下指令。', topic:'environment' },
    { id:'demo-strategy', title:'空间取舍 · 演示反馈', type:'玩家反馈', content:'有限的格子让每次构筑和组合更有意思。我想在少量规则中比较不同策略，不想记很多复杂数值。', topic:'strategy' }
  ].map(x=>({...x, url:'', demo:true, createdAt:'2026-10-15T00:00:00.000Z'}));
  function id(prefix='item') { return prefix+'-'+(typeof crypto!=='undefined' && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)); }
  function text(value,max=12000) { return typeof value==='string'?value.trim().slice(0,max):''; }
  function safeURL(value) { if (!value) return ''; try { const u=new URL(value); return ['https:','http:'].includes(u.protocol)?u.href:''; } catch { return ''; } }
  function normalizeBrief(raw={}) { return { platform:text(raw.platform,60)||DEFAULT_BRIEF.platform, team:text(raw.team,30)||DEFAULT_BRIEF.team, budget:text(raw.budget,30)||DEFAULT_BRIEF.budget, topic:text(raw.topic,160), method:Object.hasOwn(METHODS,raw.method)?raw.method:'all' }; }
  function validateSource(raw) {
    if (!raw || typeof raw!=='object') throw new Error('资料格式不正确。');
    const title=text(raw.title,120), content=text(raw.content,12000);
    if (!title || content.length<8) throw new Error('请填写资料标题，并输入至少 8 个字的正文。');
    if (raw.url && !safeURL(raw.url)) throw new Error('来源链接需要完整的 http:// 或 https:// 地址。');
    return { id:text(raw.id,100)||id('source'), title, content, url:safeURL(raw.url), type:text(raw.type,40)||'个人笔记', topic:RULES.some(r=>r.id===raw.topic)?raw.topic:'auto', demo:raw.demo===true, createdAt:text(raw.createdAt,40)||new Date().toISOString() };
  }
  function matchSources(sources, topic='') {
    return RULES.map(rule=>{
      const matches=sources.map(source=>{
        const lower=source.content.toLowerCase();
        const hits=rule.keywords.filter(k=>lower.includes(k));
        const manual=source.topic===rule.id;
        if (!hits.length&&!manual) return null;
        const sentences=source.content.split(/(?<=[。！？!?\n])/).filter(s=>s.trim());
        const excerpt=text(sentences.find(s=>rule.keywords.some(k=>s.toLowerCase().includes(k)))||source.content,360);
        return { sourceId:source.id, title:source.title, url:source.url, excerpt, demo:source.demo===true, hits, manual };
      }).filter(Boolean);
      const focus=rule.keywords.some(k=>topic.toLowerCase().includes(k));
      return { rule, matches, rank:matches.length*10+matches.reduce((n,m)=>n+m.hits.length,0)+(focus?5:0), focus };
    }).filter(x=>x.matches.length>0).sort((a,b)=>b.rank-a.rank);
  }
  function makeIdea(rule, evidence, brief, method='demand', seedId) {
    const index=Object.keys(METHODS).indexOf(method);
    const topic=brief.topic ? `以「${brief.topic}」为题材切入，` : '';
    return { id:seedId||id('idea'), title:rule.titles[index], pitch:topic+rule.pitches[index], genre:rule.genre, theme:rule.label, color:rule.color, method, audience:rule.audience, loop:rule.loop.slice(), prototype:rule.prototype, test:rule.test, risk:rule.risk, counter:rule.counter, evidence:evidence.map(e=>({...e})), brief:{...brief}, demo:evidence.length>0&&evidence.every(e=>e.demo), status:'待研究', notes:'', favorite:false, createdAt:new Date().toISOString(), engine:'local-rules-v1' };
  }
  function generateIdeas(sources, rawBrief={}) {
    const brief=normalizeBrief(rawBrief);
    if (!sources.length) return { ideas:[], signals:[], message:'先添加一条资料，或切换到演示资料体验。' };
    const signals=matchSources(sources,brief.topic);
    if (!signals.length) return { ideas:[], signals:[], message:'没有识别出明确主题。请给资料手动选择线索主题，再试一次。没有命中并不代表没有创意。' };
    const methods=brief.method==='all'?Object.keys(METHODS):[brief.method];
    const ideas=Array.from({length:brief.method==='all'?3:Math.min(3,signals.length)},(_,i)=>{
      const signal=signals[i%signals.length];
      return makeIdea(signal.rule,signal.matches,brief,methods[i%methods.length]);
    });
    return { ideas, signals:signals.map(s=>({label:s.rule.label,count:s.matches.length,keywords:[...new Set(s.matches.flatMap(m=>m.hits))]})), message:`已从 ${sources.length} 条资料整理出 ${signals.length} 类线索。候选方向需要人工核查。` };
  }
  function initialIdeas() {
    return RULES.map((rule,index)=>{
      const source=DEMO_SOURCES[index];
      return makeIdea(rule,[{sourceId:source.id,title:source.title,url:'',excerpt:source.content,demo:true,hits:[],manual:true}],{...DEFAULT_BRIEF},index===1?'transfer':index===4?'constraint':'demand','seed-'+rule.id);
    });
  }
  function markdown(idea) {
    const lines=[`# ${idea.title}`,'',`> ${idea.demo?'演示构想 · 资料为虚构示例':'候选构想 · 资料由用户导入，未经独立核实'} · ${METHODS[idea.method]||'需求切口'} · ${idea.status}`,'',idea.pitch,'','## 目标与约束',`- 目标玩家：${idea.audience}`,`- 目标平台：${idea.brief.platform}`,`- 团队：${idea.brief.team}`,`- 原型验证预算：${idea.brief.budget}（用户设定，不是工期估算）`,'','## 核心循环',idea.loop.join(' → '),'','## 来源线索'];
    idea.evidence.forEach(e=>{lines.push('',`### ${e.title}${e.demo?'（演示）':''}`,e.url||'未提供来源链接',...e.excerpt.split(/\r?\n/).map(line=>'> '+line));});
    lines.push('','关键词匹配仅提示相关主题，不判断正反立场或需求规模。','', '## 最小原型',idea.prototype,'','## 验证方法',idea.test,'','## 风险与反例',idea.risk,idea.counter,'','## 我的验证记录',idea.notes||'尚未记录。');
    return lines.join('\n');
  }
  function prompt(idea) {
    return '请基于下面的创意卡继续研究游戏创意。先区分原始资料、设计推断与待验证假设；不要把演示材料当成真实市场证据。给出近似作品的核查计划、机制之间的因果关系、反例和最小原型测试方案。资料不足时明确指出，不编造引用或销量。\n\n'+markdown(idea);
  }
  function normalizeIdea(raw) {
    if (!raw || typeof raw!=='object' || !text(raw.title,120) || !Array.isArray(raw.evidence) || !Array.isArray(raw.loop)) throw new Error('备份中的创意卡格式不正确。');
    const colors=['mint','lilac','peach','rose','sky','sand'];
    const result={id:text(raw.id,100)||id('idea'),title:text(raw.title,120),pitch:text(raw.pitch,1200),genre:text(raw.genre,60),theme:text(raw.theme,60),color:colors.includes(raw.color)?raw.color:'mint',method:Object.hasOwn(METHODS,raw.method)?raw.method:'demand',brief:normalizeBrief(raw.brief),status:STATUSES.includes(raw.status)?raw.status:'待研究',favorite:raw.favorite===true,notes:text(raw.notes,20000),createdAt:text(raw.createdAt,40),engine:'local-rules-v1'};
    for (const key of ['audience','prototype','test','risk','counter']) result[key]=text(raw[key],2000);
    result.loop=raw.loop.slice(0,10).map(x=>text(x,100));
    result.evidence=raw.evidence.slice(0,100).map(e=>{
      if (!e||typeof e!=='object') throw new Error('备份中的资料引用格式不正确。');
      return {sourceId:text(e.sourceId,100),title:text(e.title,120),url:safeURL(e.url),excerpt:text(e.excerpt,12000),demo:e.demo===true,hits:Array.isArray(e.hits)?e.hits.slice(0,30).map(x=>text(x,50)):[],manual:e.manual===true};
    });
    result.demo=result.evidence.length>0&&result.evidence.every(e=>e.demo);
    return result;
  }
  function parseBackup(value) {
    const raw=typeof value==='string'?JSON.parse(value):value;
    if (!raw||raw.version!==1||!Array.isArray(raw.sources)||!Array.isArray(raw.ideas)) throw new Error('请选择游戏种子导出的 v1 JSON 备份。');
    if (raw.sources.length>1000||raw.ideas.length>1000) throw new Error('单次备份最多包含 1000 条资料和 1000 张创意卡。');
    const sources=raw.sources.map(validateSource), ideas=raw.ideas.map(normalizeIdea);
    for (const entries of [sources,ideas]) if (new Set(entries.map(e=>e.id)).size!==entries.length) throw new Error('备份存在重复编号，请使用完整导出的备份。');
    return { version:1,sources,ideas,brief:normalizeBrief(raw.brief) };
  }
  return { METHODS,STATUSES,DEFAULT_BRIEF,RULES,DEMO_SOURCES,id,safeURL,normalizeBrief,validateSource,matchSources,generateIdeas,initialIdeas,markdown,prompt,parseBackup };
});
