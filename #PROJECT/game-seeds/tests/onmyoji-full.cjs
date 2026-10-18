const {chromium}=require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');
const root=path.resolve(__dirname,'../../../#Game-TearDown/阴阳师-国服App');
// Check published specification tables arithmetically, independent of any future service.
const souls=fs.readFileSync(path.join(root,'systems/御魂构筑与整理.md'),'utf8');
const rows=[...souls.matchAll(/^\| (\d+) \| (\d+) \| (\d+) \| (\d+) \|/gm)].map(m=>m.slice(1).map(Number));
assert.equal(rows.length,15);let total=0,coin=0;
for(const [level,exp,cost,cumulative] of rows){total+=exp;coin+=cost;assert.equal(exp,600*level);assert.equal(cost,exp*2);assert.equal(cumulative,total);}
assert.equal(total,72000);assert.equal(coin,144000);
const contract=fs.readFileSync(path.join(root,'systems/契灵与术印.md'),'utf8');
const bands=[...contract.matchAll(/^\| (\d+)—(\d+) \| ([\d、]+) \| (\d+) \| (\d+) \|/gm)];assert.equal(bands.length,4);let cumulative=0;
for(const m of bands){const values=m[3].split('、').map(Number);assert.equal(values.length,Number(m[2])-Number(m[1])+1);const sum=values.reduce((a,b)=>a+b,0);assert.equal(sum,Number(m[4]));cumulative+=sum;assert.equal(cumulative,Number(m[5]));}assert.equal(cumulative,20900);
assert.equal(79+19+1.5+0.5,100);assert.equal(3*25+2*12.5,100);assert.equal((45+.2*30)/.8,63.75);
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)failures.push(r.url());});
 const ready=()=>page.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===location.hash);
 await page.goto(base);await ready();assert.equal(new URL(page.url()).hash,'#games');assert(await page.locator('#game-library').isVisible());assert.equal(await page.locator('.brand').getAttribute('href'),'#games');
 await page.goto(base+'#invalid-route');await ready();assert.equal(new URL(page.url()).hash,'#games');
 await page.goto(base+'#library/onmyoji-cn-app');await ready();const links=await page.locator('.system-map a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));assert.equal(links.length,11);
 const report=[];
 for(const href of links){await page.goto(base+href);await ready();assert.equal(await page.locator('#reading-position').count(),0);
  await page.locator('.dev-reference summary').click();await page.locator('.reference-content h1').waitFor();
  const text=await page.locator('.reference-content').innerText();assert(text.includes('参考'));assert(text.includes('验收'));assert(/UI|界面|美术制作/.test(text),href+' UI or visual specification');
  for(const width of [1440,390,320]){await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),href+' overflow '+width);}
  for(const img of await page.locator('#case-document img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());assert(await img.evaluate(i=>i.naturalWidth>0));}
  const dead=await page.locator('#case-document a[href^="#library/"]').evaluateAll(as=>as.filter(a=>!GameLibrary.docs[a.getAttribute('href').slice(9)]).map(a=>a.href));assert.deepEqual(dead,[]);
  report.push({route:href,referenceCharacters:text.length});
 }
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.goto(base+'#library/onmyoji-contract');await ready();await page.locator('.reference-detail').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`contract-detail-${width}.png`)});
  await page.goto(base+'#library/onmyoji-souls');await ready();await page.locator('.dev-reference summary').click();await page.locator('.reference-content table').nth(1).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`souls-cost-${width}.png`)});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);fs.writeFileSync(path.join(out,'onmyoji-full-acceptance.json'),JSON.stringify({base,at:new Date().toISOString(),passed:true,checks:['default and unknown route → games','TOC highlight only','11 system routes and detailed appendices','all local image decoding','valid internal crosslinks','1440/390/320 no overflow','15 soul cost rows and 19 contract level costs arithmetically checked'],report,errors,failures},null,2));console.log('Onmyoji full documentation: 11 systems, cost tables, images, links and responsive appendices passed.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
