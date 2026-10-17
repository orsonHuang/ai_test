const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');
const ready=p=>p.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===(location.hash||'#library'));
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const errors=[],results=[];
 for(const width of [1440,390,320]){
  const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'#library/blue-planet-app');await ready(page);
  assert(await page.locator('#case-document ol>li').count()>=4);
  assert(await page.locator('#case-document ul>li').count()>10);
  assert(await page.locator('#case-document>p').first().evaluate(p=>parseFloat(getComputedStyle(p).marginBottom)>=15));
  assert.match(await page.locator('#case-document ul>li').first().evaluate(n=>getComputedStyle(n,'::marker').content),/·/);
  if(width===1440){await page.locator('#case-document h3').first().scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'reader-paragraphs.png')});await page.locator('#case-toc').evaluate(n=>n.scrollTop=150);}
  const target='.system-map a[href="#library/blue-planet-coop"]';
  await page.locator(target).evaluate(n=>window.scrollTo(0,scrollY+n.getBoundingClientRect().top-300));
  const before=await page.evaluate(()=>scrollY),cardTop=await page.locator(target).evaluate(n=>n.getBoundingClientRect().top);
  await page.screenshot({path:path.join(out,`reader-map-position-${width}.png`)});
  await page.locator(target).click();await ready(page);
  assert.equal(await page.locator('[data-reader-back]').getAttribute('href'),'#library/blue-planet-app');
  const title=await page.locator('.system-title h1').boundingBox(),save=await page.locator('.system-title [data-case-save]').boundingBox();
  if(width>640){assert(save.x>title.x);assert(Math.abs(save.y-title.y)<10);}
  assert(await page.locator('.reader-game-title').evaluate(n=>parseFloat(getComputedStyle(n).fontSize)>=26));
  await page.screenshot({path:path.join(out,`reader-heading-${width}.png`)});
  await page.locator('.system-title [data-case-save]').click();await page.reload();await ready(page);
  assert.equal(await page.locator('.system-title [data-case-save]').getAttribute('aria-pressed'),'true');
  // A related system is a new level; it must return to this visit first.
  await page.locator('#case-document a[href="#library/blue-planet-equipment"]').last().click();await ready(page);
  assert.equal(await page.locator('[data-reader-back]').getAttribute('href'),'#library/blue-planet-coop');
  await page.locator('[data-reader-back]').click();await ready(page);
  assert.equal(new URL(page.url()).hash,'#library/blue-planet-coop');
  await page.evaluate(()=>scrollTo(0,document.body.scrollHeight));
  await page.locator('[data-reader-back]').waitFor();
  const box=await page.locator('[data-reader-back]').boundingBox();assert(box.y>=0&&box.y+box.height<900,'sticky back at article bottom '+width);
  await page.locator('[data-reader-back]').click();await ready(page);
  assert.equal(new URL(page.url()).hash,'#library/blue-planet-app');
  assert(Math.abs(await page.evaluate(()=>scrollY)-before)<5,'restore overview position '+width);
  assert(Math.abs(await page.locator(target).evaluate(n=>n.getBoundingClientRect().top)-cardTop)<5);
  if(width===1440)assert(await page.locator('#case-toc').evaluate(n=>n.scrollTop)>0,'restore table of contents');
  // Native browser history also restores the particular overview visit.
  await page.locator(target).click();await ready(page);await page.goBack();await ready(page);
  assert(Math.abs(await page.evaluate(()=>scrollY)-before)<5,'browser back '+width);
  await page.goForward();await ready(page);assert.equal(new URL(page.url()).hash,'#library/blue-planet-coop');
  await page.locator('[data-reader-home]').click();await ready(page);assert.equal(new URL(page.url()).hash,'#library');
  assert.equal(await page.locator('#library-list').isVisible(),true);assert.equal(await page.evaluate(()=>scrollY),0);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  results.push({width,restoredY:before,passed:true});await context.close();
 }
 const page=await browser.newPage();await page.goto(base+'#library/blue-planet-combat');await ready(page);
 assert.equal(await page.locator('[data-reader-back]').getAttribute('href'),'#library/blue-planet-app');
 await page.locator('[data-reader-back]').click();await ready(page);assert.equal(new URL(page.url()).hash,'#library/blue-planet-app');
 await page.locator('[data-reader-home]').click();await ready(page);await page.selectOption('#game-filter','blue-planet-app');
 const listTarget=page.locator('.system-card h3 a[href="#library/blue-planet-coop"]');await listTarget.evaluate(n=>scrollTo(0,scrollY+n.getBoundingClientRect().top-250));const listY=await page.evaluate(()=>scrollY);
 await listTarget.click();await ready(page);await page.locator('[data-reader-back]').click();await ready(page);
 assert.equal(new URL(page.url()).hash,'#library');assert.equal(await page.inputValue('#game-filter'),'blue-planet-app');assert(Math.abs(await page.evaluate(()=>scrollY)-listY)<5,'restore filtered list position');
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'reader-navigation-acceptance.json'),JSON.stringify({base,at:new Date().toISOString(),results,errors},null,2));
 console.log('Reader navigation passed: paragraphs, lists, titles, favorites, sticky controls, nested return, reload, browser back/forward, direct entry, homepage; 1440/390/320.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
