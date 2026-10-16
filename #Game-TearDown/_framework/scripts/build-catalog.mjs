import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const dirs=process.argv.slice(2);
if(!dirs.length) throw new Error('Pass explicit game directories; do not silently migrate legacy cases.');
const catalog={schemaVersion:1,asOf:'2026-10-16',publicationStatus:'local-review',games:[],systems:[]};
const media=new Map(); const ids=new Set();
for(const dir of dirs){
  const folder=path.resolve(root,dir);
  if(!folder.startsWith(root+path.sep)) throw new Error('Game directory outside library');
  const g=JSON.parse(fs.readFileSync(path.join(folder,'game.json'),'utf8'));
  catalog.games.push({id:g.id,title:g.title,platform:g.platform,build:g.build,asOf:g.asOf,scope:g.scope,playModes:g.playModes,businessModels:g.businessModels,operationModels:g.operationModels,indexPath:`${dir}/README.md`,manifestPath:`${dir}/game.json`});
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
for(const s of catalog.systems)for(const id of s.related||[])if(!ids.has(id))throw new Error(`Unknown related ID ${id}`);
for(const [file,data] of [['catalog.json',catalog],['public-media.json',{schemaVersion:1,scope:'Media allowlist only; not a deployable package. Research-only images are excluded.',media:[...media.values()]}]]){
  const dest=path.join(root,file);if(fs.existsSync(dest))fs.readFileSync(dest,'utf8');
  fs.writeFileSync(dest,JSON.stringify(data,null,2)+'\n');
}
console.log(JSON.stringify({games:catalog.games.length,systems:catalog.systems.length,defaultDiscoverable:catalog.systems.filter(s=>s.defaultDiscoverable).length,referenceOnlyCases:catalog.systems.filter(s=>!s.defaultDiscoverable).length,publicMedia:media.size}));
