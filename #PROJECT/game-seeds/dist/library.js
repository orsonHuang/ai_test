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
      window.scrollTo({top:y,behavior:'instant'});if($('#case-toc'))$('#case-toc').scrollTop=saved?.toc||0;$('#view-library').dataset.readyRoute=location.hash||'#library';
    }));
  }
  function parentLink(doc){const parent=visits[activeVisit?.parent];return parent?.hash||((doc&&doc.gameId!==location.hash.slice(9))?'#library/'+doc.gameId:'#library');}
  document.addEventListener('click',event=>{
    const a=event.target.closest('a');if(!a||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||a.target==='_blank')return;
    const hash=a.getAttribute('href');if(!hash?.startsWith('#library'))return;
    rememberPosition();if(hash===(location.hash||'#library'))return;
    if(a.hasAttribute('data-reader-back')){returnVisit=activeVisit?.parent||null;pendingParent=null;}
    else if(a.hasAttribute('data-reader-home')){pendingParent=null;returnVisit=null;}
    else pendingParent=activeVisit?.key||null;
  },true);
  let scrollFrame=0;
  window.addEventListener('scroll',()=>{cancelAnimationFrame(scrollFrame);scrollFrame=requestAnimationFrame(rememberPosition);},{passive:true});
  window.addEventListener('pagehide',rememberPosition);
  history.scrollRestoration='manual';

  function route(){
    const savedPosition=beginVisit();delete $('#view-library').dataset.readyRoute;
    const id=location.hash.startsWith('#library/')?location.hash.slice(9):'',doc=D.docs[id];renderToken++;
    $('#library-list').hidden=!!id;$('#library-detail').hidden=!id;
    if(!id){list();restorePosition(savedPosition,renderToken);return;}
    if(!doc){$('#library-detail').innerHTML='<a href="#library">← 返回案例库</a><h1>这个案例暂时不存在</h1>';return;}
    const s=D.systems.find(s=>s.id===id),g=game(s?.gameId||doc.gameId);
    $('#library-detail').innerHTML=`<header class="reader-masthead"><p>${s?'系统拆解':'游戏拆解'}</p><div class="reader-game-title">${e(g?.title||doc.title)}</div>${s?`<a href="#library/${g.id}">查看整游分析与系统地图 ↗</a>`:''}</header>${doc.readerEdition?'<div class="reader-edition">游戏分析样稿 · 手机 App · 资料核读 2026-10-16<span>原作依据随文引用；作者分析与补充设计分别说明。</span></div>':`<div class="evidence-note"><b>阅读标记：F 原作事实 · I 分析推断 · P 补充参考设计 · U 未核实</b><p>${e(s?.evidenceWarning||g?.scope||'跨模块参考文档')}。P 参考规格尚未实现和进行玩法测试。</p></div>`}<div class="reader-layout"><aside class="reader-toc"><nav class="reader-return" aria-label="阅读导航"><a href="${e(parentLink(doc))}" data-reader-back>← 返回上一层</a><a href="#library" data-reader-home title="游戏种子主页">返回主页</a></nav><details class="reader-contents" open><summary>本文目录</summary><nav id="case-toc"></nav></details></aside><article class="case-document" id="case-document">${doc.html}</article></div>${doc.referenceHtml?`<details class="dev-reference" data-reference-id="${id}"><summary>开发参考附录 · 补充方案，非原作规则</summary><p>展开查看此前整理的可开发参考规格。演示参数、接口与异常策略均属补充设计，尚未实现或进行玩法测试。</p><div class="reference-content case-document"></div></details>`:''}${s?`<section class="case-notes panel"><h2>我的用途与笔记</h2><label for="case-note">收藏后可记录借鉴目标、取舍与待验证问题</label><textarea id="case-note" rows="4" maxlength="20000" placeholder="例如：借鉴批量分解前的保护规则，用于我的刷宝游戏。">${e(favorites[id]?.note||'')}</textarea><button class="button secondary" id="save-case-note" data-id="${id}">保存笔记并收藏</button><span id="case-note-status" role="status"></span></section>`:''}`;
    const title=$('#case-document h1');if(title){const header=document.createElement('header');header.className='system-title';title.before(header);header.append(title);if(s)header.insertAdjacentHTML('beforeend',`<button class="button secondary" data-case-save="${id}" aria-pressed="${!!favorites[id]}">${favorites[id]?'♥ 已收藏':'♡ 收藏系统'}</button>`);}
    if(innerWidth<=1100)$('.reader-contents').open=false;
    const appendix=$('.dev-reference');if(appendix)appendix.addEventListener('toggle',()=>{if(appendix.open&&!appendix.dataset.loaded){appendix.dataset.loaded='true';appendix.querySelector('.reference-content').innerHTML=doc.referenceHtml;const nodes=[...appendix.querySelectorAll('.mermaid')];if(nodes.length)window.LibraryMermaid?.run({nodes}).catch(()=>{$('#library-warning').textContent='附录流程图暂未渲染，可阅读规则文字。';});}});
    const headings=[...$('#case-document').querySelectorAll('h2,h3')];headings.forEach((h,i)=>{h.id='section-'+i;});$('#case-toc').innerHTML=headings.map((h,i)=>`<button type="button" data-scroll-section="section-${i}" class="${h.tagName==='H3'?'subheading':''}">${e(h.textContent)}</button>`).join('');
    for(const extra of document.querySelectorAll('#library-detail>.dev-reference,#library-detail>.case-notes'))$('#case-document').append(extra);
    const token=renderToken,diagrams=[...$('#case-document').querySelectorAll('.mermaid')];
    const ready=diagrams.length&&window.LibraryMermaid?window.LibraryMermaid.run({nodes:diagrams}).catch(()=>{if(token===renderToken)$('#library-warning').textContent='部分流程图暂未渲染，可阅读图中规则文本及机制示意图。';}):Promise.resolve();
    Promise.all([ready,document.fonts.ready,...[...$('#case-document').querySelectorAll('img')].map(img=>img.decode().catch(()=>{}))]).then(()=>restorePosition(savedPosition,token));
  }
  $('#game-filter').insertAdjacentHTML('beforeend',D.games.map(g=>`<option value="${g.id}">${e(g.title)}</option>`).join(''));
  $('#system-filter').insertAdjacentHTML('beforeend',Object.entries(types).map(([id,t])=>`<option value="${id}">${t}</option>`).join(''));
  $('#game-summaries').innerHTML=D.games.map(g=>`<a href="#library/${g.id}" class="game-summary"><small>${e(g.platform)}</small><b>${e(g.title.split(' · ')[0])}</b><span>${D.systems.filter(s=>s.gameId===g.id).length} 个模块 · 整游分析与地图 ↗</span></a>`).join('');
  $('#system-search').addEventListener('input',list);for(const id of ['game-filter','system-filter','mode-filter','evidence-filter','only-saved'])$('#'+id).addEventListener('change',list);
  $('#view-library').addEventListener('click',event=>{const b=event.target.closest('button');if(!b)return;
    if(b.dataset.caseSave){const id=b.dataset.caseSave;if(save(id,favorites[id]?null:{note:''})){list();if(location.hash.startsWith('#library/')){b.textContent=favorites[id]?'♥ 已收藏':'♡ 收藏系统';b.setAttribute('aria-pressed',String(!!favorites[id]));}}}
    if(b.dataset.scrollSection)document.getElementById(b.dataset.scrollSection).scrollIntoView({block:'start'});
    if(b.id==='save-case-note'){if(save(b.dataset.id,{note:$('#case-note').value})){$('#case-note-status').textContent='已保存在此浏览器';const f=$('#library-detail [data-case-save]');f.textContent='♥ 已收藏';f.setAttribute('aria-pressed','true');}}
    if(b.id==='clear-system-filters'){for(const id of ['game-filter','system-filter','mode-filter'])$('#'+id).value='';$('#evidence-filter').value='all';$('#system-search').value='';$('#only-saved').checked=false;list();}
  });
  $('#export-cases').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,favorites},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='game-system-favorites.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  $('#import-cases').onclick=()=>$('#case-backup-input').click();
  $('#case-backup-input').onchange=async event=>{const f=event.target.files[0];event.target.value='';if(!f)return;try{if(f.size>1024*1024)throw Error('文件超过 1 MB');const imported=validate(JSON.parse(await f.text()));const raw=localStorage.getItem(KEY);const latest=raw?validate(JSON.parse(raw)):{};favorites={...imported,...latest};localStorage.setItem(KEY,JSON.stringify({version:1,favorites}));storageOK=true;$('#library-warning').textContent='已合并收藏备份，同编号保留当前笔记。';list();}catch(err){$('#library-warning').textContent='导入失败：'+err.message;}};
  window.addEventListener('storage',event=>{if(event.key===KEY){read();list();}});
  window.addEventListener('hashchange',route);window.LibraryMermaid?.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral',fontFamily:'Microsoft YaHei, sans-serif',suppressErrorRendering:true});read();route();
})();
