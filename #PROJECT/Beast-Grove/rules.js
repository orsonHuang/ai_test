(function(root){
'use strict';
const W=5,H=7,GOAL=5;
const types={elephant:{name:'象',emoji:'🐘',rank:8,tip:'陆地上的大家伙，记得躲开老鼠。'},tiger:{name:'虎',emoji:'🐯',rank:6,tip:'能跳过河流；河里有鼠就跳不过去。'},cat:{name:'猫',emoji:'🐱',rank:2,tip:'可以吃鼠、同级猫，适合占点和守家。'},rat:{name:'鼠',emoji:'🐭',rank:1,tip:'能下水，也能在陆地吃象！水陆之间不能吃子。'}};
const water=(x,y)=>x===2&&y>=2&&y<=4;
const camp=(x,y)=>y===3&&(x===0||x===4);
const den=(side,x,y)=>x===2&&y===(side===0?6:0);
const at=(s,x,y)=>s.pieces.find(p=>p.x===x&&p.y===y);
const clone=s=>JSON.parse(JSON.stringify(s));
function initial(){const pieces=[];for(let side=0;side<2;side++)['elephant','tiger','cat','rat'].forEach((kind,i)=>{const x=[0,1,3,4][i];pieces.push({id:side+'-'+kind,side,kind,x:side===0?x:4-x,y:side===0?5:1});});return {pieces,turn:0,scores:[0,0],ply:0,winner:null,reason:'',last:null,log:['抢占两侧星星营地，守到下一回合就得分。']};}
function canEat(a,b){if(a.side===b.side)return false;if(water(a.x,a.y)!==water(b.x,b.y))return false;if(a.kind==='rat'&&b.kind==='elephant')return true;if(a.kind==='elephant'&&b.kind==='rat')return false;return types[a.kind].rank>=types[b.kind].rank;}
function moves(s,id){const p=s.pieces.find(p=>p.id===id);if(!p||s.winner!==null||p.side!==s.turn)return [];const out=[];for(const [dx,dy] of [[0,-1],[1,0],[0,1],[-1,0]]){let x=p.x+dx,y=p.y+dy,jump=false;if(water(x,y)&&p.kind==='tiger'){jump=true;let blocked=false;while(water(x,y)){if(at(s,x,y))blocked=true;x+=dx;y+=dy;}if(blocked)continue;}if(x<0||x>=W||y<0||y>=H||den(p.side,x,y))continue;if(water(x,y)&&p.kind!=='rat')continue;const target=at(s,x,y);if(target&&!canEat(p,target))continue;out.push({id,x,y,capture:target?.id||null,jump});}return out;}
const allMoves=s=>s.pieces.filter(p=>p.side===s.turn).flatMap(p=>moves(s,p.id));
function apply(s,action){const valid=moves(s,action.id).find(m=>m.x===action.x&&m.y===action.y);if(!valid)throw new Error('非法走法');const n=clone(s),p=n.pieces.find(p=>p.id===valid.id),actor=p.side;const name=actor===0?'蓝方':'橙方';n.last={from:[p.x,p.y],to:[valid.x,valid.y]};const eaten=n.pieces.find(p=>p.id===valid.capture);n.pieces=n.pieces.filter(p=>p.id!==valid.capture);p.x=valid.x;p.y=valid.y;n.ply++;n.log.unshift(name+types[p.kind].name+(eaten?'吃掉了'+types[eaten.kind].name:valid.jump?'跳过了河流':camp(p.x,p.y)?'进入营地，等待下一回合得星':'向前探索'));
 const win=(side,why)=>{n.winner=side;n.reason=why;};
 if(den(1-actor,p.x,p.y))win(actor,'成功进入对方兽穴');
 else if(!n.pieces.some(p=>p.side!==actor))win(actor,'对方动物全部退场');
 if(n.winner===null){n.turn=1-actor;const points=n.pieces.filter(p=>p.side===n.turn&&camp(p.x,p.y)).length;n.scores[n.turn]+=points;if(points)n.log.unshift((n.turn===0?'蓝方':'橙方')+'守住营地，获得 '+points+' 颗星！');if(n.scores[n.turn]>=GOAL)win(n.turn,'收集到 5 颗星');else if(!allMoves(n).length)win(actor,'对方已无合法走法');else if(n.ply>=100)win(n.scores[0]===n.scores[1]?-1:n.scores[0]>n.scores[1]?0:1,'达到 100 步，按星数结算');}n.log=n.log.slice(0,8);return n;}
function evaluate(s,side){if(s.winner!==null)return s.winner===-1?0:s.winner===side?10000:-10000;let v=(s.scores[side]-s.scores[1-side])*85;for(const p of s.pieces){let a=types[p.kind].rank*5+24;if(camp(p.x,p.y))a+=60;const d=Math.min(p.x+Math.abs(p.y-3),4-p.x+Math.abs(p.y-3));a-=d*7;a-=Math.abs(p.x-2)*1.5+Math.abs(p.y-(p.side===0?0:6))*2;v+=p.side===side?a:-a;}return v;}
function choose(s,level='easy',rng=Math.random){const side=s.turn;const options=allMoves(s).map(m=>{const n=apply(s,m);let score=evaluate(n,side);if(n.winner===null){const replies=allMoves(n);score=Math.min(...replies.map(r=>evaluate(apply(n,r),side)));}return {m,score};}).sort((a,b)=>b.score-a.score);if(!options.length)return null;const eligible=options.filter(o=>o.score>=options[0].score-(level==='easy'?24:0));return eligible[Math.min(eligible.length-1,Math.floor(rng()*eligible.length))].m;}
const api={W,H,GOAL,types,water,camp,den,at,clone,initial,canEat,moves,allMoves,apply,choose};if(typeof module!=='undefined')module.exports=api;else root.BeastRules=api;
})(typeof globalThis!=='undefined'?globalThis:this);
