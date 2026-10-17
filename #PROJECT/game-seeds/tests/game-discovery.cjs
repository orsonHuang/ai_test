const {chromium}=require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');
const ready=page=>page.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===location.hash);
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const errors=[],results=[];
 for(const width of [1440,390,320]){
  const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  const go=async hash=>{await page.goto(base+hash);await ready(page);};
  const facet=(key,value)=>page.locator(`[data-game-facet="${key}"][data-value="${value}"]`);
  await go('#games');assert.equal(await page.locator('.game-card').count(),4);assert.equal(await page.locator('[data-nav=games]').getAttribute('aria-current'),'page');
  await page.fill('#game-search','roguelike');assert.equal(await page.locator('.game-card').count(),2);
  await facet('platform','Steam').click();assert.equal(await page.locator('.game-card').count(),1);assert.match(await page.locator('.game-card').innerText(),/暖雪/);
  for(const tag of ['俯视角','2.5D','动作','Roguelike','Steam单机','国产'])assert((await page.locator('.game-card .case-tags').innerText()).includes(tag));
  await facet('origin','海外').click();assert.equal(await page.locator('.game-card').count(),0);await page.locator('[data-reset-games]').click();assert.equal(await page.locator('.game-card').count(),4);
  // Same-axis OR, cross-axis AND, and keyword tokens.
  await facet('platform','手机App').click();await facet('platform','Steam').click();assert.equal(await page.locator('.game-card').count(),3);
  await facet('genre','RPG').click();assert.equal(await page.locator('.game-card').count(),1);assert.match(await page.locator('.game-card').innerText(),/阴阳师/);
  await page.locator('#reset-game-filters').click();await page.fill('#game-search','Steam 单机');assert.equal(await page.locator('.game-card').count(),1);
  await page.locator('#reset-game-filters').click();await facet('platform','手机App').click();
  await page.locator('.game-card h2 a').last().scrollIntoViewIfNeeded();const listY=await page.evaluate(()=>scrollY);
  await page.screenshot({path:path.join(out,`games-${width}.png`),fullPage:true});
  await page.locator('.game-card h2 a[href="#library/onmyoji-cn-app"]').click();await ready(page);
  assert.equal(await page.locator('[data-reader-back]').getAttribute('href'),'#games');
  const map=page.locator('.system-map a[href="#library/onmyoji-heroes"]');await map.evaluate(n=>scrollTo(0,scrollY+n.getBoundingClientRect().top-250));const overviewY=await page.evaluate(()=>scrollY);
  await map.click();await ready(page);await page.reload();await ready(page);await page.locator('[data-reader-back]').click();await ready(page);assert(Math.abs(await page.evaluate(()=>scrollY)-overviewY)<5);
  await page.locator('[data-reader-back]').click();await ready(page);assert.equal(new URL(page.url()).hash,'#games');assert.equal(await facet('platform','手机App').getAttribute('aria-pressed'),'true');assert.equal(await page.locator('.game-card').count(),2);assert(Math.abs(await page.evaluate(()=>scrollY)-listY)<5);
  await page.reload();await ready(page);assert.equal(await page.locator('.game-card').count(),2);assert(Math.abs(await page.evaluate(()=>scrollY)-listY)<5);
  await page.locator('.game-card h2 a').last().click();await ready(page);await page.goBack();await ready(page);assert.equal(await page.locator('.game-card').count(),2);await page.goForward();await ready(page);
  // At a section boundary the bottom reading line must select the preceding section,
  // then advance when the next heading crosses that line.
  const heading=page.locator('#case-document h2').nth(3),id=await heading.getAttribute('id');
  await heading.evaluate(h=>scrollTo(0,scrollY+h.getBoundingClientRect().top-(innerHeight-48+12)));
  await page.waitForFunction(id=>document.querySelector('#case-toc [aria-current]')?.dataset.scrollSection!==id,id);
  await heading.evaluate(h=>scrollTo(0,scrollY+h.getBoundingClientRect().top-(innerHeight-48-12)));
  await page.waitForFunction(id=>document.querySelector('#case-toc [aria-current]')?.dataset.scrollSection===id,id);
  assert.equal(await page.locator('#case-toc [aria-current]').count(),1);assert((await page.locator('#reading-position').innerText()).includes(await heading.innerText()));
  assert(await page.locator('#reading-position').isVisible());
  await page.screenshot({path:path.join(out,`reading-position-${width}.png`)});
  await go('#library/onmyoji-heroes');
  for(const figure of await page.locator('.reference-figure').all()){
   assert.equal(await figure.locator('figcaption br').count(),0);assert.equal(await figure.locator('figcaption a').innerText(),'来源 ↗');assert((await figure.locator('figcaption span').innerText()).length<15);assert.match(await figure.locator('.image-source').getAttribute('title'),/历史截图/);
  }
  const photo=page.locator('.reference-figure').first();await photo.scrollIntoViewIfNeeded();await photo.locator('img').evaluate(i=>i.decode());await page.screenshot({path:path.join(out,`caption-${width}.png`)});
  await page.evaluate(()=>scrollTo(0,document.body.scrollHeight));await page.waitForFunction(()=>document.querySelector('#reading-position').textContent.includes('我的用途与笔记'));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.locator('[data-reader-home]').click();await ready(page);assert.equal(await page.locator('#game-summaries').count(),0);assert.equal(await page.locator('.system-card').count(),31);
  await go('#games');await page.locator('#reset-game-filters').click();await facet('platform','手机App').click();await page.locator('.game-card h2 a').last().click();await ready(page);
  await page.locator('[data-nav=games]').click();await ready(page);await facet('platform','Steam').click();assert.equal(await page.locator('.game-card').count(),3);
  await page.goBack();await ready(page);await page.locator('[data-reader-back]').click();await ready(page);assert.equal(await page.locator('.game-card').count(),2,'independent list visits retain their own filters');
  results.push({width,passed:true});await context.close();
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'game-discovery-acceptance.json'),JSON.stringify({base,passed:true,at:new Date().toISOString(),results,checks:['four tagged games','search tokens and case-insensitive matching','same-axis OR / cross-axis AND','empty and reset','list / game / system return, reload, native history','bottom reading boundary and page end','collapsed mobile reading hint','title and source only','legacy system library and favorites intact'],errors},null,2));console.log('Game discovery passed: filtering, history, reading position, compact captions; 1440/390/320.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
