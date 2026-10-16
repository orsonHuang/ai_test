const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true}),page=await context.newPage(),errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)failed.push(r.url()+':'+r.status());});
 await page.goto(base);await page.locator('.system-card').first().waitFor();assert.equal(await page.locator('.system-card').count(),21);
 await page.screenshot({path:path.join(out,'library-desktop.png'),fullPage:true});
 await page.selectOption('#evidence-filter','all');assert.equal(await page.locator('.system-card').count(),27);
 await page.selectOption('#system-filter','inventory');assert.equal(await page.locator('.system-card').count(),1);assert.match(await page.locator('.system-card').innerText(),/适用待核/);
 await page.selectOption('#evidence-filter','present');assert.equal(await page.locator('.system-card').count(),0);
 await page.click('#clear-system-filters');await page.selectOption('#mode-filter','premium');assert.equal(await page.locator('.system-card').count(),8);
 await page.selectOption('#mode-filter','');await page.fill('#system-search','圣物');assert((await page.locator('.system-card').count())>0);
 await page.goto(base+'#library/hero-no-dodge-inventory');await page.locator('#case-document h1').waitFor();
 await page.fill('#case-note','背包验收：批量分解保护 <script>');await page.click('#save-case-note');await page.reload();assert.equal(await page.inputValue('#case-note'),'背包验收：批量分解保护 <script>');
 await page.goto(base+'#library');await page.check('#only-saved');await page.selectOption('#evidence-filter','all');assert.equal(await page.locator('.system-card').count(),1);
 const [download]=await Promise.all([page.waitForEvent('download'),page.click('#export-cases')]);const backup=path.join(out,'library-backup.json');await download.saveAs(backup);
 const newContext=await browser.newContext(),p2=await newContext.newPage();await p2.goto(base);await p2.setInputFiles('#case-backup-input',backup);await p2.check('#only-saved');await p2.selectOption('#evidence-filter','all');assert.equal(await p2.locator('.system-card').count(),1);await newContext.close();
 const docs=await page.evaluate(()=>Object.keys(GameLibrary.docs));const diagramCount=[];
 for(const id of docs){await page.goto(base+'#library/'+id);await page.locator('#case-document h1').waitFor();await page.waitForFunction(()=>[...document.querySelectorAll('#case-document .mermaid')].every(e=>e.querySelector('svg')),{},{timeout:15000});assert.equal(await page.locator('#case-document img').evaluateAll(imgs=>imgs.filter(i=>!/\/media\/diagram-\d+\.svg$/.test(i.src)).length),0);diagramCount.push([id,await page.locator('.mermaid svg').count()]);}
 for(const width of [1440,390,320]){await page.setViewportSize({width,height:900});for(const route of ['library','library/warm-snow-relics','library/hero-no-dodge-inventory','discover','mine','sources','saved']){await page.goto(base+'#'+route);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${route} overflow ${width}`);}await page.goto(base+'#library/warm-snow-relics');await page.waitForFunction(()=>[...document.querySelectorAll('.mermaid')].every(e=>e.querySelector('svg')));await page.screenshot({path:path.join(out,`library-detail-${width}.png`),fullPage:true});}
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);fs.writeFileSync(path.join(out,'library-acceptance.json'),JSON.stringify({base,passed:true,at:new Date().toISOString(),documents:docs.length,diagramCount,checks:['21 default / 27 total','unknown exclusion','type / commercial filters','full-text search','favorite and note persistence','backup roundtrip','all documents / Mermaid diagrams','local allowlisted media','desktop and mobile overflow'],errors,failed},null,2));console.log('Library acceptance passed: '+docs.length+' documents');await context.close();
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
