import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const selected = process.argv.slice(2);
if (!selected.length) throw new Error('Pass explicit game directory names. Legacy cases are not implicitly validated.');
const errors=[], warnings=[], ids=new Set();
const types=new Set(['combat','build','inventory','equipment','progression','economy','level','arena','coop','social','narrative','collection','monetization','liveops','onboarding','settings']);
const localFile=(dir,p)=> {
  const resolved=path.resolve(dir,p);
  return resolved.startsWith(root+path.sep) && fs.existsSync(resolved) && fs.statSync(resolved).isFile();
};
for (const name of selected) {
  const dir=path.resolve(root,name);
  if(!dir.startsWith(root+path.sep)) {errors.push(`${name}: outside library`); continue;}
  for(const required of ['README.md','sources.json','game.json']) if(!localFile(dir,required)) errors.push(`${name}: missing ${required}`);
  if(!localFile(dir,'game.json') || !localFile(dir,'sources.json')) continue;
  let game,sources;
  try {game=JSON.parse(fs.readFileSync(path.join(dir,'game.json'),'utf8'));sources=JSON.parse(fs.readFileSync(path.join(dir,'sources.json'),'utf8'));} catch(e){errors.push(`${name}: ${e.message}`);continue;}
  const sourceIds=new Set(sources.map(s=>s.id));
  if(sourceIds.size!==sources.length) errors.push(`${name}: duplicate source IDs`);
  if(game.schemaVersion!==1 || !game.id || !game.platform || !game.scope || !game.asOf) errors.push(`${name}: missing game scope fields`);
  for(const s of sources) if(!s.id || !s.url?.startsWith('https://') || !s.accessedAt || !s.limitations) errors.push(`${name}: incomplete source ${s.id}`);
  for(const system of game.systems || []) {
    if(ids.has(system.id)) errors.push(`${system.id}: duplicate ID`); ids.add(system.id);
    if(!['present','unknown','absent','out-of-scope'].includes(system.presence)) errors.push(`${system.id}: invalid presence`);
    if(!types.has(system.type)) errors.push(`${system.id}: invalid system type`);
    if(!Number.isInteger(system.revision)||system.revision<1) errors.push(`${system.id}: invalid revision`);
    if(system.platformApplicability==='shared-unverified'&&system.presence==='present') errors.push(`${system.id}: shared source cannot confirm target platform presence`);
    if(!localFile(dir,system.path)) {errors.push(`${system.id}: missing body`);continue;}
    const body=fs.readFileSync(path.join(dir,system.path),'utf8');
    if(!body.includes(system.id)) errors.push(`${system.id}: body ID mismatch`);
    for(const f of system.facts || []) {
      if(!f.id || !f.claim || !f.sources?.length) errors.push(`${system.id}: incomplete fact`);
      for(const s of f.sources||[]) if(!sourceIds.has(s)) errors.push(`${system.id}: unknown source ${s}`);
      if(!body.includes(f.id)) errors.push(`${system.id}: fact ${f.id} not in body`);
    }
    if(system.presence==='present' && !system.facts?.length) errors.push(`${system.id}: presence without evidence`);
    for(const m of system.media || []) {
      if(!localFile(dir,m.path)) errors.push(`${system.id}: missing media ${m.path}`);
      if(!m.caption || !m.kind || !['original','authorized','reference-only','unresolved'].includes(m.publication)) errors.push(`${system.id}: incomplete media metadata`);
      for(const s of m.sources||[]) if(!sourceIds.has(s)) errors.push(`${system.id}: media unknown source ${s}`);
    }
    if(!system.media?.length) warnings.push(`${system.id}: no registered local media`);
    if(system.specStatus!=='reviewable') warnings.push(`${system.id}: professional specification pending`);
    else {
      for(const [label,pattern] of [['rule ID',/[A-Z]+-R\d+/],['test ID',/[A-Z]+-T\d+/],['UI ID',/[A-Z]+-UI\d+/],['reference scope',/参考|P方案/],['test execution boundary',/未运行|尚未运行|未实测实现/]])
        if(!pattern.test(body)) errors.push(`${system.id}: reviewable spec missing ${label}`);
    }
  }
  const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);
  for(const file of walk(dir).filter(f=>f.endsWith('.md'))) {
    const body=fs.readFileSync(file,'utf8');
    for(const match of body.matchAll(/\]\(([^)]+)\)/g)) {
      const target=match[1].replace(/^<|>$/g,'');
      if (/^(https?:|#)/.test(target)) continue;
      if(!localFile(path.dirname(file),decodeURIComponent(target.split('#')[0]))) errors.push(`${path.relative(root,file)}: broken link ${target}`);
    }
  }
}
const report={checkedAt:new Date().toISOString(),games:selected,systems:ids.size,errors,warnings,scope:'Structural validation only; does not verify source truth, professional quality or original game behavior.'};
console.log(JSON.stringify(report,null,2));
process.exitCode=errors.length?1:0;
