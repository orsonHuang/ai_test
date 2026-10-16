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
function walk(dir){for(const e of fs.readdirSync(path.join(root,dir),{withFileTypes:true})){const p=dir+'/'+e.name;if(e.isDirectory())walk(p);else if(p.endsWith('.md'))files.push(p);}}
for(const g of catalog.games)walk(path.posix.dirname(g.indexPath));
for(const f of ['三岗位阅读总索引','三款参考切片集成表','参考实现公共契约'])files.push('_framework/'+f+'.md');
const ids=new Map(files.map((p,i)=>[p,catalog.systems.find(s=>s.path===p)?.id||catalog.games.find(g=>g.indexPath===p)?.id||'doc-'+i]));
const mediaPaths=new Map();fs.mkdirSync(path.join(out,'media'),{recursive:true});
for(const [i,p] of [...allowed].entries()){const dest='media/diagram-'+i+'.svg';fs.copyFileSync(path.join(root,p),path.join(out,dest));mediaPaths.set(p,dest);}
const docs={};
for(const file of files){
  const markdown=fs.readFileSync(path.join(root,file),'utf8');
  const resolve=href=>path.posix.normalize(path.posix.join(path.posix.dirname(file),decodeURIComponent(href.split('#')[0])));
  const renderer={
    html({text}){return esc(text);},
    link({href,tokens}){const label=this.parser.parseInline(tokens);if(/^https?:\/\//i.test(href))return `<a href="${esc(href)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`;const id=ids.get(resolve(href));return id?`<a href="#library/${id}">${label}</a>`:`<span>${label}</span>`;},
    image({href,text}){const dest=mediaPaths.get(resolve(href));return dest?`<figure><a href="./${dest}" target="_blank" rel="noopener"><img loading="lazy" src="./${dest}" alt="${esc(text)}"></a><figcaption>${esc(text)} · 原创示意图，点击放大</figcaption></figure>`:`<p class="research-image">研究引用图：${esc(text)}。公开版请通过本篇来源链接查看原图。</p>`;},
    code({text,lang}){return lang==='mermaid'?`<pre class="mermaid">${esc(text)}</pre>`:`<pre><code>${esc(text)}</code></pre>`;},
    table(token){return `<div class="table-scroll">${marked.Renderer.prototype.table.call(this,token)}</div>`;}
  };
  // Instance-local renderer prevents path handling from leaking between documents.
  const parser=new Marked({renderer});
  docs[ids.get(file)]={id:ids.get(file),title:markdown.match(/^# (.+)/m)?.[1]||path.basename(file),html:parser.parse(markdown),search:markdown,gameId:catalog.games.find(g=>file.startsWith(path.posix.dirname(g.indexPath)+'/'))?.id};
}
const payload={asOf:catalog.asOf,games:catalog.games,systems:catalog.systems.map(s=>({...s,media:s.media.filter(m=>allowed.has(m.path)).map(m=>({...m,path:mediaPaths.get(m.path)}))})),docs};
fs.writeFileSync(path.join(out,'library-data.js'),'window.GameLibrary='+JSON.stringify(payload).replace(/</g,'\\u003c')+';\n');
await build({stdin:{contents:"import mermaid from 'mermaid'; window.LibraryMermaid=mermaid;",resolveDir:project},bundle:true,minify:true,format:'iife',outfile:path.join(out,'mermaid.js'),legalComments:'eof'});
console.log(JSON.stringify({systems:payload.systems.length,documents:Object.keys(docs).length,publicImages:mediaPaths.size}));
