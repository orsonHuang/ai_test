'use strict';
const crypto=require('crypto');
const {memoryTransaction}=require('./memory-transaction');
const {mergeMemorySeed}=require('./memory-reconcile');
const data=require('./memories-catalog.json');
const cards=new Map(data.cards.map(c=>[c.id,c]));
const fail=(code,message)=>Object.assign(Error(message),{code:'MEMORY_'+code});
const token=()=>crypto.randomBytes(24).toString('hex');
const hash=(...v)=>crypto.createHash('sha256').update(v.join('|')).digest('hex');
const copy=v=>JSON.parse(JSON.stringify(v));
const validToken=v=>typeof v==='string'&&/^[a-f0-9]{48}$/.test(v);
const integer=(v,max=1e9)=>Number.isSafeInteger(v)&&v>=0&&v<=max;
const validReceipt=v=>typeof v==='string'&&v.length>0&&v.length<=256;
const creditShape=e=>e&&typeof e.key==='string'&&e.key.length>0&&e.key.length<=240&&integer(e.amount,20)&&typeof e.kind==='string';
const dayAt=t=>new Date(t+8*3600000).toISOString().slice(0,10);
const endOfDay=t=>Date.parse(dayAt(t)+'T00:00:00+08:00')+86400000;
const fresh=()=>({version:2,month:data.month,glimmer:0,counts:{},claimed:[],items:[],freeDay:'',videoDay:'',videoReceipts:[],lastResults:[],revision:0});
const developmentAccount='071b3a74a75dd15e7877d5340bfafeefb399a0edd257410d06d7c380b24ef981';
function validateSeed(s){
 if(!s||!integer(s.stamps)||!s.monthly||s.monthly.month!==data.month||!integer(s.monthly.glimmer)||!s.monthly.counts||Array.isArray(s.monthly.counts))throw fail('MIGRATION','旧相册暂时无法读取，请保留存档后重试');
 if(Object.entries(s.monthly.counts).some(([id,n])=>!cards.has(id)||!integer(n,100000)))throw fail('MIGRATION','旧故事数量无法读取，请保留存档后重试');
 for(const key of ['stories','residents'])if(!Array.isArray(s[key])||s[key].some(id=>typeof id!=='string'||id.length>100))throw fail('MIGRATION','旧相册记录无法读取');
 if(!Array.isArray(s.monthly.claimed)||s.monthly.claimed.some(n=>!Number.isInteger(n)||n<1||n>6))throw fail('MIGRATION','旧奖励记录无法读取');
 if(JSON.stringify(s).length>800000)throw fail('MIGRATION','旧存档过大，请联系客服核对');
}
/** Server-only account, operation receipts and gifts commit together. No client count writes after import. */
function memories(store,{now=Date.now,random=n=>crypto.randomInt(n),catalog,validProof}){
 const changed=a=>{a.revision++;a.monthly.revision=a.revision;};
 async function developmentGrant(tx,a,test,time){
  if(!test||a.id!=='dev:'+developmentAccount)return;
  const key='development-stamps-20261025',receipt=hash(a.id,key);
  if(await tx.get('memoryCredits',receipt))return;
  if(!integer(a.stamps+100))throw fail('STATE','印章数量异常，请联系客服');
  a.stamps+=100;changed(a);
  await tx.set('memoryCredits',receipt,{account:a.id,key,kind:'development',amount:100,at:time});
  await tx.set('memoryAccounts',a.id,a);
 }
 const stamp=a=>a.revision+'|'+a.giftDay;
 const snapshot=a=>({account:a.id,revision:a.revision,stamps:a.stamps,monthly:copy(a.monthly),stories:[...a.stories],residents:[...a.residents],reserved:{...a.reserved},draws:copy(a.draws||{}),giftDay:a.giftDay,giftUsed:a.giftUsed});
 const giftView=(g,id)=>({token:g.token,cardId:g.cardId,state:g.state,expiresAt:g.expiresAt,createdAt:g.createdAt,mine:g.sender===id,received:g.claimant===id});
 async function expire(tx,a,time){
  for(const t of [...a.pending]){const g=await tx.get('memoryGifts',t);if(g?.state==='pending'&&g.expiresAt<=time){g.state='expired';a.reserved[g.cardId]=Math.max(0,(a.reserved[g.cardId]||0)-1);a.pending=a.pending.filter(x=>x!==t);changed(a);await tx.set('memoryGifts',t,g);}}
  if(a.giftDay!==dayAt(time)){a.giftDay=dayAt(time);a.giftUsed=0;}
 }
 function receive(a,id,glimmer){const old=a.monthly.counts[id]||0;a.monthly.counts[id]=old+1;const bonus=old&&glimmer?1:0;a.monthly.glimmer+=bonus;return {id,isNew:!old,count:old+1,glimmer:bonus};}
 function seedMonthly(s){const m=fresh();m.counts=copy(s.counts);m.glimmer=s.glimmer;m.claimed=Array.from(new Set(s.claimed));m.items=m.claimed.flatMap(ch=>data.chapters[ch-1].items);m.freeDay=/^\d{4}-\d{2}-\d{2}$/.test(s.freeDay)?s.freeDay:'';m.videoDay=/^\d{4}-\d{2}-\d{2}$/.test(s.videoDay)?s.videoDay:'';return m;}
 return {async call(user,event,context={}){
  const time=now(),day=dayAt(time),test=event.test===true;
  if(test&&user!==developmentAccount)throw fail('AUTH','测试赠礼仅对开发账号开放');
  const id=(test?'dev:':'live:')+user,action=event.action;
  return memoryTransaction(store,async tx=>{
   let a=await tx.get('memoryAccounts',id);
   if(action==='memoryMigrate'){
    const repair=event.reconcile;
    if(repair&&(!validToken(repair.operation)||typeof repair.source!=='string'||repair.source.length>500))throw fail('MIGRATION','相册合并记录无法读取，请重试');
    const repairKey=repair?hash(id,'reconcile',repair.operation):'',repaired=repair?await tx.get('memoryMigrations',repairKey):null;
    if(repaired&&a)return {ok:true,snapshot:snapshot(a),reconciled:repair.operation};
    if(repair){validateSeed(event.seed);const baseline=event.seedCredits||[];if(!Array.isArray(baseline)||baseline.length>5000||baseline.some(e=>!creditShape(e)))throw fail('MIGRATION','旧奖励记录无法读取，请保留存档后重试');}
    const before=repair&&a?copy(a):null;
    if(!a){validateSeed(event.seed);const s=event.seed,baseline=event.seedCredits||[];
     if(!Array.isArray(baseline)||baseline.length>(repair?5000:2500)||baseline.some(e=>!creditShape(e)))throw fail('MIGRATION','旧奖励记录无法读取，请保留存档后重试');
     const imported={};for(const e of baseline)imported[hash(id,e.key)]={key:e.key,kind:e.kind,amount:e.amount,stage:e.stage||0,day:e.day};
     a={id,revision:1,stamps:s.stamps,monthly:seedMonthly(s.monthly),stories:Array.from(new Set(s.stories)),residents:Array.from(new Set(s.residents)),reserved:{},pending:[],history:[],giftDay:day,giftUsed:0,createdAt:time,imported,draws:{},loginStage:s.login?.claimed||0,loginDay:s.login?.lastDay||''};
     if(s.tasks?.day&&integer(s.tasks.drawCount,2))a.draws[s.tasks.day]=s.tasks.drawCount;
     a.legacyTasks=s.tasks?.legacyTotalEligible?s.tasks.day:'';
     // Preserve the complete approved one-time import for support/reconciliation. Never merge a later device's seed.
     await tx.set('memoryMigrations',id,{account:id,at:time,seed:copy(s),policy:'one-time-local-import-approved-20261024'});
     await tx.set('memoryAccounts',id,a);
    }
    if(repair){
     if(before)mergeMemorySeed(a,event.seed,seedMonthly(event.seed.monthly));
     a.imported??={};for(const e of event.seedCredits||[]){const key=hash(id,e.key);a.imported[key]??={key:e.key,kind:e.kind,amount:e.amount,stage:e.stage||0,day:e.day};}
     changed(a);await tx.set('memoryAccounts',id,a);
     await tx.set('memoryMigrations',repairKey,{account:id,at:time,source:repair.source,operation:repair.operation,seed:copy(event.seed),before,policy:'player-favouring-union-and-max-approved-20261026'});
    }
    await developmentGrant(tx,a,test,time);
    return {ok:true,snapshot:snapshot(a),...(repair?{reconciled:repair.operation}:{})};
   }
   if(!a)throw fail('MIGRATION','请先同步相册，再领取或赠送故事');
   if(action==='memoryStatus')await developmentGrant(tx,a,test,time);
   const original=stamp(a);
   await expire(tx,a,time);
   if(action==='memoryStatus'){
    const gifts=[];for(const t of a.history.slice(-20).reverse()){const g=await tx.get('memoryGifts',t);if(g)gifts.push(giftView(g,id));}
    if(stamp(a)!==original)await tx.set('memoryAccounts',id,a);return {ok:true,snapshot:snapshot(a),gifts};
   }
   if(action==='memoryGiftInspect'||action==='memoryGiftClaim'){
    if(!validToken(event.token))throw fail('LINK','这份故事链接无效');
    const g=await tx.get('memoryGifts',event.token);if(!g||g.test!==test)throw fail('LINK','这份故事链接无效');
    const sender=g.sender===id?a:await tx.get('memoryAccounts',g.sender);if(!sender)throw fail('LINK','这份故事暂时无法领取');
    const senderOriginal=sender===a?original:stamp(sender);
    await expire(tx,sender,time);const current={...g};if(current.state==='pending'&&current.expiresAt<=time)current.state='expired';
    if(action==='memoryGiftClaim'&&current.state==='pending'&&current.sender!==id){
     if((sender.reserved[g.cardId]||0)<1||(sender.monthly.counts[g.cardId]||0)<2)throw fail('STATE','赠礼记录正在核对，请稍后重试');
     sender.monthly.counts[g.cardId]--;sender.reserved[g.cardId]--;sender.pending=sender.pending.filter(t=>t!==g.token);sender.giftUsed++;changed(sender);
     receive(a,g.cardId,false);changed(a);current.state='claimed';current.claimant=id;current.claimedAt=time;await tx.set('memoryGifts',g.token,current);
    }
    // Settled links and previews are read-only: retries must not keep competing
    // for the sender's account lock after the first successful transfer.
    if(stamp(sender)!==senderOriginal)await tx.set('memoryAccounts',sender.id,sender);if(sender!==a&&stamp(a)!==original)await tx.set('memoryAccounts',id,a);
    return {ok:true,snapshot:snapshot(a),gift:giftView(current,id)};
   }
   if(!validToken(event.operation))throw fail('OPERATION','操作记录无法读取，请重试');
   const opKey=hash(id,event.operation),previous=await tx.get('memoryOperations',opKey);
   const fingerprint=hash(action,JSON.stringify(event.payload||{}));
   if(previous){if(previous.fingerprint!==fingerprint)throw fail('OPERATION','重复操作的内容不一致');const result=copy(previous.result);if(result.gift){const g=await tx.get('memoryGifts',result.gift.token);if(g)result.gift=giftView(g,id);}if(stamp(a)!==original)await tx.set('memoryAccounts',id,a);return {ok:true,...result,snapshot:snapshot(a)};}
   const p=event.payload||{};let result={};
   if(action==='memoryGiftCreate'){
    if(!cards.has(p.cardId))throw fail('CARD','故事不存在');
    const existing=await Promise.all(a.pending.map(t=>tx.get('memoryGifts',t))),same=existing.find(g=>g?.state==='pending'&&g.cardId===p.cardId);
    if(same)result={gift:giftView(same,id)};
    else{
     if((a.monthly.counts[p.cardId]||0)-(a.reserved[p.cardId]||0)<2)throw fail('COUNT','数量2以上的故事才能赠送哦');
     if(a.giftUsed+a.pending.length>=3)throw fail('LIMIT','今天已送出或预留3份故事，明天再来吧');
     const g={token:token(),sender:id,cardId:p.cardId,state:'pending',createdAt:time,expiresAt:endOfDay(time),test};
     a.reserved[p.cardId]=(a.reserved[p.cardId]||0)+1;a.pending.push(g.token);a.history.push(g.token);a.history=a.history.slice(-60);await tx.set('memoryGifts',g.token,g);result={gift:giftView(g,id)};
    }
   }else if(action==='memoryGiftRevoke'){
    const g=validToken(p.token)?await tx.get('memoryGifts',p.token):null;if(!g||g.sender!==id||p.cardId!==undefined&&g.cardId!==p.cardId)throw fail('LINK','无法撤回这份故事');
    if(g.state==='pending'){g.state='revoked';a.reserved[g.cardId]--;a.pending=a.pending.filter(t=>t!==g.token);await tx.set('memoryGifts',g.token,g);}result={gift:giftView(g,id)};
   }else if(action==='memoryDraw'){
    if(!['free','paid','video'].includes(p.kind))throw fail('OPERATION','抽取方式无效');
    if(p.kind==='free'){if(a.monthly.freeDay>=day)throw fail('USED','今日免费抽取已使用');a.monthly.freeDay=day;}
    if(p.kind==='paid'){if(a.stamps<10)throw fail('FUNDS','回忆印章不足');a.stamps-=10;}
    if(p.kind==='video'){if(a.monthly.videoDay>=day)throw fail('USED','每日视频已使用，明天再来吧');if(!validReceipt(p.receipt))throw fail('VIDEO','请完整观看视频后重试');a.monthly.videoDay=day;}
    const results=Array.from({length:3},()=>{const n=random(100),rarity=n<65?1:n<95?2:3,pool=data.cards.filter(c=>c.rarity===rarity);return receive(a,pool[random(pool.length)].id,true);});a.monthly.lastResults=results;a.draws[day]=Math.min(2,(a.draws[day]||0)+1);result={results};
   }else if(action==='memoryExchange'){
    const missing=data.cards.filter(c=>!a.monthly.counts[c.id]);if(!missing.length)throw fail('COMPLETE','本月限定已集齐啦');if(a.monthly.glimmer<6)throw fail('FUNDS','微光不够，抽卡获取吧');a.monthly.glimmer-=6;result={results:[receive(a,missing[random(missing.length)].id,false)]};a.monthly.lastResults=result.results;
   }else if(action==='memoryChapter'){
    const ch=p.chapter,info=data.chapters[ch-1];if(!Number.isInteger(ch)||!info||a.monthly.claimed.includes(ch)||data.cards.filter(c=>c.chapter===ch).some(c=>!a.monthly.counts[c.id]))throw fail('REWARD','集齐这一页即可领取');a.monthly.claimed.push(ch);a.monthly.items.push(...info.items);if(ch===3)a.monthly.glimmer+=6;if(ch===5)a.stamps+=30;result={name:info.reward};
   }else if(action==='memoryPurchase'){
    const resident=data.residents.find(r=>r.stories.some(s=>s.id===p.storyId)),story=resident?.stories.find(s=>s.id===p.storyId);if(!story||!a.residents.includes(resident.id))throw fail('LOCKED','请先获得这位住户的入住卡');
    if(!a.stories.includes(story.id)){if(resident.stories.slice(0,resident.stories.indexOf(story)).some(s=>!a.stories.includes(s.id)))throw fail('LOCKED','请先按顺序解锁前面的故事');if(a.stamps<story.cost)throw fail('FUNDS','回忆印章不足');a.stamps-=story.cost;a.stories.push(story.id);}
   }else if(action==='memoryCredits'){
    if(!Array.isArray(p.credits)||p.credits.length>30)throw fail('CREDIT','奖励记录过多，请稍后重试');
    for(const e of p.credits){
     if(!creditShape(e))throw fail('CREDIT','奖励记录无效');const key=hash(id,e.key);if(a.imported[key]||await tx.get('memoryCredits',key))continue;
     await validateCredit(tx,a,e,{catalog,validProof,day,time,context});a.stamps+=e.amount;await tx.set('memoryCredits',key,{account:id,...copy(e),at:time});
    }
    // Resident unlocks follow verified level proofs or the one-time imported entitlement.
    for(const r of data.residents){if(r.levelId&&p.credits.some(e=>e.kind==='main'&&e.levelId===r.levelId)&&!a.residents.includes(r.id))a.residents.push(r.id);}
   }else throw fail('ACTION','不支持的相册操作');
   if(!integer(a.stamps))throw fail('STATE','印章数量异常，请联系客服');changed(a);await tx.set('memoryAccounts',id,a);await tx.set('memoryOperations',opKey,{account:id,fingerprint,result,at:time});return {ok:true,...result,snapshot:snapshot(a)};
  });
 }};
}
async function validateCredit(tx,a,e,{catalog,validProof,day,context}){
 if(e.day>day||!/^\d{4}-\d{2}-\d{2}$/.test(e.day))throw fail('CREDIT','奖励日期无效');
 if(e.kind==='main'){
  // New clients grant 2 per main run; keep accepting unsynced legacy 1-stamp receipts.
  const l=catalog.main.find(l=>l.id===e.levelId&&l.version===e.version);if(!validReceipt(e.runId)||!validProof(l,e.placements)||![1,2].includes(e.amount)||e.key!==`main:${e.runId}`)throw fail('CREDIT','通关奖励未通过核验');
 }else if(e.kind==='daily'){
  // Accept outstanding receipts from older clients without changing once-per-day keys.
  const run=await tx.get('runs',context.dailyKeyFor(e.day));if(![2,10].includes(e.amount)||e.key!==`daily:${e.day}`||!run||run.level.id!==e.levelId||run.level.version!==e.version||!validProof(run.level,e.placements))throw fail('CREDIT','挑战奖励未通过核验');
 }else if(e.kind==='double'){
  const key=hash(a.id,e.base),base=a.imported[key]||await tx.get('memoryCredits',key);if(!base||!['main','daily'].includes(base.kind)||base.amount!==e.amount||!validReceipt(e.receipt)||e.key!==`double:${e.base}`)throw fail('CREDIT','翻倍奖励未通过核验');
 }else if(e.kind==='login'){
  const expected=e.stage===1?0:e.stage===2?(e.rewardKind==='card'?0:2):Number(e.day.slice(-2))%2?0:5;
  if(e.key!==`login:${e.day}:${e.bonus?'bonus':'base'}`||e.amount!==expected||!Number.isInteger(e.stage)||e.stage<1||e.stage>1000000||e.bonus&&!validReceipt(e.receipt))throw fail('CREDIT','签到奖励未通过核验');
  if(e.bonus){const key=hash(a.id,`login:${e.day}:base`),base=a.imported[key]||await tx.get('memoryCredits',key);if(!base||base.stage!==e.stage||base.amount!==e.amount)throw fail('CREDIT','签到翻倍记录尚未同步');}
  else{if(e.stage!==a.loginStage+1||e.day<=a.loginDay)throw fail('CREDIT','签到日期或次数不一致');a.loginStage=e.stage;a.loginDay=e.day;if(e.stage===2&&!a.residents.includes('zhaocai'))a.residents.push('zhaocai');}
 }else if(e.kind==='task'){
  const rewards=[2,2,2,4,10,10];if(e.key!==`task:${e.day}:${e.index}`||rewards[e.index]!==e.amount||e.index===5&&!validReceipt(e.receipt))throw fail('CREDIT','任务奖励未通过核验');
  if((e.index===1||e.index>=4)&&!validProof(catalog.main.concat(catalog.daily).find(l=>l.id===e.proof?.levelId&&l.version===e.proof?.version),e.proof?.placements))throw fail('CREDIT','任务通关记录未通过核验');
  if((e.index===2||e.index>=4&&a.legacyTasks!==e.day)&&(a.draws[e.day]||0)<2)throw fail('CREDIT','抽取任务记录尚未同步');
  if((e.index===3||e.index>=4)&&!await tx.get('runs',context.dailyKeyFor(e.day)))throw fail('CREDIT','每日挑战记录尚未同步');
 }else throw fail('CREDIT','奖励来源无效');
}
module.exports={memories,dayAt,endOfDay,validateSeed};
