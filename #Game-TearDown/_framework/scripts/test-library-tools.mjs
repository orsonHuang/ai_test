import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const scripts=path.dirname(fileURLToPath(import.meta.url));
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'game-teardown-contract-'));
const scriptFolder=path.join(scratch,'_framework','scripts');fs.mkdirSync(scriptFolder,{recursive:true});
for(const name of ['check-library.mjs','build-catalog.mjs'])fs.copyFileSync(path.join(scripts,name),path.join(scriptFolder,name));
const dir=path.join(scratch,'Fixture');fs.mkdirSync(path.join(dir,'assets'),{recursive:true});
fs.writeFileSync(path.join(dir,'README.md'),'Fixture');
fs.writeFileSync(path.join(dir,'module.md'),'fixture-system\nF01\nP参考\nREF-R01\nREF-T01\nREF-UI01\n未运行\n![图](assets/diagram.svg)');
fs.writeFileSync(path.join(dir,'assets','diagram.svg'),'<svg xmlns="http://www.w3.org/2000/svg"/>');
fs.writeFileSync(path.join(dir,'assets','reference.jpg'),'fixture-only; not a real image');
const write=(name,obj)=>fs.writeFileSync(path.join(dir,name),JSON.stringify(obj));
write('sources.json',[{id:'S1',url:'https://example.com/source',accessedAt:'2026-10-16',limitations:'fixture'}]);
const base={schemaVersion:1,id:'fixture',title:'fixture',platform:'test',asOf:'2026-10-16',scope:'fixture only',systems:[{id:'fixture-system',type:'inventory',presence:'unknown',platformApplicability:'shared-unverified',revision:1,specStatus:'reviewable',path:'module.md',facts:[{id:'F01',claim:'historical shared source',sources:['S1']}],tags:[],media:[{id:'m1',path:'assets/diagram.svg',kind:'original-diagram',caption:'fixture',publication:'original',sources:[]},{id:'m2',path:'assets/reference.jpg',kind:'original-screenshot',caption:'reference',publication:'reference-only',sources:['S1']}],related:[]}]};
const run=name=>spawnSync(process.execPath,[path.join(scriptFolder,name),'Fixture'],{encoding:'utf8'});
let passed=0;
function check(mutate,expected){const data=structuredClone(base);mutate(data);write('game.json',data);const r=run('check-library.mjs');const report=JSON.parse(r.stdout);assert.equal(r.status,expected?1:0,r.stderr);if(expected)assert.ok(report.errors.some(e=>e.includes(expected)),r.stdout);passed++;}
check(()=>{},null);
check(g=>g.systems.push(structuredClone(g.systems[0])),'duplicate ID');
check(g=>g.systems[0].facts[0].sources=['missing'],'unknown source');
check(g=>g.systems[0].media[0].path='assets/missing.svg','missing media');
check(g=>g.systems[0].presence='present','shared source cannot confirm');
write('game.json',base);let r=run('build-catalog.mjs');assert.equal(r.status,0,r.stderr);
const cat=JSON.parse(fs.readFileSync(path.join(scratch,'catalog.json'),'utf8'));
const media=JSON.parse(fs.readFileSync(path.join(scratch,'public-media.json'),'utf8'));
assert.equal(cat.systems[0].defaultDiscoverable,false);passed++;
assert.equal(media.media.length,1);assert.equal(media.media[0].path,'Fixture/assets/diagram.svg');passed++;
// Keep the tiny scratch fixture for diagnostics; never recursively delete computed paths.
console.log(JSON.stringify({passed,scratch,scope:'Negative structural and export-boundary tests only; no gameplay behavior executed.'}));
