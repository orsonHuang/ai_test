'use strict';
const METRIC='highest-main-v2';
/** Only server-validated clears enter this calculation. Never use client unlocks. */
function highestScore(player,main){
 const positions=new Map(main.map((l,i)=>[l.id,Number.isSafeInteger(l.sequence)&&l.sequence>0?l.sequence:i+1]));
 const old=player.rankMetric===METRIC&&Number.isSafeInteger(player.count)&&player.count>=0;
 let count=old?player.count:0,reachedAt=old?player.reachedAt:0;
 for(const [id,time]of Object.entries(player.clears||{})){
  // Removed legacy night IDs still represent genuine historical achievements.
  const position=positions.get(id)??Number(/^night-(\d+)$/.exec(id)?.[1]);
  if(!Number.isSafeInteger(position)||position<=0||!Number.isFinite(time)||time<0)continue;
  if(position>count){count=position;reachedAt=time;}
  else if(position===count&&(!Number.isFinite(reachedAt)||time<reachedAt))reachedAt=time;
 }
 // Incomplete legacy records cannot reconstruct the maximum. Preserve the old verified
 // count as a conservative lower bound rather than silently wiping an existing score.
 if(!old&&Number.isSafeInteger(player.count)&&player.count>count){count=player.count;reachedAt=Number.isFinite(player.reachedAt)?player.reachedAt:0;}
 return {count,reachedAt:count?reachedAt:0,rankMetric:METRIC};
}
function scoreChanged(player,score){return player.count!==score.count||player.reachedAt!==score.reachedAt||player.rankMetric!==score.rankMetric;}
module.exports={METRIC,highestScore,scoreChanged};
