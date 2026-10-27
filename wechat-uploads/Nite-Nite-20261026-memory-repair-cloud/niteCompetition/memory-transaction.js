'use strict';
// CloudBase can reject a document write before commit, outside the SDK's
// commit-conflict retry. Retry the entire rolled-back transaction only.
const conflict=e=>/DATABASE_TRANSACTION_CONFLICT|ResourceUnavailable\.TransactionConflict/.test(String(e?.code||'')+' '+String(e?.message||e?.errMsg||''));
async function memoryTransaction(store,work,{sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms)),random=Math.random,now=Date.now}={}){
 const started=now();
 for(let attempt=0;;attempt++){
  try{return await store.transaction(work);}
  catch(e){
   if(!conflict(e)||attempt>=4||now()-started>=8000)throw e;
   await sleep(60*2**attempt+Math.floor(random()*80));
  }
 }
}
module.exports={memoryTransaction};
