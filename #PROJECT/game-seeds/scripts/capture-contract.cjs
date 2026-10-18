const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const project=path.resolve(__dirname,'..'),out=path.resolve(project,'../../#Game-TearDown/阴阳师-国服App/reader-assets');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:1080,height:609},deviceScaleFactor:1});
 for(const [source,name,clip] of [
 ['onmyoji-contract-explore-source.jpg','contract-explore.png',null],
 ['onmyoji-contract-explore-source.jpg','contract-cost-detail.png',{x:945,y:468,width:130,height:138}],
 ['onmyoji-contract-source.jpg','contract-performance.png',null]]){
  const data=fs.readFileSync(path.join(project,'validation',source)).toString('base64');
  await page.setContent(`<style>body{margin:0}img{display:block;width:1080px;height:609px}</style><img src="data:image/jpeg;base64,${data}">`);
  await page.locator('img').evaluate(i=>i.decode());await page.screenshot({path:path.join(out,name),...(clip?{clip}:{})});
 }console.log('Captured inspected contract source images and cost detail.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
