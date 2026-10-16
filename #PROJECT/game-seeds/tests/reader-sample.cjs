const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'#library/blue-planet-app');
 assert.equal(await page.locator('.system-map a').count(),10);
 const links=await page.locator('.system-map a').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
 assert.equal(new Set(links).size,10);
 assert.equal(await page.locator('.reader-edition').count(),1);
 assert.equal(await page.locator('.evidence-note').count(),0);
 assert(!/目录结构|roomRevision|P参考/.test(await page.locator('#case-document').innerText()));
 await page.screenshot({path:path.join(out,'blue-planet-overview.png')});
 await page.locator('.system-map').screenshot({path:path.join(out,'blue-planet-map.png')});
 for(const link of links){
  await page.goto(base+'#library/blue-planet-app');
  await page.locator('.system-map a[href="'+link+'"]').click();
  assert.equal(new URL(page.url()).hash,link);
  await page.waitForFunction(()=>[...document.querySelectorAll('#case-document .mermaid')].every(e=>e.querySelector('svg')));
  assert.equal(await page.locator('.ui-analysis').count(),1);
  assert.equal(await page.locator('.dev-reference[open]').count(),0);
  assert.equal(await page.locator('.reference-content h1').count(),0);
  assert(!/COM-R|COOP-R|roomRevision|## P/.test(await page.locator('#case-document').innerText()));
 }
 await page.goto(base+'#library/blue-planet-coop');
 await page.locator('.ui-analysis').screenshot({path:path.join(out,'blue-planet-coop-ui.png')});
 await page.fill('#case-note','样稿验收：准备状态绑定方案');await page.click('#save-case-note');await page.reload();
 assert.equal(await page.inputValue('#case-note'),'样稿验收：准备状态绑定方案');
 await page.locator('.dev-reference summary').click();
 await page.locator('.reference-content h1').waitFor();
 await page.waitForFunction(()=>[...document.querySelectorAll('.reference-content .mermaid')].every(e=>e.querySelector('svg')));
 assert.match(await page.locator('.reference-content').innerText(),/roomRevision/);
 assert(!/roomRevision|COOP-R/.test(await page.locator('#case-toc').innerText()));
 for(const width of [390,320]){
  await page.setViewportSize({width,height:900});
  for(const route of ['blue-planet-app',...links.map(x=>x.slice(9))]){
   await page.goto(base+'#library/'+route);
   await page.waitForFunction(()=>[...document.querySelectorAll('#case-document .mermaid')].every(e=>e.querySelector('svg')));
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),route+' overflow '+width);
  }
  await page.goto(base+'#library/blue-planet-app');await page.locator('.system-map').screenshot({path:path.join(out,'blue-planet-map-'+width+'.png')});
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'reader-sample-acceptance.json'),JSON.stringify({base,at:new Date().toISOString(),passed:true,systems:10,checks:['10 real map clicks','10 analysis UI figures','reader prose without internal spec jargon','lazy reference appendix and diagrams','favorite note persistence','all sample pages at 320 and 390 pixels'],errors},null,2));
 console.log('Reader sample passed: overview, 10 systems, appendix, favorites, mobile');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
