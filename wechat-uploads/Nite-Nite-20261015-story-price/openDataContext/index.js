/* Friend identities, ordering and own rank stay in the isolated open-data context. */
const canvas=wx.getSharedCanvas(),ctx=canvas.getContext('2d'),images=new Map();
let visible=false,rows=[],own=null,offset=0,designHeight=694,lastRefresh=-Infinity,loading=false,error='',viewer='',fallback=null;
function image(src){if(!src)return null;if(images.has(src))return images.get(src);images.set(src,null);const im=wx.createImage();im.onload=()=>{images.set(src,im);if(visible)draw();};im.onerror=()=>{};im.src=src;return null;}
function fit(text,max,size){ctx.font='bold '+size+'px sans-serif';while(size>12&&ctx.measureText(text).width>max){size--;ctx.font='bold '+size+'px sans-serif';}}
function avatar(src,x,y,size,k){const im=image(src)||image('openDataContext/ranking/portrait.png');if(!im)return;ctx.save();ctx.beginPath();ctx.arc(x,y,size/2,0,Math.PI*2);ctx.clip();const z=size/Math.min(im.width,im.height);ctx.drawImage(im,x-im.width*z/2,y-im.height*z/2,im.width*z,im.height*z);ctx.restore();ctx.strokeStyle='#CEA051';ctx.lineWidth=2*k;ctx.beginPath();ctx.arc(x,y,size/2,0,Math.PI*2);ctx.stroke();}
function paint(r,rank,y,h,k,self=false){
 const cy=y+h/2,w=canvas.width,art=image('openDataContext/ranking/row_'+(self||rank<=3?'honor':'regular')+'.png');
 if(art)ctx.drawImage(art,0,y,w,h);else{ctx.fillStyle=self?'#FFE3A0':'#F5E7C8';ctx.fillRect(0,y,w,h);}
 const medal=!self&&rank<=3?image('openDataContext/ranking/'+['gold','silver','bronze'][rank-1]+'.png'):null;
 if(medal)ctx.drawImage(medal,12*k,cy-36*k,66*k,72*k);else{ctx.textAlign='center';ctx.fillStyle='#674526';ctx.font='bold '+22*k+'px sans-serif';ctx.fillText(rank?String(rank):'—',42*k,cy,65*k);}
 const src=String(r.avatar||r.avatarUrl||'').replace(/^http:/,'https:');avatar(/^https:\/\//.test(src)?src:'',123*k,cy,Math.min(64*k,h-10*k),k);
 ctx.textAlign='left';ctx.fillStyle='#674526';fit(r.name||'我',210*k,22*k);ctx.fillText(r.name||'我',168*k,cy,210*k);
 ctx.textAlign='right';ctx.font='bold '+24*k+'px sans-serif';ctx.fillText(Number(r.count||0)+'关',w-36*k,cy,132*k);
}
function draw(){
 if(!visible)return;const k=canvas.width/566,h=canvas.height,listH=h-92*k;
 ctx.clearRect(0,0,canvas.width,h);ctx.textBaseline='middle';ctx.save();ctx.beginPath();ctx.rect(0,0,canvas.width,listH);ctx.clip();
 if(!rows.length){ctx.textAlign='center';ctx.fillStyle='#674526';ctx.font=22*k+'px sans-serif';ctx.fillText(loading?'正在读取好友排行…':error||'暂无好友通关记录',canvas.width/2,50*k,canvas.width-32*k);}
 let y=-offset*k;rows.forEach((r,i)=>{const rh=(i<3?94:68)*k;if(y+rh>=0&&y<=listH)paint(r,i+1,y,rh,k);y+=rh+5*k;});ctx.restore();
 paint(own||fallback||{name:'我'},own?.rank||null,h-78*k,78*k,k,true);
}
function contentHeight(){return rows.reduce((sum,_,i)=>sum+(i<3?99:73),0)-5;}
function refresh(event){
 if(loading||Date.now()-lastRefresh<180000)return;lastRefresh=Date.now();loading=true;error='';viewer=event.viewer||'';fallback=event.self;draw();
 let settled=false;const finish=(res,failed)=>{if(settled)return;settled=true;clearTimeout(timer);loading=false;
  if(failed){error='授权后请从主页排行榜入口更新';draw();return;}
  const all=(res.data||[]).map(p=>{try{const score=JSON.parse(p.KVDataList.find(k=>k.key==='nite-progress-v1').value);return {name:p.nickname||'微信好友',id:p.openid||'',avatar:p.avatarUrl||'',count:score.count,reachedAt:score.reachedAt};}catch{return null;}}).filter(p=>p&&Number.isSafeInteger(p.count)&&p.count>=0&&Number.isSafeInteger(p.reachedAt)&&p.reachedAt>=0).sort((a,b)=>b.count-a.count||a.reachedAt-b.reachedAt||a.id.localeCompare(b.id));
  const index=all.findIndex(r=>r.id===viewer);own=index<0?null:{...all[index],rank:index+1};rows=all.slice(0,100);offset=0;draw();
 };
 const timer=setTimeout(()=>finish(null,true),12000);
 try{wx.getFriendCloudStorage({keyList:['nite-progress-v1'],success:r=>finish(r,false),fail:()=>finish(null,true)});}catch{finish(null,true);}
}
wx.onMessage(event=>{
 if(event.type==='nite-hide'){visible=false;ctx.clearRect(0,0,canvas.width,canvas.height);return;}
 if(event.type==='nite-friends-refresh'){refresh(event);return;}
 if(event.type==='nite-friends'){visible=true;designHeight=event.height||694;offset=0;if(!rows.length&&!loading&&!error)error='请从主页排行榜入口更新好友榜';draw();return;}
 if(event.type==='nite-friends-resize'){designHeight=event.height||694;offset=Math.min(offset,Math.max(0,contentHeight()-(designHeight-92)));draw();return;}
 if(event.type==='nite-friends-scroll'&&visible){offset=Math.max(0,Math.min(Math.max(0,contentHeight()-(designHeight-92)),offset+(Number(event.delta)||0)));draw();}
});
