import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const dryRun=process.argv.includes('--check'),dirs=process.argv.slice(2).filter(x=>x!=='--check');
if(!dirs.length) throw new Error('Pass explicit game directories; do not silently migrate legacy cases.');
const catalog={schemaVersion:1,asOf:'2026-10-16',publicationStatus:'local-review',games:[],systems:[]};
const media=new Map(); const ids=new Set();
for(const dir of dirs){
  const folder=path.resolve(root,dir);
  if(!folder.startsWith(root+path.sep)) throw new Error('Game directory outside library');
  const g=JSON.parse(fs.readFileSync(path.join(folder,'game.json'),'utf8'));
  catalog.games.push({id:g.id,title:g.title,platform:g.platform,region:g.region,discovery:g.discovery,build:g.build,asOf:g.asOf,scope:g.scope,playModes:g.playModes,businessModels:g.businessModels,operationModels:g.operationModels,indexPath:`${dir}/README.md`,manifestPath:`${dir}/game.json`});
  for(const s of g.systems){
    if(ids.has(s.id)) throw new Error(`Duplicate system ID: ${s.id}`);ids.add(s.id);
    const full=path.resolve(folder,s.path);
    if(!full.startsWith(folder+path.sep)||!fs.existsSync(full))throw new Error(`Invalid body: ${s.id}`);
    catalog.systems.push({...s,gameId:g.id,platform:g.platform,asOf:g.asOf,path:`${dir}/${s.path}`,media:s.media.map(m=>({...m,path:`${dir}/${m.path}`})),
      defaultDiscoverable:s.presence==='present',referenceFilterNamespace:'referenceAttributes',evidenceWarning:s.platformApplicability==='shared-unverified'?'共用旧资料，微信适用未核实':g.scope});
    for(const m of s.media){
      if(!['original','authorized'].includes(m.publication))continue;
      const relative=`${dir}/${m.path}`;
      if(!fs.existsSync(path.resolve(root,relative)))throw new Error(`Missing media ${relative}`);
      media.set(relative,{path:relative,kind:m.kind,publication:m.publication});
    }
  }
}
// Append reader media after legacy media so existing public image paths stay stable.
for(const dir of dirs){
  const folder=path.resolve(root,dir),file=path.join(folder,'reader.json');if(!fs.existsSync(file))continue;
  const reader=JSON.parse(fs.readFileSync(file,'utf8'));
  for(const s of reader.systems){
    if(!catalog.systems.some(x=>x.id===s.id&&x.gameId===reader.gameId))throw new Error(`Unknown reader system ${s.id}`);
    for(const p of [s.path,s.cover]){const full=path.resolve(folder,p);if(!full.startsWith(folder+path.sep)||!fs.existsSync(full))throw new Error(`Invalid reader file ${p}`);}
    if(!['original','authorized'].includes(s.coverPublication))throw new Error(`Reader media is not public: ${s.id}`);
    const relative=`${dir}/${s.cover}`;media.set(relative,{path:relative,kind:'original-diagram',publication:s.coverPublication});
  }
}
for(const s of catalog.systems)for(const id of s.related||[])if(!ids.has(id))throw new Error(`Unknown related ID ${id}`);
// Keep explicitly reviewed reference images and stable image positions across rebuilds.
for(const dir of dirs){const file=path.join(root,dir,'reader.json');if(!fs.existsSync(file))continue;const r=JSON.parse(fs.readFileSync(file,'utf8'));for(const m of r.referenceMedia||[]){if(m.publication!=='editorial-reference'||m.kind!=='source-screenshot'||!/^https:\/\//.test(m.sourceUrl)||!m.sourceDate||!m.sourceAuthor)throw Error('Incomplete reference image');const relative=dir+'/'+m.path,full=path.resolve(root,relative);if(!full.startsWith(root+path.sep)||!fs.existsSync(full))throw Error('Missing reference image');media.set(relative,{...m,path:relative});}}
const oldMediaFile=path.join(root,'public-media.json');
if(fs.existsSync(oldMediaFile)){const ordered=new Map();for(const m of JSON.parse(fs.readFileSync(oldMediaFile,'utf8')).media){if(media.has(m.path)){ordered.set(m.path,media.get(m.path));media.delete(m.path);}else if(fs.existsSync(path.resolve(root,m.path))&&['original','authorized'].includes(m.publication)){ordered.set(m.path,m);}}for(const [key,value] of media)ordered.set(key,value);media.clear();for(const [key,value] of ordered)media.set(key,value);}
catalog.asOf=catalog.games.map(g=>g.asOf).sort().at(-1);
for(const [file,data] of [['catalog.json',catalog],['public-media.json',{schemaVersion:1,scope:'Media allowlist only; not a deployable package. Research-only images are excluded.',media:[...media.values()]}]]){
  const dest=path.join(root,file);if(fs.existsSync(dest))fs.readFileSync(dest,'utf8');
  if(!dryRun)fs.writeFileSync(dest,JSON.stringify(data,null,2)+'\n');
}
console.log(JSON.stringify({games:catalog.games.length,systems:catalog.systems.length,defaultDiscoverable:catalog.systems.filter(s=>s.defaultDiscoverable).length,referenceOnlyCases:catalog.systems.filter(s=>!s.defaultDiscoverable).length,publicMedia:media.size}));
