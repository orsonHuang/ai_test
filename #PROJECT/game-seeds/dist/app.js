(() => {
  'use strict';
  const E=window.SeedEngine;
  const KEY='game-seeds-v1';
  const $=selector=>document.querySelector(selector);
  const $$=selector=>Array.from(document.querySelectorAll(selector));
  const escape=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  let corrupted=false, storageSnapshot=null;
  let state={version:1,sources:[],ideas:E.initialIdeas(),brief:{...E.DEFAULT_BRIEF}};
  try {
    const stored=localStorage.getItem(KEY);storageSnapshot=stored;
    if (stored) state=E.parseBackup(stored);
  } catch {
    corrupted=true;
    warn('无法读取浏览器中的记录。当前改动仅在本次打开保留，请导出备份；原有数据不会被覆盖。');
  }
  let page='discover', filter='all', selectedId=null, detailTab='concept', toastTimer;
  let lastMining=null;
  function warn(message) { $('#storage-warning').textContent=message; $('#storage-warning').hidden=false; }
  function persist() {
    if (corrupted) return false;
    try {
      if(localStorage.getItem(KEY)!==storageSnapshot){warn('另一个标签页更新了资料。为避免覆盖，当前改动仅保留在本次打开；请先导出备份，再刷新并合并。');return false;}
      const next=JSON.stringify(state);localStorage.setItem(KEY,next);storageSnapshot=next;$('#storage-warning').hidden=true;return true;
    }
    catch { warn('浏览器存储不可用或空间已满。当前改动仍可操作，但刷新后可能丢失，请立即导出备份。'); return false; }
  }
  function toast(message) { clearTimeout(toastTimer); $('#toast').textContent=message; $('#toast').hidden=false; toastTimer=setTimeout(()=>$('#toast').hidden=true,3800); }
  function download(name,content,type='text/plain;charset=utf-8') {
    const url=URL.createObjectURL(new Blob([content],{type}));
    const link=document.createElement('a'); link.href=url; link.download=name; document.body.append(link); link.click(); link.remove(); setTimeout(()=>URL.revokeObjectURL(url),2000);
  }
  function filename(title) { return title.replace(/[<>:"/\\|?*\x00-\x1F]/g,'-').slice(0,70)||'游戏创意'; }
  function today() { return new Date().toLocaleDateString('en-CA'); }
  function link(url,label) { const safe=E.safeURL(url); return safe?`<a href="${escape(safe)}" target="_blank" rel="noopener noreferrer">${escape(label)} ↗</a>`:'<span class="muted">未提供来源链接</span>'; }
  function empty(title,message,button,route) { return `<div class="empty-state"><h3>${escape(title)}</h3><p>${escape(message)}</p>${button?`<button type="button" class="button secondary" data-go="${escape(route)}">${escape(button)}</button>`:''}</div>`; }
  function card(idea) {
    const glyphs={mint:['⌕','?','✓'],lilac:['◇','↔','✧'],peach:['▥','⚙','↗'],rose:['✧','♡','⌂'],sky:['☁','✳','☀'],sand:['▦','◇','+']};
    const glyph=glyphs[idea.color]||glyphs.mint;
    return `<article class="idea-card ${escape(idea.color)}" data-card-id="${escape(idea.id)}"><div class="card-art"><span class="card-type">${idea.demo?'演示灵感':'我的挖掘'}</span><button type="button" class="favorite-button" data-favorite="${escape(idea.id)}" aria-label="${idea.favorite?'取消收藏':'收藏'}${escape(idea.title)}" aria-pressed="${idea.favorite}">${idea.favorite?'♥':'♡'}</button><div class="art-tiles" aria-hidden="true">${glyph.map(g=>`<span>${g}</span>`).join('')}</div></div><div class="card-body"><div class="card-meta"><span>${escape(idea.genre)}</span><span class="dot"></span><span>${escape(E.METHODS[idea.method])}</span></div><h3><button type="button" class="card-title" data-open="${escape(idea.id)}">${escape(idea.title)}</button></h3><p>${escape(idea.pitch)}</p><footer class="card-footer"><span>${idea.demo?'虚构示例':idea.evidence.length+' 条来源线索'} · ${escape(idea.status)}</span><button type="button" class="card-open" data-open="${escape(idea.id)}" aria-label="查看${escape(idea.title)}">查看创意 ↗</button></footer></div></article>`;
  }
  function renderCollection() {
    const query=$('#idea-search').value.trim().toLowerCase();
    const ideas=state.ideas.filter(x=>(filter==='all'||(filter==='demo'?x.demo:!x.demo))&&[x.title,x.pitch,x.genre,x.theme,E.METHODS[x.method]].join(' ').toLowerCase().includes(query));
    $('#idea-grid').innerHTML=ideas.length?ideas.map(card).join(''):empty('还没有找到这颗种子','试试其他关键词，或从自己的资料开始挖掘。','去挖掘','mine');
    $('#idea-summary').textContent=`${ideas.length} 个方向 · 演示与导入资料已标记`;
    $$('[data-filter]').forEach(button=>button.setAttribute('aria-pressed',String(filter===button.dataset.filter)));
    const status=$('#status-filter').value;
    const saved=state.ideas.filter(x=>x.favorite&&(status==='all'||x.status===status));
    $('#saved-grid').innerHTML=saved.length?saved.map(card).join(''):empty(status==='all'?'留住一颗感兴趣的种子':'这个阶段还没有创意','点击创意卡上的爱心，收藏后可以继续记录验证进展。','发现灵感','discover');
    $('#saved-count').textContent=state.ideas.filter(x=>x.favorite).length;
  }
  function renderSources() {
    $('#source-count').textContent=state.sources.length;
    $('#source-list').innerHTML=state.sources.length?state.sources.map(source=>{
      const rule=E.RULES.find(x=>x.id===source.topic);
      const content=source.content.length>360?`<p>${escape(source.content.slice(0,260))}…</p><details><summary>展开完整资料</summary><p>${escape(source.content)}</p></details>`:`<p>${escape(source.content)}</p>`;
      return `<article class="source-item"><header><h3>${escape(source.title)}</h3><div class="source-actions"><button type="button" data-edit-source="${escape(source.id)}">编辑</button><button type="button" class="remove-source" data-remove-source="${escape(source.id)}">删除</button></div></header><div class="source-meta">${escape(source.type)} · ${rule?escape(rule.label):'自动识别主题'}${source.demo?' · 演示资料':''}</div>${content}<footer>${link(source.url,'查看原始来源')}<span class="muted">${source.demo?'虚构示例':'用户录入 · 未独立核实'}</span></footer></article>`;
    }).join(''):empty('资料架上还是空的','把原始反馈和自己的观察存下来，之后每个创意都能回到源头。');
    updateCorpusNote();
  }
  function updateCorpusNote() {
    $('#corpus-note').innerHTML=$('#corpus').value==='demo'?`${E.DEMO_SOURCES.length} 条虚构示例，仅用于体验流程。`:`${state.sources.length} 条已保存资料${state.sources.length?'将参与本次挖掘。':'。<button type="button" class="text-button" data-go="sources">去添加 →</button>'}`;
  }
  function renderMining() {
    if (!lastMining) return;
    const {signals,ideas,message}=lastMining;
    $('#mining-output').innerHTML=`<div class="signal-summary"><p>${escape(message)}</p>${signals.length?`<div class="signal-tags">${signals.map(x=>`<span>${escape(x.label)} · ${x.count} 条相关资料</span>`).join('')}</div>`:''}</div>${ideas.length?`<div class="idea-grid">${ideas.map(i=>card(state.ideas.find(x=>x.id===i.id)||i)).join('')}</div><p class="method-note">候选已加入发现灵感。数字是主题相关资料数，不是独立玩家人数或需求强度。</p>`:empty('给线索一点上下文','编辑资料时可手动指定主题，让工具理解你想探索的角度。','编辑资料','sources')}`;
  }
  function refresh() { renderCollection(); renderSources(); renderMining(); }
  function route() {
    const next=location.hash.slice(1).split('/')[0];
    page=['games','library','discover','mine','sources','saved'].includes(next)?next:'library';
    $$('.view').forEach(view=>view.hidden=view.id!=='view-'+(page==='games'?'library':page));
    $$('[data-nav]').forEach(nav=>{ nav.classList.toggle('active',nav.dataset.nav===page); if(nav.dataset.nav===page)nav.setAttribute('aria-current','page');else nav.removeAttribute('aria-current'); });
    $('#breadcrumb').textContent={games:'游戏拆解库',library:'系统案例库',discover:'发现灵感',mine:'挖掘工作台',sources:'我的资料',saved:'收藏与验证'}[page];
    if (page==='mine') updateCorpusNote();
    window.scrollTo({top:0,behavior:'instant'});
  }
  function openSource(source, content, title) {
    const form=$('#source-form'); form.reset(); $('#source-error').textContent='';
    $('#source-dialog-title').textContent=source?'编辑资料':'添加一条资料';
    if (source) for(const key of ['id','title','url','type','topic','content'])form.elements.namedItem(key).value=source[key]||'';
    else {form.elements.namedItem('id').value=''; if(content)form.elements.namedItem('content').value=content; if(title)form.elements.namedItem('title').value=title;}
    $('#source-dialog').showModal();
  }
  function idea() { return state.ideas.find(x=>x.id===selectedId); }
  function renderDetail(focusTab=false) {
    const item=idea(); if(!item)return;
    let body='';
    if(detailTab==='concept') body=`<section class="detail-section"><h3>为谁设计</h3><p>${escape(item.audience)}</p></section><section class="detail-section"><h3>核心循环</h3><div class="loop">${item.loop.map((step,i)=>`${i?'<i aria-hidden="true">→</i>':''}<span>${escape(step)}</span>`).join('')}</div></section><section class="detail-section"><h3>制作风险</h3><p>${escape(item.risk)}</p></section><section class="detail-section"><h3>先找反例</h3><p>${escape(item.counter)}</p></section>`;
    if(detailTab==='evidence') body=`<div class="detail-note">${item.demo?'这里的资料均为虚构示例，不能用作市场需求证据。':'资料由用户录入，尚未独立核实。关键词命中只提示主题相关，无法判断否定、讽刺或真实需求。'}</div>${item.evidence.map(e=>`<article class="evidence"><b>${escape(e.title)}</b><blockquote>${escape(e.excerpt)}</blockquote>${link(e.url,'回到原始来源')}<small>${e.demo?'演示资料':e.manual?'包含人工指定主题':'关键词匹配'}${e.hits.length?' · '+escape(e.hits.join('、')):''}</small></article>`).join('')||'<p class="muted">这张创意卡暂时没有来源线索。</p>'}`;
    if(detailTab==='prototype') body=`<div class="detail-note">原型验证预算：${escape(item.brief.budget)} · ${escape(item.brief.team)} · ${escape(item.brief.platform)}<br>这是你设定的验证边界，实际范围需根据能力调整。</div><section class="detail-section"><h3>最小原型做什么</h3><p>${escape(item.prototype)}</p></section><section class="detail-section"><h3>用什么观察判断</h3><p>${escape(item.test)}</p></section><section class="detail-section"><h3>验证记录</h3><div class="record-toolbar"><label>当前状态<select id="record-status">${E.STATUSES.map(status=>`<option${item.status===status?' selected':''}>${escape(status)}</option>`).join('')}</select></label></div><label>试玩、发现与下一步<textarea id="record-notes" rows="5" maxlength="20000" placeholder="例如：3 位玩家中有 2 位在中断后忘记线索。下一步尝试事实回顾卡。">${escape(item.notes)}</textarea></label><p class="save-note" id="note-save-status">修改会自动保存在此浏览器。标记「已验证」时，请留下具体证据。</p></section>`;
    $('#idea-detail').innerHTML=`<header class="detail-head ${escape(item.color)}"><div class="eyebrow">${item.demo?'DEMO IDEA / 演示构想':'YOUR NEXT POSSIBILITY / 候选构想'}</div><button type="button" class="icon-button" data-close="idea-dialog" aria-label="关闭创意详情">×</button><h2>${escape(item.title)}</h2><p>${escape(item.pitch)}</p><div class="detail-badges"><span>${escape(E.METHODS[item.method])}</span><span>${escape(item.genre)}</span><span>${escape(item.brief.platform)}</span><span>${escape(item.status)}</span></div></header><div class="detail-tabs" role="tablist" aria-label="创意详情">${[['concept','创意与玩法'],['evidence','来源线索'],['prototype','原型与验证']].map(([key,title])=>`<button type="button" id="detail-tab-${key}" role="tab" aria-selected="${detailTab===key}" aria-controls="detail-panel" data-detail-tab="${key}">${title}</button>`).join('')}</div><div class="detail-content" id="detail-panel" role="tabpanel" aria-labelledby="detail-tab-${detailTab}">${body}</div><footer class="detail-actions"><button type="button" class="button primary" data-favorite="${escape(item.id)}" aria-pressed="${item.favorite}">${item.favorite?'♥ 已收藏':'♡ 收藏方向'}</button><button type="button" class="button secondary" id="export-idea">导出创意卡 ↗</button><button type="button" class="button secondary" id="copy-prompt">复制研究提示词</button></footer>`;
    if(focusTab)$('#detail-tab-'+detailTab).focus();
  }
  document.addEventListener('click',async event=>{
    const button=event.target.closest('button'); if(!button)return;
    const d=button.dataset;
    if(d.go){location.hash=d.go;return;}
    if(d.close){$('#'+d.close).close();return;}
    if(d.filter){filter=d.filter;renderCollection();return;}
    if(d.open){selectedId=d.open;detailTab='concept';renderDetail();$('#idea-dialog').showModal();return;}
    if(d.favorite){const item=state.ideas.find(x=>x.id===d.favorite);if(!item)return;item.favorite=!item.favorite;const saved=persist();refresh();if($('#idea-dialog').open)renderDetail();toast((item.favorite?'已收藏这个方向':'已取消收藏')+(saved?'':' · 尚未持久保存'));return;}
    if(d.detailTab){detailTab=d.detailTab;renderDetail(true);return;}
    if(d.editSource){openSource(state.sources.find(x=>x.id===d.editSource));return;}
    if(d.removeSource){const source=state.sources.find(x=>x.id===d.removeSource);if(source&&confirm(`删除「${source.title}」？已生成的创意卡会保留原始引用快照。`)){state.sources=state.sources.filter(x=>x.id!==source.id);persist();renderSources();toast('资料已移除，创意卡里的引用快照已保留。');}return;}
    if(button.id==='export-idea'){download(filename(idea().title)+'.md',E.markdown(idea()));toast('创意卡已导出为 Markdown。');return;}
    if(button.id==='copy-prompt'){
      const content=E.prompt(idea());
      try { if(!navigator.clipboard)throw new Error('clipboard');await navigator.clipboard.writeText(content);toast('研究提示词已复制，可粘贴到你常用的 AI 工具。'); }
      catch {download(filename(idea().title)+'-研究提示词.txt',content);toast('当前环境无法复制，已改为下载提示词。');}
    }
  });
  $('#source-form').addEventListener('submit',event=>{
    event.preventDefault();
    try{
      const raw=Object.fromEntries(new FormData(event.currentTarget));
      const existing=state.sources.find(x=>x.id===raw.id);
      const source=E.validateSource({...raw,createdAt:existing?.createdAt,demo:existing?.demo===true});
      if(existing)state.sources[state.sources.indexOf(existing)]=source;else state.sources.unshift(source);
      const saved=persist();refresh();$('#source-dialog').close();toast(saved?'资料已保存，可以开始挖掘。':'资料已加入本次工作空间，请导出备份。');
    }catch(error){$('#source-error').textContent=error.message;}
  });
  $('#mining-form').addEventListener('submit',event=>{
    event.preventDefault();
    const values=Object.fromEntries(new FormData(event.currentTarget));
    state.brief=E.normalizeBrief(values);
    const sources=values.corpus==='demo'?E.DEMO_SOURCES:state.sources;
    lastMining=E.generateIdeas(sources,state.brief);
    state.ideas.unshift(...lastMining.ideas);
    persist();refresh();
    if(lastMining.ideas.length)toast(`生成了 ${lastMining.ideas.length} 个候选方向。`);
    if(window.innerWidth<861)$('#mining-output').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
  });
  $('#idea-dialog').addEventListener('input',event=>{
    if(event.target.id!=='record-notes')return;
    const item=idea();item.notes=event.target.value;
    $('#note-save-status').textContent=persist()?'记录已保存在此浏览器。':'记录尚未持久保存，请导出备份。';
  });
  $('#idea-dialog').addEventListener('change',event=>{
    if(event.target.id!=='record-status')return;
    const item=idea();item.status=event.target.value;const saved=persist();refresh();
    const badges=$('.detail-badges');badges.lastElementChild.textContent=item.status;
    $('#note-save-status').textContent=saved?'状态已保存。请留下支持判断的试玩证据。':'状态尚未持久保存，请导出备份。';
  });
  $('#idea-search').addEventListener('input',renderCollection);
  $('#status-filter').addEventListener('change',renderCollection);
  $('#corpus').addEventListener('change',updateCorpusNote);
  $('#add-source-button').addEventListener('click',()=>openSource());
  $('#about-button').addEventListener('click',()=>$('#about-dialog').showModal());
  $('#demo-button').addEventListener('click',()=>{location.hash='mine';$('#corpus').value='demo';updateCorpusNote();});
  $('#backup-button').addEventListener('click',()=>{download('game-seeds-backup-'+today()+'.json',JSON.stringify(state,null,2),'application/json;charset=utf-8');toast('备份已导出，包含资料、创意和验证记录。');});
  $('#restore-button').addEventListener('click',()=>$('#restore-input').click());
  $('#restore-input').addEventListener('change',async event=>{
    const file=event.target.files[0];event.target.value='';if(!file)return;
    try{
      if(file.size>5*1024*1024)throw new Error('备份文件不能超过 5 MB。');
      const backup=E.parseBackup(await file.text());
      let added=0;
      for(const key of ['sources','ideas']){
        const ids=new Set(state[key].map(x=>x.id));
        for(const item of backup[key]){
          if(!ids.has(item.id)){state[key].push(item);ids.add(item.id);added++;}
          else if(key==='ideas'){
            const index=state.ideas.findIndex(x=>x.id===item.id), current=state.ideas[index];
            if(current.id.startsWith('seed-')&&!current.favorite&&!current.notes&&current.status==='待研究')state.ideas[index]=item;
          }
        }
      }
      const saved=persist();refresh();toast(`已合并 ${added} 条新记录；相同编号保留当前版本。${saved?'':'请导出备份。'}`);
    }catch(error){toast('导入失败：'+error.message);}
  });
  $('#import-text-button').addEventListener('click',()=>$('#text-input').click());
  $('#text-input').addEventListener('change',async event=>{
    const file=event.target.files[0];event.target.value='';if(!file)return;
    if(file.size>256*1024){toast('文本文件不能超过 256 KB。');return;}
    try{const content=await file.text();if(content.length>12000){toast('单条资料最多 12000 字，请先拆分文本后导入。');return;}openSource(null,content,file.name.replace(/\.txt$/i,''));}catch{toast('无法读取该文本文件，请重试。');}
  });
  $$('dialog').forEach(dialog=>dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}}));
  $('#source-topic').insertAdjacentHTML('beforeend',E.RULES.map(rule=>`<option value="${rule.id}">${rule.label}</option>`).join(''));
  for(const [key,value]of Object.entries(state.brief)){const control=$('#mining-form').elements.namedItem(key);if(control){control.value=value;if(control.tagName==='SELECT'&&control.selectedIndex<0)control.selectedIndex=0;}}
  window.addEventListener('hashchange',route);
  window.addEventListener('storage',event=>{if(event.key===KEY)warn('另一个标签页更新了资料。请先导出当前备份，再刷新以载入最新版本。');});
  refresh();route();
})();
