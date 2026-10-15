/* Friend identities, ordering and own rank stay in the isolated open-data context. */
const canvas=wx.getSharedCanvas(),ctx=canvas.getContext('2d'),images=new Map();
const rankingAssets=require('./ranking-assets');
let visible=false,rows=[],own=null,offset=0,designHeight=694,lastRefresh=-Infinity,loading=false,error='',viewer='',fallback=null;
let listHeight=602,loadingY=350,loadingTimer=null,loadingStarted=0;
const art=name=>image(rankingAssets[name]);
const fontFamilies={normal:'sans-serif',bold:'sans-serif'},fontKeys={};
function configureFonts(fonts){
 if(!fonts)return;
 for(const weight of ['normal','bold']){
  const info=fonts[weight];if(!info)continue;const key=JSON.stringify(info);if(fontKeys[weight]===key)continue;let family=typeof info.family==='string'?info.family:'';
  // Some hosts expose loadFont here; others share the face registered by the main context.
  if(typeof wx.loadFont==='function'&&info.path){try{family=wx.loadFont(info.path)||family;}catch{}}
  if(family){fontFamilies[weight]=family;fontKeys[weight]=key;}
 }
}
function font(size,weight='normal'){
 const family=fontFamilies[weight];
 // The Bold TTF has its own outlines: do not synthesize another layer of bold.
 return (family==='sans-serif'&&weight==='bold'?'bold ':'')+size+'px '+(family==='sans-serif'?family:'"'+family.replace(/["\\]/g,'')+'", sans-serif');
}
function image(src){if(!src)return null;if(images.has(src))return images.get(src);images.set(src,null);const im=wx.createImage();im.onload=()=>{images.set(src,im);if(visible)draw();};im.onerror=()=>{};im.src=src;return null;}
function fit(text,max,size){ctx.font=font(size);while(size>12&&ctx.measureText(text).width>max){size--;ctx.font=font(size);}}
function avatar(src,x,y,size,k){const im=image(src)||art('portrait');if(!im)return;ctx.save();ctx.beginPath();ctx.arc(x,y,size/2,0,Math.PI*2);ctx.clip();const z=size/Math.min(im.width,im.height);ctx.drawImage(im,x-im.width*z/2,y-im.height*z/2,im.width*z,im.height*z);ctx.restore();ctx.strokeStyle='#C89749';ctx.lineWidth=2*k;ctx.beginPath();ctx.arc(x,y,size/2+.5*k,0,Math.PI*2);ctx.stroke();}
function paper(im,x,y,w,h,k){const sx=[0,30,im.width-30,im.width],sy=[0,20,im.height-20,im.height],dx=[x,x+30*k,x+w-30*k,x+w],dy=[y,y+20*k,y+h-20*k,y+h];for(let r=0;r<3;r++)for(let c=0;c<3;c++)ctx.drawImage(im,sx[c],sy[r],sx[c+1]-sx[c],sy[r+1]-sy[r],dx[c],dy[r],dx[c+1]-dx[c],dy[r+1]-dy[r]);}
function paint(r,rank,y,h,k,self=false){
 const cy=y+h/2,w=canvas.width,isMe=!!viewer&&r.id===viewer,top=!self&&rank>0&&rank<=3,background=art('row_'+(self||isMe?'self':top?'honor':'regular'));
 if(background)paper(background,0,y,w,h,k);else{ctx.fillStyle=self?'#FFE3A0':'#F5E7C8';ctx.fillRect(0,y,w,h);}
 const medal=top?art(['gold','silver','bronze'][rank-1]):null;
 if(medal)ctx.drawImage(medal,.5*k,cy-42*k,77*k,84*k);else{ctx.textAlign='center';ctx.fillStyle='#674526';ctx.font=font(26*k,'bold');ctx.fillText(rank?String(rank):'—',39*k,cy,56*k);}
 if(isMe&&!self){const mark=art('bookmark');if(mark)ctx.drawImage(mark,-4*k,cy-41.5*k,26*k,43*k);}
 const src=String(r.avatar||r.avatarUrl||'').replace(/^http:/,'https:');avatar(/^https:\/\//.test(src)?src:'',130*k,cy,(self?60:top?72:57.6)*k,k);
 const name=(r.name||'我')+(isMe&&!self?'（我）':'');ctx.textAlign='left';ctx.fillStyle='#674526';fit(name,215*k,22*k);ctx.fillText(name,174.5*k,cy,215*k);
 ctx.textAlign='right';ctx.font=font((top?28:25)*k,'bold');ctx.fillText(Number(r.count||0).toLocaleString('en-US')+'关',530*k,cy,132*k);
}
function stopLoadingTick(){if(loadingTimer!==null){clearTimeout(loadingTimer);loadingTimer=null;}}
function drawLoading(k){
 const cx=canvas.width/2,cy=loadingY*k,t=(Date.now()-loadingStarted)/1000,x=cx-110*k,y=cy-105*k,w=220*k,h=210*k,r=24*k;
 ctx.beginPath();ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);ctx.quadraticCurveTo(x+w,y,x+w,y+r);ctx.lineTo(x+w,y+h-r);ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);ctx.lineTo(x+r,y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-r);ctx.lineTo(x,y+r);ctx.quadraticCurveTo(x,y,x+r,y);ctx.fillStyle='rgba(8,29,47,.92)';ctx.fill();
 const icon=art('zhaocai');if(icon)ctx.drawImage(icon,0,0,389,406,cx-60*k,cy-(80+Math.sin(t*Math.PI*1.4)*7)*k,120*k,120*k);
 ctx.textAlign='left';ctx.fillStyle='#FFF2CD';ctx.font=font(28*k);ctx.fillText('加载中'+'.'.repeat(Math.floor(t/.25)%7),cx-70*k,cy+65*k);
 if(loadingTimer===null)loadingTimer=setTimeout(()=>{loadingTimer=null;if(visible&&loading)draw();},50);
}
function draw(){
 if(!visible)return;const k=canvas.width/566,h=canvas.height,listH=listHeight*k;
 ctx.clearRect(0,0,canvas.width,h);ctx.textBaseline='middle';ctx.save();ctx.beginPath();ctx.rect(0,0,canvas.width,listH);ctx.clip();
 if(!rows.length&&!loading){ctx.textAlign='center';ctx.fillStyle='#674526';ctx.font=font(22*k);ctx.fillText(error||'暂无好友通关记录',canvas.width/2,50*k,canvas.width-32*k);}
 let y=-offset*k;rows.forEach((r,i)=>{const rh=(i<3?94:68)*k;if(y+rh>=0&&y<=listH)paint(r,i+1,y,rh,k);y+=rh+5*k;});ctx.restore();
 paint(own||fallback||{name:'我'},own?.rank||null,h-78*k,78*k,k,true);
 if(loading)drawLoading(k);else stopLoadingTick();
}
function contentHeight(){return rows.reduce((sum,_,i)=>sum+(i<3?99:73),0)-5;}
function refresh(event){
 if(loading||Date.now()-lastRefresh<180000)return;lastRefresh=Date.now();loading=true;loadingStarted=Date.now();error='';viewer=event.viewer||'';fallback=event.self;draw();
 let settled=false;const finish=(res,failed)=>{if(settled)return;settled=true;clearTimeout(timer);loading=false;
  if(failed){lastRefresh=-Infinity;error='好友排行读取失败，请稍后重新打开';stopLoadingTick();draw();return;}
  const all=(res.data||[]).map(p=>{try{const score=JSON.parse(p.KVDataList.find(k=>k.key==='nite-progress-v1').value);return {name:p.nickname||'微信好友',id:p.openid||'',avatar:p.avatarUrl||'',count:score.count,reachedAt:score.reachedAt};}catch{return null;}}).filter(p=>p&&Number.isSafeInteger(p.count)&&p.count>=0&&Number.isSafeInteger(p.reachedAt)&&p.reachedAt>=0).sort((a,b)=>b.count-a.count||a.reachedAt-b.reachedAt||a.id.localeCompare(b.id));
  const index=all.findIndex(r=>r.id===viewer);own=index<0?null:{...all[index],rank:index+1};rows=all.slice(0,100);offset=0;draw();
 };
 const timer=setTimeout(()=>finish(null,true),12000);
 try{wx.getFriendCloudStorage({keyList:['nite-progress-v1'],success:r=>finish(r,false),fail:()=>finish(null,true)});}catch{finish(null,true);}
}
wx.onMessage(event=>{
 configureFonts(event.fonts);
 if(event.type==='nite-hide'){visible=false;stopLoadingTick();ctx.clearRect(0,0,canvas.width,canvas.height);return;}
 if(event.type==='nite-friends-refresh'){refresh(event);return;}
 if(event.type==='nite-friends'){visible=true;designHeight=event.height||694;listHeight=event.listHeight||designHeight-92;loadingY=event.loadingY||350;offset=0;if(!rows.length&&!loading&&!error)error='请从主页排行榜入口更新好友榜';draw();return;}
 if(event.type==='nite-friends-resize'){designHeight=event.height||694;listHeight=event.listHeight||designHeight-92;loadingY=event.loadingY||350;offset=Math.min(offset,Math.max(0,contentHeight()-listHeight));draw();return;}
 if(event.type==='nite-friends-scroll'&&visible&&!loading){offset=Math.max(0,Math.min(Math.max(0,contentHeight()-listHeight),offset+(Number(event.delta)||0)));draw();}
});
