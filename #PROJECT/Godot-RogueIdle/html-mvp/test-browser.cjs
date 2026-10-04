// Run with Playwright available: node test-browser.cjs
const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const out = path.join(__dirname, 'test-output');
fs.mkdirSync(out, { recursive: true });
const url = process.env.MVP_URL || 'http://127.0.0.1:8767/';
(async () => {
 const browser = await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const context = await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const page = await context.newPage();
 const errors=[];
 page.setDefaultTimeout(8000);
 page.on('pageerror',e=>{errors.push(e.message);console.error('PAGE ERROR',e.message);});
 page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('favicon'))errors.push(m.text());});
 const screenshot=async name=>page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
 const value=fn=>page.evaluate(fn);
 const click=selector=>page.locator(selector).first().click();
 const claim=async (desired='thorn')=>{
  await click('[data-cmd="skip"]');await click('[data-cmd="claim"]');
  const phase=await value(()=>RogueIdle.state.phase);
  if(phase==='map'){
   const set=await value(()=>{let s=RogueIdle.state;return s.inventory.find(i=>i.id===s.reward?.item)?.set;});
   if(set===desired)await click('#modal [data-equip]');
   await click('[data-cmd="reward-done"]');
  }
  return phase;
 };
 const enter=async id=>{await click(`[data-region="${id}"] .region-shape`);await click(`[data-travel="${id}"]`);if(await page.locator(`[data-depart="${id}"]`).count())await click(`[data-depart="${id}"]`);};
 const fight=async type=>{await click(`[data-action="${type}"]`);await click(`[data-fight="${type}"]`);};
 await page.goto(url);
 await screenshot('01-home');
 await click('[data-cmd="start"]');
 assert.equal(await value(()=>RogueIdle.state.current),'village');
 await enter('briar');
 await screenshot('02-region');
 await click('[data-action="recruit"]');await click('[data-hire]');
 assert.equal(await value(()=>RogueIdle.state.party.length),3);
 await fight('dungeon');
 await page.waitForFunction(()=>RogueIdle.state.battle.index>=2);
 await click('[data-cmd="pause"]');
 await screenshot('03-battle');
 const saved = await value(()=>({ap:RogueIdle.state.ap,index:RogueIdle.state.battle.index}));
 await page.reload();await click('[data-cmd="continue"]');
 assert.deepEqual(await value(()=>({ap:RogueIdle.state.ap,index:RogueIdle.state.battle.index})),saved);
 await click('[data-cmd="skip"]');await click('[data-cmd="claim"]');
 await screenshot('04-reward');
 await click('#modal [data-equip]');await click('[data-cmd="reward-done"]');
 await fight('dungeon');assert.equal(await claim(),'map');
 await click('[data-action="rest"]');
 assert.equal(await value(()=>RogueIdle.state.ap),0);
 for(const id of ['quarry','frost']){
  await enter(id);
  for(let i=0;i<2;i++){await fight('dungeon');assert.equal(await claim(),'map');}
  while(await value(()=>RogueIdle.state.ap>0))await click('[data-action="rest"]');
 }
 await click('[data-cmd="gear"]');await screenshot('05-loadout');
 assert.equal(await value(()=>RogueIdle.setCounts(RogueIdle.state).thorn),3);
 await click('[data-tab="tactics"]');
 await page.locator('[data-config="passive"]').selectOption('regen');
 assert.equal(await value(()=>RogueIdle.state.passive),'regen');
 await page.locator('[data-config="passive"]').selectOption('resolve');
 await click('[data-cmd="close"]');
 await enter('castle');await fight('final');
 assert.equal(await claim(),'won');
 assert.ok(await value(()=>RogueIdle.state.totals.counters>0));
 await screenshot('06-ending');
 // A separate fresh browser session exercises events, chest, departure, formation and mobile layout.
 const mobile = await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});
 const p = await mobile.newPage();p.on('pageerror',e=>errors.push(e.message));
 await p.goto(url);await p.locator('[data-role="fire"]').click();await p.locator('[data-cmd="start"]').click();
 await p.locator('[data-region="ruins"] .region-shape').click();await p.locator('[data-travel="ruins"]').click();
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'mobile overflow');
 await p.screenshot({path:path.join(out,'07-mobile.png'),fullPage:true});
 await p.locator('[data-action="event"]').click();await p.locator('[data-event="1"]').click();await p.locator('[data-cmd="reward-done"]').click();
 await p.locator('[data-action="chest"]').click();await p.locator('#modal [data-equip]').click();await p.locator('[data-cmd="reward-done"]').click();
 await p.locator('[data-cmd="gear"]').click();await p.locator('[data-tab="tactics"]').click();await p.locator('[data-front="priest"]').click();
 assert.equal(await p.evaluate(()=>RogueIdle.state.party[0].kind),'priest');
 await p.locator('[data-front="hero"]').click();await p.locator('[data-cmd="close"]').click();
 const hp=await p.evaluate(()=>RogueIdle.state.party.map(m=>m.hp));
 await p.locator('[data-region="ember"] .region-shape').click();await p.locator('[data-travel="ember"]').click();
 assert.ok(await p.locator('[data-depart="ember"]').isVisible());await p.locator('[data-depart="ember"]').click();
 assert.equal(await p.evaluate(()=>RogueIdle.state.ap),6);
 assert.deepEqual(await p.evaluate(()=>RogueIdle.state.party.map(m=>m.hp)),hp);
 await p.locator('[data-region="ruins"] .region-shape').click();assert.equal(await p.locator('[data-travel="ruins"]').count(),0);
 // Direct file mode is the downloadable offline deliverable.
 const offline=await context.newPage();await offline.goto(require('node:url').pathToFileURL(path.join(__dirname,'index.html')).href);
 await offline.locator('[data-cmd="start"]').click();
 assert.equal(await offline.evaluate(()=>RogueIdle.state.current),'village');
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({browser:'Edge Chromium',desktop:'1440x1000',mobile:'390x844',fullRun:'victory',battleReload:'passed',eventAndChest:'passed',formation:'passed',noBacktracking:'passed',offlineFile:'passed',pageErrors:errors,screenshots:out},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
