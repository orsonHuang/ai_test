const {chromium}=require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.BASE_URL||'http://127.0.0.1:8789/',out=path.resolve(__dirname,'../validation');
const root=path.resolve(__dirname,'../../../#Game-TearDown/永远的蔚蓝星球-App');
const growth=fs.readFileSync(path.join(root,'systems/英雄与永久成长.md'),'utf8');
// Audit the actual published table independently: contiguous domains, marginal and cumulative costs.
const hero=[...growth.matchAll(/^\| (\d+)→(\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|/gm)].map(m=>m.slice(1).map(Number));
assert.equal(hero.length,34);let gold=0,shards=0;
for(const [l,next,c,s,totalG,totalS] of hero){assert.equal(next,l+1);gold+=c;shards+=s;assert.equal(totalG,gold);assert.equal(totalS,shards);assert.equal(c,100*l);assert.equal(s,2*l);}
assert.equal(gold,59500);assert.equal(shards,1190);
const talents=[...growth.matchAll(/^\| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|/gm)].map(m=>m.slice(1).map(Number));
assert.equal(talents.length,30);
for(const [rows,totalExpected,matExpected] of [[talents.slice(0,20),42000,1050],[talents.slice(20),27500,55]]){let g=0,s=0;rows.forEach((r,i)=>{assert.equal(r[0],i+1);g+=r[1];s+=r[2];assert.equal(r[3],g);assert.equal(r[4],s);});assert.equal(g,totalExpected);assert.equal(s,matExpected);}
const reader=JSON.parse(fs.readFileSync(path.join(root,'reader.json'),'utf8'));
assert.equal(reader.referenceMedia.length,11);for(const m of reader.referenceMedia){assert.equal(m.publication,'editorial-reference');assert(m.sourceUrl&&m.sourceAuthor&&m.sourceDate);assert(fs.existsSync(path.join(root,m.path)));}
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],failed=[];
 page.setDefaultNavigationTimeout(60000);
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)failed.push(r.url());});
 const ready=()=>page.waitForFunction(()=>document.querySelector('#view-library').dataset.readyRoute===location.hash);
 await page.goto(base+'#library/blue-planet-app');await ready();assert.equal(await page.locator('.system-map a').count(),10);
 const links=await page.locator('.system-map a').evaluateAll(as=>as.map(a=>a.getAttribute('href')));const report=[];
 for(const route of ['#library/blue-planet-app',...links]){
  await page.goto(base+route);await ready();assert.equal(await page.locator('#reading-position').count(),0);
  if(route!=='#library/blue-planet-app'){await page.locator('.dev-reference summary').click();await page.locator('.reference-content h1').waitFor();assert.match(await page.locator('.reference-content').innerText(),/验收/);}
  await page.waitForFunction(()=>[...document.querySelectorAll('#case-document .mermaid')].every(e=>e.querySelector('svg')));
  const dead=await page.locator('#case-document a[href^="#library/"]').evaluateAll(as=>as.filter(a=>!GameLibrary.docs[a.getAttribute('href').slice(9)]).map(a=>a.href));assert.deepEqual(dead,[]);
  for(const img of await page.locator('#case-document img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());assert(await img.evaluate(i=>i.naturalWidth>0));}
  for(const width of [1440,390,320]){await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),route+' overflow '+width);}
  report.push({route,images:await page.locator('#case-document img').count()});
 }
 for(const width of [1440,390]){await page.setViewportSize({width,height:1000});await page.goto(base+'#library/blue-planet-heroes');await ready();await page.locator('h2').filter({hasText:'国王成长：'}).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`blue-king-${width}.png`)});await page.locator('h2').filter({hasText:'养成材料与消耗'}).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`blue-cost-${width}.png`)});}
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);fs.writeFileSync(path.join(out,'blue-full-acceptance.json'),JSON.stringify({base,at:new Date().toISOString(),passed:true,checks:['10 stable system routes','11 reference media with provenance','64 full growth/talent table rows checked','all diagrams rendered','all reader images decoded','all links resolve','1440/390/320 no overflow'],report,errors,failed},null,2));console.log('Blue full: 10 systems, 64 cost rows, 11 cited images, diagrams and three-width reading passed.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
