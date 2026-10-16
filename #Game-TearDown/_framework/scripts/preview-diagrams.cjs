const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const dependencyRoot=process.env.TEARDOWN_NODE_MODULES;
if(!dependencyRoot) throw new Error('Set TEARDOWN_NODE_MODULES to bundled Node packages.');
const {chromium}=require(path.join(dependencyRoot,'playwright'));
(async()=>{
  const assets=path.resolve(process.argv[2]);
  const output=path.resolve(process.argv[3]);
  fs.mkdirSync(output,{recursive:true});
  const config=JSON.parse(fs.readFileSync(path.join(assets,'diagrams.json'),'utf8'));
  const html='<!doctype html><meta charset="utf-8"><title>Diagram visual QA</title><style>body{margin:20px;background:#e6e9e8;display:grid;grid-template-columns:1fr 1fr;gap:16px}img{width:100%;display:block}</style>'+config.map(d=>`<img src="${pathToFileURL(path.join(assets,d.file)).href}" alt="${d.title}">`).join('');
  const preview=path.join(output,'diagram-contact-sheet.html');fs.writeFileSync(preview,html);
  const browser=await chromium.launch({channel:'msedge',headless:true});
  try {const page=await browser.newPage({viewport:{width:1600,height:900}});await page.goto(pathToFileURL(preview).href);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));await page.screenshot({path:path.join(output,'diagram-contact-sheet.png'),fullPage:true});console.log(JSON.stringify({images:config.length,broken:await page.locator('img').evaluateAll(imgs=>imgs.filter(i=>!i.naturalWidth).length),screenshot:path.join(output,'diagram-contact-sheet.png')}));}finally{await browser.close();}
})();
