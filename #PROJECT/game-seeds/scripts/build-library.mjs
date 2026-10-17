import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {marked, Marked} from 'marked';
import {build} from 'esbuild';
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const root=path.resolve(project,'../../#Game-TearDown'), out=path.join(project,'dist');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'catalog.json'),'utf8'));
const allowed=new Set(JSON.parse(fs.readFileSync(path.join(root,'public-media.json'),'utf8')).media.map(m=>m.path));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const files=[];
// Reader files replace public prose, while legacy specifications keep their stable routes.
function walk(dir){for(const e of fs.readdirSync(path.join(root,dir),{withFileTypes:true})){const p=dir+'/'+e.name;if(e.isDirectory()&&e.name!=='reader')walk(p);else if(e.isFile()&&p.endsWith('.md'))files.push(p);}}
for(const g of catalog.games)walk(path.posix.dirname(g.indexPath));
for(const f of ['三岗位阅读总索引','三款参考切片集成表','参考实现公共契约'])files.push('_framework/'+f+'.md');
// Preserve published framework URLs when appending games; new roles use explicit IDs.
const fixedDocs=new Map([
  ['_framework/三岗位阅读总索引.md','doc-39'],
  ['_framework/三款参考切片集成表.md','doc-40'],
  ['_framework/参考实现公共契约.md','doc-41'],
  ['阴阳师-国服App/roles/策划阅读.md','onmyoji-role-design'],
  ['阴阳师-国服App/roles/开发阅读.md','onmyoji-role-development'],
  ['阴阳师-国服App/roles/美术阅读.md','onmyoji-role-art']
]);
const ids=new Map(files.map((p,i)=>[p,fixedDocs.get(p)||catalog.systems.find(s=>s.path===p)?.id||catalog.games.find(g=>g.indexPath===p)?.id||'doc-'+i]));
if(new Set(ids.values()).size!==ids.size)throw Error('Duplicate document routes');
const readers=new Map(),overrides=new Map(),readerSystems=new Map();
for(const g of catalog.games){
  const dir=path.posix.dirname(g.indexPath),file=path.join(root,dir,'reader.json');
  if(!fs.existsSync(file))continue;
  const r=JSON.parse(fs.readFileSync(file,'utf8'));if(r.gameId!==g.id)throw Error('Reader game mismatch');
  readers.set(g.id,r);overrides.set(g.id,path.posix.join(dir,r.overview));
  for(const s of r.systems){if(!catalog.systems.some(x=>x.id===s.id&&x.gameId===g.id))throw Error('Unknown reader system '+s.id);overrides.set(s.id,path.posix.join(dir,s.path));readerSystems.set(s.id,{...s,cover:path.posix.join(dir,s.cover)});}
}
for(const [id,file] of overrides)ids.set(file,id);
const mediaPaths=new Map(),mediaDimensions=new Map();fs.mkdirSync(path.join(out,'media'),{recursive:true});
for(const [i,p] of [...allowed].entries()){const dest='media/diagram-'+i+'.svg';const svg=fs.readFileSync(path.join(root,p),'utf8');const box=svg.match(/viewBox="[\d.-]+ [\d.-]+ ([\d.]+) ([\d.]+)"/);if(box)mediaDimensions.set(p,{width:Number(box[1]),height:Number(box[2])});fs.copyFileSync(path.join(root,p),path.join(out,dest));mediaPaths.set(p,dest);}
function systemMap(id){
  const r=readers.get(id);if(!r)throw Error('Unknown system map '+id);
  return `<div class="system-map" aria-label="可点击的系统地图">${[...new Set(r.systems.map(s=>s.group))].map(group=>`<section class="map-group"><h3>${esc(group)}</h3><div>${r.systems.filter(s=>s.group===group).map(s=>`<a href="#library/${s.id}"><b>${esc(catalog.systems.find(x=>x.id===s.id).title)} <span aria-hidden="true">↗</span></b><span>${esc(s.summary)}</span></a>`).join('')}</div></section>`).join('')}</div>`;
}
function uiAnalysis(gid,key){
  const ui=readers.get(gid)?.ui[key];if(!ui)throw Error('Unknown UI analysis '+key);
  const special={
    'yy-combat':`<div class="battle-wire"><div class="battle-field"><b>① 战场</b><p>敌方 · 血量 · 伤害反馈</p><div class="wire-duo"><span>我方单位</span><span>当前行动</span></div></div><div class="battle-order"><b>② 行动队列</b><p>当前 → 下一位</p></div><div class="battle-footer"><b>③ 鬼火与进度</b><span>④ 技能 / 自动</span></div></div>`,
    'yy-growth':`<div class="growth-wire"><div><b>① 材料列表</b><p>筛选 · 选择</p></div><div><b>② 培养对象</b><p>角色展示</p><p>培养前 → 培养后</p></div><div><b>③ 成长方式</b><p>升级<br>升星<br>转换</p></div></div><div class="wireframe-region"><b>④ 消耗与确认</b></div>`,
    coop:`<div class="wireframe-region"><div><b>① 本层挑战条件</b><div>职业增益 · 敌人特性</div></div></div><div class="wireframe-region region-1 wire-center"><div>② 挑战对象<br><span class="wire-boss">首领</span></div></div><b>③ 成员与权限</b><div class="wire-duo"><div>队长<br><strong>当前方案</strong><small>发起挑战</small></div><div>队员<br><strong>当前方案</strong><small>尚未准备 · 请离</small></div></div><div class="wireframe-region region-3"><div><b>④ 队友还未准备</b><div class="wire-controls"><span class="wire-disabled">挑战（灰置）</span><span>方案</span></div></div></div>`,
    combat:`<div class="wireframe-region"><div><b>① 战况</b><div>波次 · 防线状态</div></div></div><div class="wireframe-region region-1 wire-center"><div>② 战场<br>敌人推进 ↓<br>伤害 / 控制反馈</div></div><b>③ 场上阵列</b><div class="wire-grid">${['输出','辅助','输出','空位','控制','输出'].map(x=>`<span>${x}</span>`).join('')}</div><small>格数、位置仅为示意</small><div class="wireframe-region region-3"><div><b>④ 决策区</b><div class="wire-controls"><span>召唤 / 成本</span><span>强化选择</span></div></div></div>`,
    equipment:`<div class="wireframe-region"><div><b>① 当前装备</b><div>部位 · 所属方案</div></div></div><div class="wireframe-region region-1"><div><b>② 属性分层</b><div>基础属性</div><div>条件词条 → 作用对象</div><div>触发条件 → 实际收益</div></div></div><b>③ 调整对比</b><div class="wire-duo"><div>当前结果<small>保留项目</small></div><div>候选结果<small>变化项目</small></div></div><div class="wireframe-region region-3"><div><b>④ 本次消耗</b><div>拥有 / 所需 / 差额</div><div class="wire-controls"><span>取消</span><span>确认调整</span></div></div></div>`,
    arena:`<div class="wireframe-region"><div><b>① 挑战信息</b><div>对手 · 模式 · 比较维度</div></div></div><b>② 我的方案</b><div class="wire-duo"><div>进攻方案<small>已保存配置</small></div><div>防守方案<small>已保存配置</small></div></div><div class="wireframe-region region-1 wire-center"><div>清怪 → 对手压力<br>防线 ← 来袭威胁</div></div><div class="wireframe-region"><div><b>③ 参与条件</b><div>当前资源 / 本次消耗</div></div></div><div class="wireframe-region region-3"><div><b>④ 结算反馈</b><div>胜负 · 排名变化 · 奖励</div></div></div>`
  };
  return `<figure class="ui-analysis ${key.startsWith('yy-')?'ui-landscape':''}"><div class="ui-wireframe" role="img" aria-label="${esc(ui.title)}"><div class="wireframe-top">界面信息示意</div>${special[key]||ui.blocks.map((b,i)=>`<div class="wireframe-region region-${i}">${esc(b)}</div>`).join('')}<div class="wireframe-bottom">静态分析图 · 非游戏画面</div></div><figcaption><b>${esc(ui.title)}</b><p>${esc(ui.basis)}</p><p>编号对应下方 UI 说明，展示信息关系与交互重点。</p></figcaption></figure>`;
}
const docs={};
function render(file,gid){
  const markdown=fs.readFileSync(path.join(root,file),'utf8');
  const resolve=href=>path.posix.normalize(path.posix.join(path.posix.dirname(file),decodeURIComponent(href.split('#')[0])));
  const renderer={
    html({text}){return esc(text);},
    link({href,tokens}){const label=this.parser.parseInline(tokens);if(/^https?:\/\//i.test(href))return `<a href="${esc(href)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`;const id=ids.get(resolve(href));return id?`<a href="#library/${id}">${label}</a>`:`<span>${label}</span>`;},
    image({href,text}){const key=resolve(href),dest=mediaPaths.get(key),size=mediaDimensions.get(key);return dest?`<figure><a href="./${dest}" target="_blank" rel="noopener"><img loading="lazy" ${size?`width="${size.width}" height="${size.height}"`:''} src="./${dest}" alt="${esc(text)}"></a><figcaption>${esc(text)} · 原创示意图，点击放大</figcaption></figure>`:`<p class="research-image">研究引用图：${esc(text)}。公开版请通过本篇来源链接查看原图。</p>`;},
    code({text,lang}){if(lang==='system-map')return systemMap(text.trim());if(lang==='ui-analysis')return uiAnalysis(gid,text.trim());if(lang==='interactive-demo'){const key=text.trim();if(!['coop','souls'].includes(key))throw Error('Unknown demo '+key);return `<section class="interactive-demo" data-demo="${key}" aria-label="可操作的补充设计原型"><p>正在准备交互样稿…</p></section>`;}return lang==='mermaid'?`<pre class="mermaid">${esc(text)}</pre>`:`<pre><code>${esc(text)}</code></pre>`;},
    table(token){return `<div class="table-scroll">${marked.Renderer.prototype.table.call(this,token)}</div>`;}
  };
  // Instance-local renderer prevents path handling from leaking between documents.
  const parser=new Marked({renderer});
  return {title:markdown.match(/^# (.+)/m)?.[1]||path.basename(file),html:parser.parse(markdown),search:markdown};
}
for(const file of files){
  const id=ids.get(file),gid=catalog.games.find(g=>file.startsWith(path.posix.dirname(g.indexPath)+'/'))?.id,reader=overrides.get(id);
  docs[id]={id,...render(reader||file,gid),gameId:gid,readerEdition:!!reader};
  if(reader&&readerSystems.has(id))docs[id].referenceHtml=render(file,gid).html;
}
const payload={asOf:catalog.asOf,games:catalog.games,systems:catalog.systems.map(s=>{const reader=readerSystems.get(s.id);return {...s,readerSummary:reader?.summary,media:reader?[{kind:'original-diagram',path:mediaPaths.get(reader.cover),caption:'原创系统关系示意'}]:s.media.filter(m=>allowed.has(m.path)).map(m=>({...m,path:mediaPaths.get(m.path)}))};}),docs};
fs.writeFileSync(path.join(out,'library-data.js'),'window.GameLibrary='+JSON.stringify(payload).replace(/</g,'\\u003c')+';\n');
await build({stdin:{contents:"import mermaid from 'mermaid'; window.LibraryMermaid=mermaid;",resolveDir:project},bundle:true,minify:true,format:'iife',outfile:path.join(out,'mermaid.js'),legalComments:'eof'});
console.log(JSON.stringify({systems:payload.systems.length,documents:Object.keys(docs).length,publicImages:mediaPaths.size}));
