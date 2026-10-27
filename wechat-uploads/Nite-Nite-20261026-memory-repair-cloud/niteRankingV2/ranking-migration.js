'use strict';
const {highestScore,scoreChanged}=require('./ranking-score');
/** Bounded, resumable and idempotent; no player, clear or profile is deleted. */
async function migrateBatch(store,main,{limit=20,now=Date.now,token=()=>require('crypto').randomBytes(12).toString('hex')}={}){
 const key='_highest_main_v2_migration',owner=token(),time=now();
 const lease=await store.transaction(async tx=>{
  const state=await tx.get('days',key)||{cursor:'',done:false};
  if(state.done)return {done:true};if(state.leaseUntil>time)return {busy:true};
  await tx.set('days',key,{...state,owner,leaseUntil:time+60000});return state;
 });
 if(lease.done||lease.busy)return lease;
 let cursor=lease.cursor||'',changed=0;
 try{
  const rows=await store.scanPlayers(cursor,limit);
  for(const row of rows){
   await store.transaction(async tx=>{const p=await tx.get('players',row.id);if(!p)return;const score=highestScore(p,main);if(scoreChanged(p,score)){
    const backup=p.rankLegacyV1||{count:p.count||0,reachedAt:p.reachedAt||0};
    await tx.set('players',row.id,{...p,...score,rankLegacyV1:backup});changed++;
   }});cursor=row._id||row.id;
  }
  const done=rows.length<limit;
  await store.transaction(async tx=>{const state=await tx.get('days',key);if(state?.owner===owner)await tx.set('days',key,{cursor,done,leaseUntil:0,updatedAt:now()});});
  return {done,changed,scanned:rows.length};
 }catch(error){
  await store.transaction(async tx=>{const state=await tx.get('days',key);if(state?.owner===owner)await tx.set('days',key,{...state,cursor,leaseUntil:0});});throw error;
 }
}
module.exports={migrateBatch};
