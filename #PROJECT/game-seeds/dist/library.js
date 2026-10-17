(() => {
  'use strict';
  const D=window.GameLibrary, $=s=>document.querySelector(s), e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const types={combat:'战斗',build:'构筑',equipment:'装备',progression:'养成',level:'关卡',economy:'资源经济',narrative:'叙事收集',arena:'竞技场',coop:'合作',social:'社交',liveops:'运营与商业化',inventory:'背包'};
  const modes={solo:'单人',coop:'多人合作',pvp:'多人竞争',premium:'买断',iap:'内购',complete:'完整作品', 'live-service':'持续运营',seasonal:'赛季'};
  const KEY='game-seeds-library-v1';let favorites={},storageOK=true,renderToken=0;
  function read(){try{const raw=localStorage.getItem(KEY);favorites=raw?validate(JSON.parse(raw)):{};}catch{storageOK=false;$('#library-warning').textContent='收藏存储无法读取。可继续浏览，请先导出当前记录。';}}
  function validate(v){if(!v||v.version!==1||!v.favorites||typeof v.favorites!=='object'||Array.isArray(v.favorites))throw Error('不是系统收藏备份');const next={};for(const [id,x]of Object.entries(v.favorites)){if(!D.systems.some(s=>s.id===id)||!x||typeof x.note!=='string'||x.note.length>20000)throw Error('收藏字段无效');next[id]={note:x.note};}return next;}
  function save(id,value){if(!storageOK)return false;try{const raw=localStorage.getItem(KEY);const latest=raw?validate(JSON.parse(raw)):{};if(value===null)delete latest[id];else latest[id]=value;localStorage.setItem(KEY,JSON.stringify({version:1,favorites:latest}));favorites=latest;return true;}catch{$('#library-warning').textContent='收藏未能保存，请导出备份。';return false;}}
  const game=id=>D.games.find(g=>g.id===id);
  function badges(g){return [...g.playModes,...g.businessModels,...g.operationModels].map(x=>`<span>${e(modes[x]||x)}</span>`).join('');}
  function card(s){const g=game(s.gameId);return `<article class="system-card"><a href="#library/${s.id}" class="system-cover"><img src="./${s.media[0].path}" alt="${e(s.title)}机制示意" loading="lazy"><span>${e(types[s.type])}</span></a><div class="system-card-body"><small>${e(g.title)}</small><h3><a href="#library/${s.id}">${e(s.title)}</a></h3><p>${e(s.readerSummary||s.facts[0]?.claim||'参考设计与研究记录')}</p><div class="case-tags">${badges(g)}</div><footer><span class="${s.defaultDiscoverable?'':'uncertain'}">${s.defaultDiscoverable?'资料支持 · 非当前实测':'适用待核 · 含参考设计'}</span><button type="button" data-case-save="${s.id}" aria-pressed="${!!favorites[s.id]}" aria-label="${favorites[s.id]?'取消收藏':'收藏'}${e(s.title)}">${favorites[s.id]?'♥':'♡'}</button></footer></div></article>`;}
  function list(){
    const query=$('#system-search').value.trim().toLowerCase(), gid=$('#game-filter').value,type=$('#system-filter').value,mode=$('#mode-filter').value,status=$('#evidence-filter').value,only=$('#only-saved').checked;
    const found=D.systems.filter(s=>{const g=game(s.gameId);return(!gid||s.gameId===gid)&&(!type||s.type===type)&&(!mode||[...g.playModes,...g.businessModels,...g.operationModels].includes(mode))&&(status==='all'||(status==='present'?s.defaultDiscoverable:!s.defaultDiscoverable))&&(!only||favorites[s.id])&&(!query||[s.title,g.title,...s.tags,D.docs[s.id].search].join(' ').toLowerCase().includes(query));});
    $('#system-count').textContent=`${found.length} 个案例 · ${Object.keys(favorites).length} 个收藏`;
    $('#system-grid').innerHTML=found.length?found.map(card).join(''):'<div class="empty-state"><h3>当前条件下没有案例</h3><p>背包案例的微信适用性仍待核实，可将证据范围切换为「全部，含待核实」。</p><button class="button secondary" id="clear-system-filters">重置筛选</button></div>';
  }
  const facets={genre:'玩法类型',platform:'平台',presentation:'视角与画面',art:'美术风格',experience:'游玩与经营',origin:'产地'};
  let gameQuery='',gameFilters={};
  const gameTags=g=>Object.values(g.discovery?.facets||{}).flat();
  function gameList(){
    const words=gameQuery.toLowerCase().split(/\s+/).filter(Boolean);
    const found=D.games.filter(g=>{
      const haystack=[g.title,g.platform,g.discovery?.summary,...gameTags(g)].join(' ').toLowerCase();
      return words.every(w=>haystack.includes(w))&&Object.entries(gameFilters).every(([key,values])=>!values.length||values.some(v=>g.discovery?.facets[key]?.includes(v)));
    });
    $('#game-search').value=gameQuery;
    $('#game-count').textContent=`${found.length} / ${D.games.length} 款游戏`;
    $('#game-facets').innerHTML=Object.entries(facets).map(([key,label])=>{
      const options=[...new Set(D.games.flatMap(g=>g.discovery?.facets[key]||[]))];
      if(key==='origin'&&!options.includes('海外'))options.push('海外');
      return `<div class="game-facet" role="group" aria-label="${label}"><b>${label}</b><div>${options.map(value=>`<button type="button" data-game-facet="${key}" data-value="${e(value)}" aria-pressed="${!!gameFilters[key]?.includes(value)}">${e(value)}</button>`).join('')}</div></div>`;
    }).join('');
    $('#game-grid').innerHTML=found.length?found.map(g=>`<article class="game-card"><div class="game-card-platform">${e(g.platform==='App'?'手机 App':g.platform==='WeChat Mini Game'?'微信小游戏':g.platform)}</div><h2><a href="#library/${g.id}">${e(g.title.split(' · ')[0])}<span aria-hidden="true">↗</span></a></h2><p>${e(g.discovery?.summary||g.scope)}</p><div class="case-tags">${gameTags(g).map(t=>`<span>${e(t)}</span>`).join('')}</div><footer><span>${D.systems.filter(s=>s.gameId===g.id).length} 个系统模块</span><a href="#library/${g.id}">阅读拆解与系统地图 →</a></footer></article>`).join(''):'<div class="empty-state"><h3>暂时没有符合条件的拆解案</h3><p>可以减少筛选条件，或换一个关键词。</p><button type="button" class="button secondary" data-reset-games>清空筛选</button></div>';
  }
  $('#game-search').addEventListener('input',event=>{gameQuery=event.target.value;gameList();rememberPosition();});
  $('#game-library').addEventListener('click',event=>{
    const b=event.target.closest('button');if(!b)return;
    if(b.dataset.gameFacet){const key=b.dataset.gameFacet,value=b.dataset.value,values=gameFilters[key]||[];gameFilters[key]=values.includes(value)?values.filter(v=>v!==value):[...values,value];gameList();[...document.querySelectorAll('[data-game-facet]')].find(n=>n.dataset.gameFacet===key&&n.dataset.value===value)?.focus({preventScroll:true});}
    if(b.id==='reset-game-filters'||b.hasAttribute('data-reset-games')){gameQuery='';gameFilters={};gameList();$('#game-search').focus({preventScroll:true});}
    rememberPosition();
  });
  let readingHeadings=[],readingObserver=null;
  function updateReadingPosition(reveal=false){
    if(!location.hash.startsWith('#library/')||!readingHeadings.length)return;
    const line=innerHeight-48;
    const current=readingHeadings.filter(h=>h.getBoundingClientRect().top<=line).at(-1)||readingHeadings[0];
    const index=readingHeadings.indexOf(current),parent=current.tagName==='H3'?readingHeadings.slice(0,index).findLast(h=>h.tagName==='H2'):null;
    let active;
    for(const b of document.querySelectorAll('#case-toc button')){
      const selected=b.dataset.scrollSection===current.id;
      b.classList.toggle('current-section',selected);b.classList.toggle('current-parent',!!parent&&b.dataset.scrollSection===parent.id);
      if(selected){b.setAttribute('aria-current','location');active=b;}else b.removeAttribute('aria-current');
    }
    const hint=$('#reading-position');if(hint){hint.textContent='读到：'+current.textContent;hint.title='按屏幕底部可见内容定位 · '+current.textContent;}
    if(reveal&&active&&$('.reader-contents')?.open){const toc=$('#case-toc'),a=active.getBoundingClientRect(),b=toc.getBoundingClientRect();if(a.top<b.top||a.bottom>b.bottom)toc.scrollTop+=a.top-b.top-toc.clientHeight/2+a.height/2;}
  }
  // Keep an entry per visit, so returning to the same article restores that visit.
  const NAV_KEY='game-seeds-reader-navigation-v1';
  let visits={};try{const stored=JSON.parse(sessionStorage.getItem(NAV_KEY)||'{}');if(stored&&typeof stored==='object'&&!Array.isArray(stored))visits=stored;}catch{}
  let activeVisit=null,pendingParent=null,returnVisit=null;
  const newVisit=()=>Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
  function persistVisits(){try{sessionStorage.setItem(NAV_KEY,JSON.stringify(visits));}catch{}}
  function rememberPosition(){
    if(!activeVisit||activeVisit.hash!==(location.hash||'#library'))return;
    const anchors=activeVisit.hash.startsWith('#library/')?[...document.querySelectorAll('#case-document h2,#case-document h3,.system-map a')]:[];
    const anchor=anchors.filter(n=>n.getBoundingClientRect().top<=100).at(-1);
    activeVisit.y=scrollY;activeVisit.toc=$('#case-toc')?.scrollTop||0;
    if(activeVisit.hash==='#games')activeVisit.gameSearch={query:gameQuery,filters:structuredClone(gameFilters)};
    activeVisit.anchor=anchor?(anchor.getAttribute('href')||anchor.id):null;
    activeVisit.offset=anchor?.getBoundingClientRect().top||0;
    visits[activeVisit.key]=activeVisit;persistVisits();
  }
  function beginVisit(){
    const hash=location.hash||'#library',key=returnVisit||(!pendingParent&&history.state?.readerVisit);
    const saved=key&&visits[key]?.hash===hash?visits[key]:null;
    activeVisit=saved||{key:newVisit(),hash,parent:pendingParent,y:0,toc:0};
    pendingParent=null;returnVisit=null;visits[activeVisit.key]=activeVisit;
    history.replaceState({...history.state,readerVisit:activeVisit.key},'');persistVisits();
    return saved?{...saved}:null;
  }
  function restorePosition(saved,token){
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      if(token!==renderToken)return;
      let y=saved?.y||0;
      if(saved?.anchor){const node=[...document.querySelectorAll('#case-document h2,#case-document h3,.system-map a')].find(n=>(n.getAttribute('href')||n.id)===saved.anchor);if(node)y=scrollY+node.getBoundingClientRect().top-saved.offset;}
      window.scrollTo({top:y,behavior:'instant'});if($('#case-toc'))$('#case-toc').scrollTop=saved?.toc||0;updateReadingPosition();$('#view-library').dataset.readyRoute=location.hash||'#library';
    }));
  }
  function parentLink(doc){const parent=visits[activeVisit?.parent];return parent?.hash||((doc&&doc.gameId!==location.hash.slice(9))?'#library/'+doc.gameId:'#games');}
  document.addEventListener('click',event=>{
    const a=event.target.closest('a');if(!a||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||a.target==='_blank')return;
    const hash=a.getAttribute('href');if(!hash?.startsWith('#library')&&hash!=='#games')return;
    rememberPosition();if(hash===(location.hash||'#library'))return;
    if(a.hasAttribute('data-reader-back')){returnVisit=activeVisit?.parent||null;pendingParent=null;}
    else if(a.hasAttribute('data-reader-home')){pendingParent=null;returnVisit=null;}
    else pendingParent=activeVisit?.key||null;
  },true);
  let scrollFrame=0;
  window.addEventListener('scroll',()=>{cancelAnimationFrame(scrollFrame);scrollFrame=requestAnimationFrame(()=>{updateReadingPosition(true);rememberPosition();});},{passive:true});
  window.addEventListener('resize',()=>updateReadingPosition(true));
  window.addEventListener('pagehide',rememberPosition);
  history.scrollRestoration='manual';

  function mountDemo(root){
    const kind=root.dataset.demo;
    const initial=()=>kind==='coop'?{member:true,ready:false,challenge:0,config:0,tickets:2,phase:'room',fail:false,message:'先让队员准备，再由队长发起挑战。'}:{selected:0,current:0,message:'比较候选方案，检查两项队伍条件。'};
    let state=initial();
    const button=(action,label,disabled=false)=>`<button type="button" data-demo-action="${action}" ${disabled?'disabled':''}>${label}</button>`;
    const candidates=[{name:'A · 当前基础方案',attack:3000,speed:125,crit:100},{name:'B · 攻击更高，出手过早',attack:3400,speed:135,crit:100},{name:'C · 攻击更高，暴击不足',attack:3300,speed:122,crit:85},{name:'D · 兼顾两个必要条件',attack:3200,speed:128,crit:95}];
    function draw(){
      let body='';
      if(kind==='coop'){
        const busy=state.phase!=='room',canStart=state.member&&state.ready&&state.tickets>=1&&!busy;
        const reason=busy?'已进入挑战，完成演示后再调整':!state.member?'等待队员加入':!state.ready?'队员尚未准备':state.tickets<1?'挑战券不足：需要 1 张':'双方条件满足，可以发起挑战';
        body=`<div class="demo-scene"><div class="demo-challenge"><small>① 共同挑战目标</small><strong>${state.challenge?'控制考验':'首领挑战'}</strong><span>演示挑战券 ${state.tickets} · 本次消耗 1</span></div><div class="demo-members"><div><small>② 队长</small><b>当前方案 ${state.config?'乙':'甲'}</b><span>拥有发起权限</span></div><div><small>③ 队员</small><b>${!state.member?'尚未加入':state.ready?'✓ 已准备':'待准备'}</b><span>确认当前挑战与配置</span></div></div><p class="demo-reason">${reason}</p>${button('start','队长：发起挑战',!canStart)}${state.phase==='battle'?button('finish','完成本次演示挑战'):''}</div><div class="demo-controls"><h4>操作两个角色，观察状态变化</h4>${button('ready',state.ready?'队员：取消准备':'队员：确认准备',!state.member||busy)}${button('config','更换队伍方案',busy)}${button('challenge','队长：更换挑战',busy)}${button('member',state.member?'队员：离开房间':'队员：加入房间',busy)}${button('tickets',state.tickets?'模拟挑战券不足':'恢复演示挑战券',busy)}<label class="demo-check"><input type="checkbox" data-demo-fail ${state.fail?'checked':''} ${busy?'disabled':''}> 模拟下次开始校验失败</label><p>修改方案或挑战会撤销准备。失败不扣券；成功只扣一次。此处模拟状态，无网络或真实奖励。</p></div>`;
      }else{
        const x=candidates[state.selected],current=candidates[state.current],order=x.speed<130,crit=x.crit>=90;
        body=`<div class="demo-scene"><small>① 队伍目标 · 自设条件</small><h4>辅助速度 130，必须先于输出行动</h4><p>输出暴击至少 90%。这里只检查两个条件，不评价完整阵容强度。</p><label>② 选择候选<select data-demo-candidate>${candidates.map((c,i)=>`<option value="${i}" ${state.selected===i?'selected':''}>${c.name}</option>`).join('')}</select></label><div class="demo-stat-grid">${[['攻击',x.attack,x.attack-current.attack],['速度',x.speed,x.speed-current.speed],['暴击',x.crit+'%',x.crit-current.crit]].map(([name,val,delta])=>`<div><small>${name}</small><b>${val}</b><span>较当前 ${delta>0?'+':''}${delta}${name==='暴击'?'个百分点':''}</span></div>`).join('')}</div></div><div class="demo-controls"><h4>③ 整体条件检查</h4><p class="demo-condition ${order?'pass':'fail'}">${order?'✓':'×'} 出手顺序：${order?'辅助先行动':'输出抢在辅助之前'}</p><p class="demo-condition ${crit?'pass':'fail'}">${crit?'✓':'×'} 暴击条件：${crit?'达到演示目标':'未达到 90%'}</p>${button('apply','④ 应用候选方案',!order||!crit)}<p>当前应用：<strong data-current-candidate>${current.name}</strong></p><p>数据、阈值与筛选界面均为补充设计；不连接原游戏账号，不模拟掉落或强化。</p></div>`;
      }
      root.innerHTML=`<header class="demo-header"><div><span>可点击原型 · 补充设计</span><h3>${kind==='coop'?'准备，是对当前配置的确认':'单件提升，也要满足队伍条件'}</h3></div>${button('reset','重置演示')}</header><div class="demo-layout">${body}</div><p class="demo-message" role="status" aria-live="polite">${e(state.message)}</p>`;
    }
    root.addEventListener('click',event=>{const target=event.target.closest('[data-demo-action]');if(!target||target.disabled)return;const action=target.dataset.demoAction;
      if(action==='reset')state=initial();
      else if(kind==='coop'){
        if(action==='finish'){state.phase='room';state.ready=false;state.message='演示挑战结束，回到房间；重新准备后可以再次开始。没有发放真实奖励。';}
        else if(state.phase!=='room')return;
        else if(action==='ready'&&state.member){state.ready=!state.ready;state.message=state.ready?'队员已确认当前挑战与方案。':'队员取消准备，队长暂不能开始。';}
        else if(action==='config'||action==='challenge'){state[action==='config'?'config':'challenge']^=1;state.ready=false;state.message='条件已改变，旧准备失效；请队员重新确认。';}
        else if(action==='member'){state.member=!state.member;state.ready=false;state.message=state.member?'队员已加入，需要重新准备。':'队员离开，挑战入口关闭。';}
        else if(action==='tickets'){state.tickets=state.tickets?0:2;state.message=state.tickets?'演示挑战券恢复为 2 张。':'挑战券不足，不消耗任何资源。';}
        else if(action==='start'&&state.member&&state.ready&&state.tickets>=1){if(state.fail){state.fail=false;state.ready=false;state.message='模拟校验失败：保留挑战券，回到未准备状态，请重新确认。';}else{state.tickets--;state.phase='battle';state.message='条件校验通过：扣除 1 张演示券，进入挑战。开始按钮已锁定。';}}
      }else if(action==='apply'){const x=candidates[state.selected];if(x.speed>=130||x.crit<90)return;state.current=state.selected;state.message='候选已应用。可以继续比较，或重置恢复初始方案。';}
      draw();root.querySelector(`[data-demo-action="${action}"]`)?.focus({preventScroll:true});
    });
    root.addEventListener('change',event=>{if(event.target.matches('[data-demo-fail]'))state.fail=event.target.checked;if(event.target.matches('[data-demo-candidate]')){const i=Number(event.target.value);if(!Number.isInteger(i)||!candidates[i])return;state.selected=i;state.message='已更新预览；当前应用方案尚未改变。';draw();root.querySelector('[data-demo-candidate]').focus({preventScroll:true});}});
    draw();
  }
  function diagramControls(container){
    for(const diagram of container.querySelectorAll('.mermaid')){
      if(diagram.dataset.zoomReady||!diagram.querySelector('svg'))continue;
      diagram.dataset.zoomReady='true';
      const button=document.createElement('button');button.type='button';button.className='diagram-expand';button.textContent='放大查看流程图 ↗';diagram.before(button);
      button.addEventListener('click',()=>{
        const svg=diagram.querySelector('svg').cloneNode(true),box=svg.viewBox.baseVal;
        const width=Math.max(600,box.width||900),height=box.width?width*box.height/box.width:700;
        svg.setAttribute('width',width);svg.setAttribute('height',height);svg.style.maxWidth='none';
        const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}));
        const dialog=document.createElement('dialog');dialog.className='diagram-dialog';dialog.setAttribute('aria-label','放大流程图');
        dialog.innerHTML='<header><b>流程图 · 可横向与纵向滚动</b><button type="button">关闭 ×</button></header><div class="diagram-viewport"></div>';
        const img=document.createElement('img');img.src=url;img.alt='放大的流程图，图中内容对应正文规则';img.style.width=width+'px';img.style.height=height+'px';dialog.querySelector('.diagram-viewport').append(img);
        dialog.querySelector('button').onclick=()=>dialog.close();dialog.addEventListener('close',()=>{URL.revokeObjectURL(url);dialog.remove();button.focus({preventScroll:true});},{once:true});document.body.append(dialog);dialog.showModal();
      });
    }
  }
  function route(){
    readingHeadings=[];readingObserver?.disconnect();readingObserver=null;renderToken++;
    if($('#view-library').hidden){activeVisit=null;pendingParent=null;returnVisit=null;return;}
    const savedPosition=beginVisit();delete $('#view-library').dataset.readyRoute;
    const id=location.hash.startsWith('#library/')?location.hash.slice(9):'',doc=D.docs[id],games=location.hash==='#games';
    const nav=games||D.games.some(g=>g.id===id)?'games':'library';
    for(const a of document.querySelectorAll('[data-nav]')){a.classList.toggle('active',a.dataset.nav===nav);if(a.dataset.nav===nav)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
    $('#breadcrumb').textContent=nav==='games'?'游戏拆解库':'系统案例库';
    $('#game-library').hidden=!games;$('#library-list').hidden=!!id||games;$('#library-detail').hidden=!id;
    if(games){if(savedPosition?.gameSearch){gameQuery=savedPosition.gameSearch.query;gameFilters=structuredClone(savedPosition.gameSearch.filters);}gameList();restorePosition(savedPosition,renderToken);return;}
    if(!id){list();restorePosition(savedPosition,renderToken);return;}
    if(!doc){$('#library-detail').innerHTML='<a href="#library">← 返回案例库</a><h1>这个案例暂时不存在</h1>';return;}
    const s=D.systems.find(s=>s.id===id),g=game(s?.gameId||doc.gameId);
    $('#library-detail').innerHTML=`<header class="reader-masthead"><p>${s?'系统拆解':'游戏拆解'}</p><div class="reader-game-title">${e(g?.title||doc.title)}</div>${s?`<a href="#library/${g.id}">查看整游分析与系统地图 ↗</a>`:''}</header>${doc.readerEdition?`<div class="reader-edition">游戏分析样稿 · ${e(g?.platform||'资料分析')} · 资料核读 ${e(g?.asOf||D.asOf)}<span>原作依据随文引用；作者分析与补充设计分别说明。</span></div>`:`<div class="evidence-note"><b>阅读标记：F 原作事实 · I 分析推断 · P 补充参考设计 · U 未核实</b><p>${e(s?.evidenceWarning||g?.scope||'跨模块参考文档')}。P 参考规格尚未实现和进行玩法测试。</p></div>`}<div class="reader-layout"><aside class="reader-toc"><nav class="reader-return" aria-label="阅读导航"><a href="${e(parentLink(doc))}" data-reader-back>← 返回上一层</a><a href="#library" data-reader-home title="游戏种子主页">返回主页</a></nav><details class="reader-contents" open><summary>本文目录</summary><nav id="case-toc"></nav></details></aside><article class="case-document" id="case-document">${doc.html}</article></div>${doc.referenceHtml?`<details class="dev-reference" data-reference-id="${id}"><summary>开发参考附录 · 补充方案，非原作规则</summary><p>${s?.referenceStatus==='calculation-tested-service-unimplemented'?'本页配置计算器已通过数值与边界检查；真实账号服务、数据库事务与完整客户端尚未实现。':s?.referenceStatus==='frontend-demo'?'本页交互样稿仅实现标明的前端状态演示；完整战斗、服务器及事务用例尚未实现。':'展开查看有限范围的可开发参考规格，尚未实现或进行玩法测试。'}所有演示参数、接口与异常策略均属补充设计。</p><div class="reference-content case-document"></div></details>`:''}${s?`<section class="case-notes panel"><h2>我的用途与笔记</h2><label for="case-note">收藏后可记录借鉴目标、取舍与待验证问题</label><textarea id="case-note" rows="4" maxlength="20000" placeholder="例如：借鉴批量分解前的保护规则，用于我的刷宝游戏。">${e(favorites[id]?.note||'')}</textarea><button class="button secondary" id="save-case-note" data-id="${id}">保存笔记并收藏</button><span id="case-note-status" role="status"></span></section>`:''}`;
    document.querySelectorAll('#case-document [data-demo]').forEach(mountDemo);
    const title=$('#case-document h1');if(title){const header=document.createElement('header');header.className='system-title';title.before(header);header.append(title);if(s)header.insertAdjacentHTML('beforeend',`<button class="button secondary" data-case-save="${id}" aria-pressed="${!!favorites[id]}">${favorites[id]?'♥ 已收藏':'♡ 收藏系统'}</button>`);}
    if(innerWidth<=1100)$('.reader-contents').open=false;
    const appendix=$('.dev-reference');if(appendix)appendix.addEventListener('toggle',()=>{if(appendix.open&&!appendix.dataset.loaded){appendix.dataset.loaded='true';appendix.querySelector('.reference-content').innerHTML=doc.referenceHtml;const nodes=[...appendix.querySelectorAll('.mermaid')];if(nodes.length)window.LibraryMermaid?.run({nodes}).catch(()=>{$('#library-warning').textContent='附录流程图暂未渲染，可阅读规则文字。';});}});
    for(const extra of document.querySelectorAll('#library-detail>.dev-reference,#library-detail>.case-notes'))$('#case-document').append(extra);
    readingHeadings=[...$('#case-document').querySelectorAll('h2,h3,.dev-reference>summary')];readingHeadings.forEach((h,i)=>{h.id='section-'+i;});$('#case-toc').innerHTML=readingHeadings.map((h,i)=>`<button type="button" data-scroll-section="section-${i}" class="${h.tagName==='H3'?'subheading':''}">${e(h.textContent)}</button>`).join('');
    $('.reader-contents summary').insertAdjacentHTML('beforeend','<span id="reading-position"></span>');
    $('.reader-contents').addEventListener('toggle',()=>updateReadingPosition(true));
    readingObserver=new ResizeObserver(()=>updateReadingPosition());readingObserver.observe($('#case-document'));
    const token=renderToken,diagrams=[...$('#case-document').querySelectorAll('.mermaid')];
    const ready=diagrams.length&&window.LibraryMermaid?window.LibraryMermaid.run({nodes:diagrams}).catch(()=>{if(token===renderToken)$('#library-warning').textContent='部分流程图暂未渲染，可阅读图中规则文本及机制示意图。';}):Promise.resolve();
    Promise.all([ready,document.fonts.ready,...[...$('#case-document').querySelectorAll('img')].filter(img=>img.loading!=='lazy'||!img.hasAttribute('width')).map(img=>img.decode().catch(()=>{}))]).then(()=>{if(token!==renderToken)return;diagramControls($('#case-document'));restorePosition(savedPosition,token);});
  }
  $('#game-filter').insertAdjacentHTML('beforeend',D.games.map(g=>`<option value="${g.id}">${e(g.title)}</option>`).join(''));
  $('#system-filter').insertAdjacentHTML('beforeend',Object.entries(types).map(([id,t])=>`<option value="${id}">${t}</option>`).join(''));
  $('#system-search').addEventListener('input',list);for(const id of ['game-filter','system-filter','mode-filter','evidence-filter','only-saved'])$('#'+id).addEventListener('change',list);
  $('#view-library').addEventListener('click',event=>{const b=event.target.closest('button');if(!b)return;
    if(b.dataset.caseSave){const id=b.dataset.caseSave;if(save(id,favorites[id]?null:{note:''})){list();if(location.hash.startsWith('#library/')){b.textContent=favorites[id]?'♥ 已收藏':'♡ 收藏系统';b.setAttribute('aria-pressed',String(!!favorites[id]));}}}
    if(b.dataset.scrollSection){if(innerWidth<=1100)$('.reader-contents').open=false;requestAnimationFrame(()=>{document.getElementById(b.dataset.scrollSection)?.scrollIntoView({block:'start'});updateReadingPosition(true);});}
    if(b.id==='save-case-note'){if(save(b.dataset.id,{note:$('#case-note').value})){$('#case-note-status').textContent='已保存在此浏览器';const f=$('#library-detail [data-case-save]');f.textContent='♥ 已收藏';f.setAttribute('aria-pressed','true');}}
    if(b.id==='clear-system-filters'){for(const id of ['game-filter','system-filter','mode-filter'])$('#'+id).value='';$('#evidence-filter').value='all';$('#system-search').value='';$('#only-saved').checked=false;list();}
  });
  $('#export-cases').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,favorites},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='game-system-favorites.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  $('#import-cases').onclick=()=>$('#case-backup-input').click();
  $('#case-backup-input').onchange=async event=>{const f=event.target.files[0];event.target.value='';if(!f)return;try{if(f.size>1024*1024)throw Error('文件超过 1 MB');const imported=validate(JSON.parse(await f.text()));const raw=localStorage.getItem(KEY);const latest=raw?validate(JSON.parse(raw)):{};favorites={...imported,...latest};localStorage.setItem(KEY,JSON.stringify({version:1,favorites}));storageOK=true;$('#library-warning').textContent='已合并收藏备份，同编号保留当前笔记。';list();}catch(err){$('#library-warning').textContent='导入失败：'+err.message;}};
  window.addEventListener('storage',event=>{if(event.key===KEY){read();list();}});
  window.addEventListener('hashchange',route);window.LibraryMermaid?.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral',fontFamily:'Microsoft YaHei, sans-serif',suppressErrorRendering:true});read();route();
})();
