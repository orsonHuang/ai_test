'use strict';
const crypto=require('crypto');
const {REGIONS}=require('./Competition');
const {check}=require('./Puzzle');
const dayAt=now=>new Date(now+8*3600000).toISOString().slice(0,10);
const idFor=(...parts)=>crypto.createHash('sha256').update(parts.join('|')).digest('hex');
const compare=(a,b)=>b.count-a.count||a.reachedAt-b.reachedAt||(a.pinyin||'').localeCompare(b.pinyin||'','en')||(a.id||'').localeCompare(b.id||'','en');
/** Repository interface makes scoring testable with serialized, concurrent transactions. */
function createService(store,catalog,{now=Date.now,random=n=>crypto.randomInt(n)}={}){
 const fail=(code,message)=>Object.assign(Error(message),{code});
 const validProof=(l,p)=>{if(!l||!p||Array.isArray(p)||typeof p!=='object'||Object.keys(p).length!==l.animals.length||!l.animals.every(a=>typeof p[a.id]==='string'))return false;return check(l,p).ok;};
 const invites=require('./invitations').invitations(store,{now,dayAt,catalog,validProof});
 const memories=require('./memories').memories(store,{now,random,catalog,validProof});
 return async function execute(uid,event,trusted={}){
  if(!uid)throw fail('AUTH','请重新进入微信小游戏。');
  const nowMs=now(),day=dayAt(nowMs),userId=idFor(uid),action=event?.action;
  if(typeof action==='string'&&action.startsWith('invite'))return invites.call(userId,event,{dailyKey:idFor(day,uid)});
  if(typeof action==='string'&&action.startsWith('memory'))return memories.call(userId,event,{dailyKeyFor:d=>idFor(d,uid)});
  const player=()=>({id:userId,name:'神秘管家'+userId.slice(0,4).toUpperCase(),clears:{},count:0,reachedAt:0});
  const profileOf=p=>({accountId:p.id,name:p.profileAuthorized?p.name:'神秘管家'+p.id.slice(0,4).toUpperCase(),avatarUrl:p.avatarUrl||'',authorized:!!p.profileAuthorized,updatedAt:p.profileUpdatedAt||0});
  if(action==='profileGet')return {ok:true,profile:profileOf(await store.get('players',userId)||player())};
  if(action==='profileUpdate'){
   const info=trusted.profile;
   if(!info?.name||!info?.avatarUrl)throw fail('PROFILE','头像昵称暂时无法获取，请稍后重试。');
   return store.transaction(async tx=>{
    const p=await tx.get('players',userId)||player();
    // Only presentation fields change; scores, clears, receipts and any future fields survive.
    p.name=info.name;p.avatarUrl=info.avatarUrl;p.profileAuthorized=true;p.profileUpdatedAt=Math.max(nowMs,(p.profileUpdatedAt||0)+1);
    await tx.set('players',userId,p);return {ok:true,profile:profileOf(p)};
   });
  }
  if(action==='clear'){
   const level=catalog.main.find(l=>l.id===event.levelId&&l.version===event.version);
   if(!validProof(level,event.placements))throw fail('ANSWER','关卡版本或入住安排未通过审核，请更新后重试。');
   return store.transaction(async tx=>{const p=await tx.get('players',userId)||player();
    if(!p.clears[level.id]){p.clears[level.id]=nowMs;p.count=Object.keys(p.clears).length;p.reachedAt=nowMs;await tx.set('players',userId,p);}
    return {ok:true,count:p.count,reachedAt:p.reachedAt};
   });
  }
  if(action==='dailyStatus'||action==='dailyStart'){
   const key=idFor(day,uid);
   return store.transaction(async tx=>{
    let run=await tx.get('runs',key);if(run)return {ok:true,ticket:run};
    if(action==='dailyStatus')return {ok:true,day,ticket:null};
    if(!REGIONS.some(r=>r.id===event.region))throw fail('REGION','请选择代表地区。');
    if(!catalog.daily.length)throw fail('POOL','今日题目还在准备中，请稍后再来。');
    // First participant freezes a full reviewed puzzle for this calendar day.
    let challenge=await tx.get('days',day);if(!challenge){
     // Persist the bag in the existing days collection; concurrent starts share one draw.
     const stateId='_daily_pool_state',state=await tx.get('days',stateId)||{cycle:1,used:[],lastLevelId:''};
     const ids=new Set(catalog.daily.map(l=>l.id));
     let used=(state.used||[]).filter(id=>ids.has(id)),cycle=state.cycle||1;
     let available=catalog.daily.filter(l=>!used.includes(l.id));
     if(!available.length){used=[];cycle++;available=catalog.daily;}
     // Avoid repeating yesterday at a cycle boundary when there is another choice.
     if(available.length>1)available=available.filter(l=>l.id!==state.lastLevelId);
     const level=available[random(available.length)];
     challenge={day,level};
     await tx.set('days',stateId,{cycle,used:[...used,level.id],lastLevelId:level.id});
     await tx.set('days',day,challenge);
    }
    run={day,region:event.region,won:false,level:challenge.level};await tx.set('runs',key,run);return {ok:true,ticket:run};
   });
  }
  if(action==='dailyClear'){
   if(event.day!==day)throw fail('EXPIRED','这道挑战已跨过北京时间零点，请返回主页参与今日挑战。');
   const key=idFor(day,uid);
   return store.transaction(async tx=>{
    const run=await tx.get('runs',key);if(!run)throw fail('RUN','请先从主页开始今日挑战。');
    if(run.won)return {ok:true,region:run.region,day,already:true};
    if(!validProof(run.level,event.placements))throw fail('ANSWER','入住安排未通过审核。');
    const region=REGIONS.find(r=>r.id===run.region),scoreKey=day+'-'+run.region;
    const score=await tx.get('regions',scoreKey)||{id:scoreKey,day,region:region.id,name:region.name,pinyin:region.pinyin,count:0,reachedAt:0};
    run.won=true;run.completedAt=nowMs;score.count++;score.reachedAt=nowMs;
    await tx.set('runs',key,run);await tx.set('regions',scoreKey,score);return {ok:true,region:run.region,day,already:false};
   });
  }
  if(action==='rankSnapshot'){
   const [players,self,scores,run]=await Promise.all([store.players(0,100),store.get('players',userId),store.regions(day),store.get('runs',idFor(day,uid))]);
   const regions=REGIONS.map(r=>scores.find(s=>s.region===r.id)||{...r,region:r.id,count:0,reachedAt:0}).sort(compare).map(({name,count,region})=>({name,count,region}));
   const mine=self||player(),rank=self?(store.playerRank?await store.playerRank(self):players.findIndex(p=>p.id===userId)+1):null;
   return {ok:true,day,exactRanks:!!store.playerRank,viewer:uid,region:run?.region||'',rows:players.map((p,i)=>({name:profileOf(p).name,avatarUrl:p.avatarUrl||'',count:p.count,rank:i+1,self:p.id===userId})),regions,self:{name:profileOf(mine).name,avatarUrl:mine.avatarUrl||'',count:mine.count,rank:rank||null}};
  }
  if(action==='rank'){
   if(event.kind==='regions'){
    const scores=await store.regions(day),rows=REGIONS.map(r=>{const s=scores.find(s=>s.region===r.id);return s||{region:r.id,name:r.name,pinyin:r.pinyin,count:0,reachedAt:0};}).sort(compare);
    return {ok:true,day,rows:rows.map(({name,count,reachedAt,region})=>({name,count,reachedAt,region})),total:rows.length,hasMore:false};
   }
   const page=Number.isSafeInteger(event.page)&&event.page>=0?Math.min(event.page,9999):0;
   const result=await store.players(page*20,21),self=await store.get('players',userId);
   return {ok:true,rows:result.slice(0,20).map(p=>({name:profileOf(p).name,avatarUrl:p.avatarUrl||'',count:p.count,reachedAt:p.reachedAt,self:p.id===userId})),hasMore:result.length>20,self:self?{count:self.count,reachedAt:self.reachedAt}:null};
  }
  throw fail('ACTION','不支持的请求。');
 };
}
module.exports={createService,dayAt,compare,idFor};
