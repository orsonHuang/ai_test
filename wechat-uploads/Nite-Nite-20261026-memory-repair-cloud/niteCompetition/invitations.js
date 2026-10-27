'use strict';
const crypto=require('crypto');
const token=()=>crypto.randomBytes(24).toString('hex');
const validToken=v=>typeof v==='string'&&/^[a-f0-9]{48}$/.test(v);
const fail=(code,message)=>Object.assign(Error(message),{code});
/** Daily assistance and reward delivery use server identity/time and one transaction. */
function invitations(store,{now=Date.now,dayAt,catalog,validProof}){
 const fresh=(id,time)=>({id,firstSeen:time,token:token(),total:0,paid:0,day:'',dayEnergy:0});
 const result=(p,day)=>({ok:true,rulesVersion:2,token:p.token,day,todayEnergy:p.day===day?p.dayEnergy:0,total:p.total,available:p.total-p.paid,invited:p.bindDay===day&&!!p.inviter,qualified:p.helpedDay===day,binding:p.bindDay===day?p.binding:'',cap:10});
 return {
  async call(id,event,context={}){
   const time=now(),day=dayAt(time);
   return store.transaction(async tx=>{
    let p=await tx.get('invites',id);
    if(event.action==='inviteVisit'){
     if(!p){
      p=fresh(id,time);await tx.set('inviteTokens',p.token,{owner:id});
     }
     // First valid invitation of this day wins, including returning players.
     // A plain app launch never resurrects yesterday's invitation.
     if(p.bindDay!==day&&p.helpedDay!==day&&validToken(event.token)){
      const link=await tx.get('inviteTokens',event.token);
      if(link&&link.owner!==id&&await tx.get('invites',link.owner)){
       p.inviter=link.owner;p.bindDay=day;p.binding=token();p.boundAt=time;delete p.run;
      }
     }
     await tx.set('invites',id,p);
     return result(p,day);
    }
    if(!p)throw fail('VISIT','请重新进入游戏后重试。');
    if(event.action==='inviteStatus')return result(p,day);
    if(event.action==='inviteBegin'){
     if(p.bindDay!==day||p.helpedDay===day||!p.inviter)return {...result(p,day),run:null};
     if(event.day!==day||event.binding!==p.binding)throw fail('EXPIRED','助力邀请已过期，请重新通过好友邀请进入。');
     if(typeof event.runId!=='string'||!event.runId.length||event.runId.length>120)throw fail('RUN','请重新开始关卡后助力。');
     const pool=event.kind==='main'?catalog.main:event.kind==='daily'?catalog.daily:[];
     const level=pool.find(l=>l.id===event.levelId&&l.version===event.version);
     if(!level)throw fail('ANSWER','关卡版本已更新，请重新进入关卡。');
     if(p.lastHelpRun===event.runId)return {...result(p,day),run:null};
     if(p.run?.runId===event.runId&&(p.run.levelId!==level.id||p.run.version!==level.version||p.run.kind!==event.kind))throw fail('RUN','关卡记录不一致，请重新开始。');
     // Recover a lost start response even if the independent daily score already arrived.
     if(p.run?.runId===event.runId&&p.run.day===day&&p.run.binding===p.binding)return {...result(p,day),run:p.run.ticket};
     if(event.kind==='daily'){
      const daily=await tx.get('runs',context.dailyKey);
      if(!daily||daily.won||daily.level.id!==level.id||daily.level.version!==level.version)throw fail('RUN','请从主页开始今日挑战后助力。');
     }
     if(!p.run||p.run.runId!==event.runId||p.run.day!==day||p.run.binding!==p.binding){
      p.run={ticket:token(),binding:p.binding,day,runId:event.runId,kind:event.kind,levelId:level.id,version:level.version,startedAt:time};
      await tx.set('invites',id,p);
     }
     return {...result(p,day),run:p.run.ticket};
    }
    if(event.action==='inviteComplete'){
     // A retry after a committed response is harmless, including after midnight.
     if(validToken(event.ticket)&&p.lastHelpTicket===event.ticket)return {...result(p,day),assisted:true,rewarded:!!p.lastHelpRewarded};
     const run=p.run;
     if(!run||!validToken(event.ticket)||run.ticket!==event.ticket||run.runId!==event.runId)throw fail('RUN','本次助力记录未就绪，请重新开始关卡。');
     if(run.day!==day||p.bindDay!==day||run.binding!==p.binding)throw fail('EXPIRED','助力已跨过北京时间0点，请重新通过好友邀请进入。');
     const pool=run.kind==='main'?catalog.main:catalog.daily,level=pool.find(l=>l.id===run.levelId&&l.version===run.version);
     if(!validProof(level,event.placements))throw fail('ANSWER','入住安排未通过审核，本次未发放助力奖励。');
     if(p.helpedDay===day)return {...result(p,day),assisted:true,rewarded:false};
     const host=await tx.get('invites',p.inviter);if(!host)throw fail('VISIT','邀请记录不可用。');
     if(host.day!==day){host.day=day;host.dayEnergy=0;}
     const rewarded=host.dayEnergy+2<=10;
     if(rewarded){host.dayEnergy+=2;host.total+=2;await tx.set('invites',host.id,host);}
     p.helpedDay=day;p.lastHelpRun=run.runId;p.lastHelpTicket=run.ticket;p.lastHelpRewarded=rewarded;delete p.run;
     await tx.set('invites',id,p);
     return {...result(p,day),assisted:true,rewarded};
    }
    if(event.action==='inviteClaim'){
     if(!validToken(event.device))throw fail('DEVICE','请恢复本机存储后重试。');
     if(p.pending&&p.pending.device!==event.device)throw fail('PENDING_DEVICE','奖励正在另一台设备同步，请先在原设备联网完成同步。');
     if(!p.pending&&p.total>p.paid){p.pending={receipt:'invite:'+token(),amount:p.total-p.paid,device:event.device};await tx.set('invites',id,p);}
     return {...result(p,day),reward:p.pending?{receipt:p.pending.receipt,amount:p.pending.amount}:null};
    }
    if(event.action==='inviteAck'){
     if(p.pending&&p.pending.device===event.device&&p.pending.receipt===event.receipt){p.paid+=p.pending.amount;delete p.pending;await tx.set('invites',id,p);}
     return result(p,day);
    }
    throw fail('ACTION','不支持的邀请请求。');
   });
  }
 };
}
module.exports={invitations};
