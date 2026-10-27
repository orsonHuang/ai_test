const cloud=require('wx-server-sdk');
cloud.init({env:cloud.DYNAMIC_CURRENT_ENV});
// SDK 4.0.2 supports this option for both ordinary and transactional doc.get().
const db=cloud.database({throwOnNotFound:false}),prefix='nite_';
function port(database){return {
 async get(collection,id){const result=await database.collection(prefix+collection).doc(id).get();return Array.isArray(result.data)?result.data[0]||null:result.data||null;},
 async set(collection,id,data){const {_id,...clean}=data;await database.collection(prefix+collection).doc(id).set({data:clean});}
};}
const store={...port(db),transaction:fn=>db.runTransaction(tx=>fn(port(tx))),
 playerRank:async p=>{const _=db.command;const r=await db.collection(prefix+'players').where(_.or([{count:_.gt(p.count)},{count:p.count,reachedAt:_.lt(p.reachedAt)},{count:p.count,reachedAt:p.reachedAt,id:_.lt(p.id)}])).count();return r.total+1;},
 regions:async day=>(await db.collection(prefix+'regions').where({day}).limit(40).get()).data,
 players:async(skip,limit)=>(await db.collection(prefix+'players').orderBy('count','desc').orderBy('reachedAt','asc').orderBy('id','asc').skip(skip).limit(limit).get()).data
};
const run=require('./service').createService(store,require('./catalog.json'));
const {resolveWechatProfile}=require('./profile');
exports.main=async(event)=>{try{const uid=cloud.getWXContext().OPENID;const profile=event?.action==='profileUpdate'?await resolveWechatProfile(cloud,uid,event):undefined;return await run(uid,event,{profile});}catch(e){console.error('competition',{action:event?.action,code:e.code||'INTERNAL',message:e.message});const business=String(e.code).startsWith('MEMORY_')||['AUTH','PROFILE','ANSWER','REGION','POOL','EXPIRED','RUN','ACTION','VISIT','DEVICE','PENDING_DEVICE'].includes(e.code);return {ok:false,code:e.code||'INTERNAL',message:business?e.message:'服务暂不可用，请稍后重试。'};}};
