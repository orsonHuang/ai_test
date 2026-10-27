'use strict';
// Parallel rollout: the legacy niteCompetition function and nite_players stay untouched.
const cloud=require('wx-server-sdk');cloud.init({env:cloud.DYNAMIC_CURRENT_ENV});
const db=cloud.database({throwOnNotFound:false}),catalog=require('./catalog.json');
const {createService}=require('./service'),{highestScore}=require('./ranking-score'),{migrateBatch}=require('./ranking-migration');
const {resolveWechatProfile}=require('./profile');
const ranked=new Set(['clear','rank','rankSnapshot','rankScore','dailyStatus','dailyStart','dailyClear']);
const get=async(database,table,id)=>{const r=await database.collection(table).doc(id).get();return Array.isArray(r.data)?r.data[0]||null:r.data||null;};
const set=async(database,table,id,value)=>{const {_id,...data}=value;await database.collection(table).doc(id).set({data});};
function table(channel,c){if(c==='players')return channel==='release'?'nite_rank_players_v2':'nite_test_players';if(channel==='test'&&['days','runs','regions'].includes(c))return 'nite_test_'+c;return 'nite_'+c;}
function port(database,channel){return {get:(c,id)=>get(database,table(channel,c),id),set:(c,id,value)=>set(database,table(channel,c),id,value)};}
function store(channel){const p=c=>table(channel,c);return {...port(db,channel),transaction:fn=>db.runTransaction(tx=>fn(port(tx,channel))),
 players:async(skip,limit)=>(await db.collection(p('players')).orderBy('count','desc').orderBy('reachedAt','asc').orderBy('id','asc').skip(skip).limit(limit).get()).data,
 regions:async day=>(await db.collection(p('regions')).where({day}).limit(40).get()).data,
 playerRank:async user=>{const _=db.command;return (await db.collection(p('players')).where(_.or([{count:_.gt(user.count)},{count:user.count,reachedAt:_.lt(user.reachedAt)},{count:user.count,reachedAt:user.reachedAt,id:_.lt(user.id)}])).count()).total+1;}
 };}
const services={release:createService(store('release'),catalog),test:createService(store('test'),catalog)};
/** Reads legacy documents; writes only the separate v2 score collection and v2 metadata. */
const importStore={scanPlayers:async(cursor,limit)=>(await db.collection('nite_players').where(cursor?{_id:db.command.gt(cursor)}:{}).orderBy('_id','asc').limit(limit).get()).data,
 transaction:fn=>db.runTransaction(tx=>fn({
  async get(c,id){if(c==='days')return get(tx,'nite_rank_meta_v2',id);const old=await get(tx,'nite_players',id),current=await get(tx,'nite_rank_players_v2',id);if(!old)return current;return {...old,...current,name:old.name,avatarUrl:old.avatarUrl||'',profileAuthorized:!!old.profileAuthorized,clears:{...old.clears,...current?.clears}};},
  set:(c,id,value)=>set(tx,c==='days'?'nite_rank_meta_v2':'nite_rank_players_v2',id,value)
 }))};
async function importLegacy(){
 const key='_highest_main_v2_migration',state=await get(db,'nite_rank_meta_v2',key);
 if(state?.done&&Date.now()-(state.updatedAt||0)>180000)await db.runTransaction(async tx=>{const s=await get(tx,'nite_rank_meta_v2',key);if(s?.done&&Date.now()-(s.updatedAt||0)>180000)await set(tx,'nite_rank_meta_v2',key,{...s,done:false,cursor:'',leaseUntil:0,hadComplete:true});});
 const r=await migrateBatch(importStore,catalog.main);return r.done||state?.done||state?.hadComplete;
}
exports.main=async event=>{try{
 const uid=cloud.getWXContext().OPENID;if(!uid)return {ok:false,code:'AUTH',message:'请重新进入微信小游戏。'};
 if(!['release','test'].includes(event?.rankingChannel))return {ok:false,code:'RANK_CHANNEL',message:'请使用新版排行榜。'};
 const channel=event.rankingChannel;
 if(channel==='release'&&!ranked.has(event.action))return {ok:false,code:'ACTION',message:'正式业务请使用原服务。'};
 if(channel==='release'&&['rank','rankSnapshot','rankScore'].includes(event.action)&&!await importLegacy())return {ok:false,code:'RANK_MIGRATING',message:'正在同步历史成绩，请稍后重新打开。'};
 const profile=event.action==='profileUpdate'?await resolveWechatProfile(cloud,uid,event):undefined;
 return await services[channel](uid,event,{profile});
 }catch(e){console.error('ranking-v2',{action:event?.action,code:e.code,message:e.message});return {ok:false,code:e.code||'INTERNAL',message:e.code?e.message:'排行榜暂不可用，请稍后重试。'};}};
