// Offline regression checks. Run: node test-engine.cjs
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(`${__dirname}/index.html`, 'utf8');
const context = { __ROGUE_TEST__: true };
vm.createContext(context);
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
const api = context.RogueIdle;
let checks = 0;
function test(name, run) { run(); checks++; console.log(`PASS ${name}`); }
function finish(s, type = 'dungeon') {
  assert.ok(api.beginBattle(s, type));
  const b = s.battle;
  b.index = b.frames.length - 1;
  assert.ok(api.claimBattle(s));
  if (s.reward?.item) {
    const item=s.inventory.find(i=>i.id===s.reward.item);
    const desired=s.skill==='guard'?'thorn':s.skill==='burst'?'storm':'ember';
    if(item.set===desired||s.inventory.find(i=>i.id===s.equipped[item.slot])?.set===null) api.equip(s, s.reward.item);
  }
  s.reward = null;
  return b;
}
test('same seed fixes contents and equipment', () => {
  const a = api.newRun(73), b = api.newRun(73);
  delete a.started; delete b.started;
  assert.equal(JSON.stringify(a), JSON.stringify(b));
});
test('reveal one adjacent ring only; cannot skip, return or cross sideways', () => {
  const s = api.newRun(7);
  assert.deepEqual(Array.from(s.revealed).sort(), ['briar','ruins','village']);
  assert.equal(api.travel(s, 'castle'), false);
  assert.ok(api.travel(s, 'briar'));
  assert.equal(api.travel(s, 'village'), false);
  assert.equal(api.travel(s, 'ruins'), false);
  assert.ok(s.revealed.includes('river'));
  assert.equal(s.revealed.includes('frost'), false);
});
test('travel resets only AP; preview never rerolls revealed contents', () => {
  const s=api.newRun(20); api.travel(s,'briar');
  s.party[0].hp=20; s.ap=1;
  const content=JSON.stringify(s.regions.river);
  api.travel(s,'river');
  assert.equal(s.ap,6); assert.equal(s.party[0].hp,20);
  assert.equal(JSON.stringify(s.regions.river),content);
});
test('dungeon costs once; insufficient AP and duplicate claims rejected', () => {
  const s=api.newRun(1); api.travel(s,'briar');
  assert.ok(api.beginBattle(s,'dungeon')); assert.equal(s.ap,4);
  assert.equal(api.beginBattle(s,'dungeon'),false);
  assert.equal(api.claimBattle(s),false);
  s.battle.index=s.battle.frames.length-1;
  assert.ok(api.claimBattle(s)); const count=s.inventory.length,gold=s.gold;
  assert.equal(api.claimBattle(s),false);
  assert.equal(s.inventory.length,count); assert.equal(s.gold,gold);
  s.ap=1; assert.equal(api.beginBattle(s,'dungeon'),false); assert.equal(s.ap,1);
});
test('first three themed drops cover all slots; fourth remains legal', () => {
  const s=api.newRun(3), slots=[];
  for(let i=0;i<4;i++){const item=api.makeItem(s,'thorn',1);s.inventory.push(item);slots.push(item.slot);}
  assert.equal(new Set(slots.slice(0,3)).size,3); assert.equal(slots.length,4);
});
test('equipment does not grant free healing; sets count equipped items only', () => {
  const s=api.newRun(3);s.party[0].hp=15;
  const item=api.makeItem(s,'thorn',2,2);s.inventory.push(item);api.equip(s,item.id);
  assert.equal(s.party[0].hp,15);assert.equal(api.setCounts(s).thorn,1);
});
test('party limited to hero + 2, and replacement cannot remove hero', () => {
  const s=api.newRun(4);api.travel(s,'briar');
  assert.ok(api.hire(s,'ranger'));assert.equal(s.party.length,3);
  s.regions.briar.used=[];
  assert.equal(api.hire(s,'guardian'),false);
  assert.equal(api.hire(s,'guardian','hero'),false);
  assert.ok(api.hire(s,'guardian','ranger'));assert.equal(s.party.length,3);
});
test('automatic actions follow speed, only one action per living unit per round', () => {
  const s=api.newRun(9,'burst','ranger');api.travel(s,'ruins');
  const b=api.simulateBattle(s,'dungeon');
  const first=b.frames.filter(f=>f.round===1&&f.kind==='action');
  assert.equal(first[0].actor,'ranger');
  assert.equal(new Set(first.map(f=>f.actor)).size,first.length);
  assert.ok(first.some(f=>f.text.includes('猎人标记')));
});
test('battle can be serialized and claimed exactly once after recovery', () => {
  let s=api.newRun(22);api.travel(s,'briar');api.beginBattle(s,'dungeon');s.battle.index=3;
  const ap=s.ap;s=JSON.parse(JSON.stringify(s));
  assert.equal(s.ap,ap);assert.equal(s.battle.index,3);
  s.battle.index=s.battle.frames.length-1;assert.ok(api.claimBattle(s));assert.equal(api.claimBattle(s),false);
});
test('wipe ends expedition; zero AP still allows gear and travel', () => {
  const s=api.newRun(15);api.travel(s,'briar');s.ap=0;
  assert.ok(api.equip(s,s.inventory[0].id));assert.ok(api.travel(s,'river'));
  api.travel(s,'ash');api.travel(s,'castle');s.party.forEach(m=>m.hp=1);
  const b=finish(s,'final');assert.equal(b.won,false);assert.equal(s.phase,'lost');
});
test('enemy rear attack, boss telegraph and burn appear in combat log', () => {
  const s=api.newRun(33,'fire','guardian');s.current='castle';
  const b=api.simulateBattle(s,'final');const text=b.frames.map(f=>f.text).join('\n');
  assert.match(text,/袭击后排/);assert.match(text,/正在蓄力/);assert.match(text,/释放横扫/);assert.match(text,/灼烧结算/);
});
// A deliberate route: recruit, farm twice, rest, advance. Fire pivots at tier 2.
const report=[];
for(const skill of ['guard','burst','fire']){
 let wins=0, losses=[], last;
 for(let seed=1;seed<=30;seed++){
  const s=api.newRun(seed,skill,skill==='burst'?'ranger':'priest');
  const route=skill==='guard'?['briar','quarry','frost']:skill==='burst'?['ruins','river','frost']:['ruins','ember','ash'];
  for(const id of route){
   if(s.phase!=='map')break;api.travel(s,id);
   if(s.party.length<3)api.hire(s,s.regions[id].recruit);
   for(let i=0;i<2&&s.phase==='map';i++){
    if(s.party.some(m=>m.hp/api.stats(s,m).maxHp<.45)&&s.ap>=3){api.spend(s,'rest',1);api.healParty(s,.5);}
    if(s.ap>=2)finish(s);
   }
   while(s.ap>0&&s.phase==='map'){api.spend(s,'rest',1);api.healParty(s,.5);}
  }
  if(s.phase==='map'){api.travel(s,'castle');last=finish(s,'final');}
  if(s.phase==='won')wins++;else losses.push(seed);
 }
 report.push({skill,wins,seeds:30,losses,lastBattle:last?{rounds:last.rounds,hp:last.final,metrics:last.metrics}:null});
}
console.log(JSON.stringify({checks,balance:report},null,2));
assert.ok(report.every(r=>r.wins>=15),'Each intended build should win a majority of prepared test runs.');
