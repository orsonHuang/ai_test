// Exact browser captures of source image regions requested by the user; no generated pixels.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const project=path.resolve(__dirname,'..'),out=path.resolve(project,'../../#Game-TearDown/阴阳师-国服App/reader-assets');
const captures=[
 ['onmyoji-combat-source.png','battle-reference.png',{x:110,y:201,width:1080,height:498}],
 ['onmyoji-combat-source.png','orb-detail.png',{x:472,y:620,width:324,height:78}],
 ['onmyoji-combat-source.png','turn-order-detail.png',{x:1080,y:244,width:100,height:238}],
 ['onmyoji-growth-source.png','growth-reference.png',{x:110,y:201,width:1080,height:498}],
 ['onmyoji-growth-source.png','growth-result-detail.png',{x:650,y:564,width:370,height:132}],
 ['onmyoji-growth-source.png','growth-tabs-detail.png',{x:1070,y:265,width:107,height:282}],
 ['onmyoji-yuling-source.jpg','yuling-reference.png',{x:0,y:0,width:550,height:413},true]
];
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:1300,height:900},deviceScaleFactor:1});
 for(const [input,name,clip,natural] of captures){const data=fs.readFileSync(path.join(project,'validation',input)).toString('base64');await page.setContent(`<style>body{margin:0}img{display:block;${natural?'':'width:1300px;height:900px'}}</style><img src="data:image/${input.endsWith('.jpg')?'jpeg':'png'};base64,${data}">`);await page.locator('img').evaluate(img=>img.decode());await page.screenshot({path:path.join(out,name),clip});}
 console.log('Captured 7 source images/regions');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
