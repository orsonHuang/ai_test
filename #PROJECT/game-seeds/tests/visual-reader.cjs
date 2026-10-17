const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)failures.push(r.url());});
 const go=async id=>{await page.goto(base+'#library/'+id);await page.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===location.hash);};
 const click=async a=>page.locator(`[data-demo-action="${a}"]`).click();
 for(const width of [1440,390,320]){
  await page.setViewportSize({width,height:1000});
  await go('onmyoji-cn-app');
  assert.equal(await page.locator('.system-map a').count(),10);
  const links=await page.locator('.system-map a').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
  for(const href of links){
   await go('onmyoji-cn-app');const a=page.locator(`.system-map a[href="${href}"]`);await a.scrollIntoViewIfNeeded();
   const before=await page.evaluate(()=>scrollY);await a.click();await page.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===location.hash);
   assert.equal(new URL(page.url()).hash,href);assert.equal(await page.locator(href==='#library/onmyoji-heroes'?'.reference-download':'.ui-analysis').count(),1);
   assert((await page.locator('.reader-edition').innerText()).includes(await page.evaluate(()=>GameLibrary.games.find(g=>g.id==='onmyoji-cn-app').asOf)));
   assert(!/roomRevision|R1 \||P参考/.test(await page.locator('#case-document').innerText()));
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),href+' overflow '+width);
   await page.locator('[data-reader-back]').click();await page.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===location.hash);
   assert.equal(new URL(page.url()).hash,'#library/onmyoji-cn-app');assert(Math.abs(await page.evaluate(()=>scrollY)-before)<=5,'map position restore');
  }
  await go('blue-planet-coop');await page.locator('.diagram-expand').first().click();await page.waitForFunction(()=>document.querySelector('.diagram-dialog img')?.naturalWidth>0);assert(await page.locator('.diagram-dialog').isVisible());await page.keyboard.press('Escape');await page.locator('.diagram-dialog').waitFor({state:'detached'});assert.equal(await page.locator('.diagram-dialog').count(),0);assert(await page.locator('[data-demo-action="start"]').isDisabled());
  await click('ready');assert(await page.locator('[data-demo-action="start"]').isEnabled());
  await click('config');assert(await page.locator('[data-demo-action="start"]').isDisabled());
  await click('ready');await click('challenge');assert(await page.locator('[data-demo-action="start"]').isDisabled());
  await click('ready');await click('tickets');assert(await page.locator('[data-demo-action="start"]').isDisabled());
  assert.match(await page.locator('.demo-reason').innerText(),/不足/);await click('tickets');
  await page.locator('[data-demo-fail]').check();await click('start');assert.match(await page.locator('.demo-message').innerText(),/失败/);assert.match(await page.locator('.demo-challenge').innerText(),/挑战券 2/);
  await click('ready');await click('start');assert.match(await page.locator('.demo-challenge').innerText(),/挑战券 1/);assert(await page.locator('[data-demo-action="start"]').isDisabled());
  await click('finish');assert(await page.locator('[data-demo-action="start"]').isDisabled());await click('member');assert(await page.locator('[data-demo-action="ready"]').isDisabled());await click('member');await click('ready');assert(await page.locator('[data-demo-action="start"]').isEnabled());
  await click('reset');assert.match(await page.locator('.demo-challenge').innerText(),/挑战券 2/);assert(await page.locator('[data-demo-action="start"]').isDisabled());
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'coop overflow');
  await page.locator('[data-demo="coop"]').screenshot({path:path.join(out,`coop-prototype-${width}.png`)});
  await go('onmyoji-souls');
  await page.selectOption('[data-demo-candidate]','1');assert(await page.locator('[data-demo-action="apply"]').isDisabled());assert.match(await page.locator('.demo-condition.fail').innerText(),/出手/);
  await page.selectOption('[data-demo-candidate]','2');assert(await page.locator('[data-demo-action="apply"]').isDisabled());assert.match(await page.locator('.demo-condition.fail').innerText(),/暴击/);
  await page.selectOption('[data-demo-candidate]','3');await click('apply');assert.match(await page.locator('[data-current-candidate]').innerText(),/^D/);
  await click('reset');assert.match(await page.locator('[data-current-candidate]').innerText(),/^A/);
  await page.locator('[data-demo="souls"]').screenshot({path:path.join(out,`souls-prototype-${width}.png`)});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'souls overflow');
  await page.fill('#case-note','御魂验收：条件先于总分');await page.click('#save-case-note');await page.reload();assert.equal(await page.inputValue('#case-note'),'御魂验收：条件先于总分');
  await page.locator('.dev-reference summary').click();await page.locator('.reference-content h1').waitFor();assert.match(await page.locator('.reference-content').innerText(),/速度|speed/);
 }
 await page.setViewportSize({width:1440,height:1000});await go('onmyoji-cn-app');await page.screenshot({path:path.join(out,'onmyoji-overview.png')});await page.locator('.system-map').screenshot({path:path.join(out,'onmyoji-system-map.png')});
 await go('onmyoji-combat');await page.locator('.ui-analysis').screenshot({path:path.join(out,'onmyoji-combat-ui.png')});
 assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);
 fs.writeFileSync(path.join(out,'visual-reader-acceptance.json'),JSON.stringify({base,at:new Date().toISOString(),passed:true,widths:[1440,390,320],checks:['30 real map clicks and origin restores','10 Onmyoji system UI figures','coop readiness invalidation, membership, insufficient tickets, failure without cost, single start and reset','souls constraints, preview, apply and reset','new favorites persist','reference appendix','no overflow or console/network errors'],errors,failures},null,2));
 console.log('Visual reader passed: Onmyoji 10 systems, both interactive prototypes, 3 widths, navigation and favorites');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
