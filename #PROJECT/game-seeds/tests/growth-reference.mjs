import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as G from '../../../%23Game-TearDown/阴阳师-国服App/reference/growth-calculator.mjs';
let checks=0;const eq=(a,b)=>{assert.deepEqual(a,b);checks++;},bad=(f)=>{assert.throws(f);checks++;};
eq(G.cumulative('hero',40),78000);eq(G.cumulative('account',60),354000);eq(G.cumulative('guardian',40),117000);
eq(G.advance('hero',1,0,650),{level:4,xp:50,spent:650,unused:0});
eq(G.quoteHeroUpgrade({level:19,xp:1800,star:2,amount:500,bank:100,coins:10}),{level:20,xp:0,spent:100,unused:400,coinCost:10,bankAfter:0,coinsAfter:0});
bad(()=>G.quoteHeroUpgrade({level:19,xp:1800,star:2,amount:500,bank:100,coins:9}));
for(const cap of [20,25,30,35,40]){eq(G.advance('hero',cap-1,100*(cap-1)-1,9999,cap).spent,1);eq(G.advance('hero',cap,0,1,cap).spent,0);}
for(const v of [-1,1.5,NaN,Infinity,0])bad(()=>G.advance('hero',1,0,v));
bad(()=>G.advance('hero',2,200,1));bad(()=>G.advance('hero',41,0,1));
const target={id:'a',star:2,level:20,xp:0},m=[{id:'b',star:2},{id:'c',star:2}];
eq(G.quoteStar(target,m,25000),{star:3,level:20,xp:0,coinCost:20000,coinsAfter:5000,consumedIds:['b','c']});
for(const field of ['locked','assigned','referenced','dispatched'])bad(()=>G.quoteStar(target,[{...m[0],[field]:true},m[1]],25000));
bad(()=>G.quoteStar(target,[m[0],m[0]],25000));bad(()=>G.quoteStar(target,[target,m[1]],25000));bad(()=>G.quoteStar(target,m,19999));
const recipe={wind_low:16,water_low:16,wind_mid:8,water_mid:8};eq(G.quoteAwaken('A',recipe).after,{wind_low:0,water_low:0,wind_mid:0,water_mid:0});eq(recipe.wind_low,16);
bad(()=>G.quoteAwaken('A',{...recipe,wind_low:15}));bad(()=>G.quoteAwaken('A',recipe,true));bad(()=>G.quoteAwaken(null,recipe));
eq(G.skillChoice([5,4,5],0.999).after,[5,5,5]);eq(G.skillChoice([1,1,1],0).selected,0);eq(G.skillChoice([1,1,1],0.999).selected,2);bad(()=>G.skillChoice([5,5],0));bad(()=>G.skillChoice([1],1));
eq(G.quoteGuardian(4,500,200,10,200),{level:5,xp:100,spent:200,unused:0,bankAfter:0,milestones:[5]});
eq(G.quoteGuardian(1,0,6750,10,6750).milestones,[5,10]);bad(()=>G.quoteGuardian(10,0,1,10,100));
eq(G.deposit(999000,1000,1),1000000);bad(()=>G.deposit(999001,1000,1));bad(()=>G.deposit(0,1000,-1));
eq(G.mainAttributes(10,5),{attack:210,hp:2100,defense:103,speed:100});
eq(G.heroAttributes('reference_attacker',20,3,true),{attack:350,hp:3509,defense:175,speed:105});
bad(()=>G.heroAttributes('reference_fodder',1,2,true));
const a={id:'a',curve:'hero',star:2,level:20,xp:0,awakened:true,skills:[5,1,1]},b={id:'b',curve:'hero',star:3,level:22,xp:10,awakened:false,skills:[1,1,1]};
const swap=G.transfer(a,b,1);eq(swap.a.level,22);eq(swap.a.awakened,true);eq(swap.a.skills,[5,1,1]);eq(swap.b.level,20);eq(swap.tickets,0);eq(a.level,20);bad(()=>G.transfer(a,{...b,curve:'fodder'},1));bad(()=>G.transfer(a,b,0));
const rows=fs.readFileSync(new URL('../../../%23Game-TearDown/阴阳师-国服App/reference/growth-levels.csv',import.meta.url),'utf8').trim().split(/\r?\n/).slice(1);eq(rows.length,180);
for(const kind of ['hero','fodder','account','guardian']){let sum=0;for(const row of rows.filter(r=>r.split(',')[1]===kind)){const [, ,l,next,total]=row.split(',');eq(Number(total),sum);sum+=Number(next);eq(Number(total),G.cumulative(kind,Number(l)));}}
fs.mkdirSync(new URL('../validation/',import.meta.url),{recursive:true});fs.writeFileSync(new URL('../validation/growth-reference-acceptance.json',import.meta.url),JSON.stringify({passed:true,checks,at:new Date().toISOString(),scope:'Pure reference calculations only; no database, account server, combat or full-client validation'},null,2));console.log(`Growth reference: ${checks} checks passed`);

