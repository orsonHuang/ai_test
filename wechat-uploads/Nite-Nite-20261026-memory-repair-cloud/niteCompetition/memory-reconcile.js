'use strict';
// Player-favouring recovery: retain the union of unlocks and the higher balance/count.
// A durable receipt prevents a response retry from restoring already-spent currency again.
const union=(a=[],b=[])=>Array.from(new Set([...a,...b]));
function mergeMemorySeed(account,seed,monthly){
 account.stamps=Math.max(account.stamps,seed.stamps);
 account.stories=union(account.stories,seed.stories);account.residents=union(account.residents,seed.residents);
 const m=account.monthly;m.glimmer=Math.max(m.glimmer,monthly.glimmer);
 for(const [id,n]of Object.entries(monthly.counts))m.counts[id]=Math.max(m.counts[id]||0,n);
 m.claimed=union(m.claimed,monthly.claimed);m.items=union(m.items,monthly.items);
 m.freeDay=[m.freeDay,monthly.freeDay].sort().pop();m.videoDay=[m.videoDay,monthly.videoDay].sort().pop();
 const login=seed.login;if(Number.isSafeInteger(login?.claimed)&&login.claimed>=0)account.loginStage=Math.max(account.loginStage||0,login.claimed);
 if(typeof login?.lastDay==='string')account.loginDay=[account.loginDay||'',login.lastDay].sort().pop();
 const task=seed.tasks;if(typeof task?.day==='string'&&Number.isSafeInteger(task.drawCount)&&task.drawCount>=0&&task.drawCount<=2){account.draws??={};account.draws[task.day]=Math.max(account.draws[task.day]||0,task.drawCount);}
 if(task?.legacyTotalEligible)account.legacyTasks=task.day;
}
module.exports={mergeMemorySeed};
