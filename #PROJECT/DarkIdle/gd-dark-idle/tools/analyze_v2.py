"""Read-only deterministic build comparison in the current Godot runtime."""
import json
from mcp_bridge import GodotMCP,EVIDENCE
c=GodotMCP();session=c.project_session()
code='''var R=load("res://scripts/combat_rules.gd")
var cfg=load("res://resources/balance_v2.tres")
var builds=[
    ["扩散燃爆",["wall","double","spread","burst"],["charge","shield"]],
    ["提前引爆",["wall","double","burst","spread"],["charge","shield"]],
    ["单点击杀",["ignite","double","burst","burst"],["charge","shield"]],
    ["全场焚烧",["wall","funeral","inferno","ignite"],["charge","mana"]],
    ["回能防御",["wall","funeral","inferno","ignite"],["mana","shield"]],
    ["无蓄能",["wall","double","spread","burst"],["mana","shield"]]
]
var result=[]
for b in builds:
    var p=[]
    var reactions=[]
    for id in b[1]: p.append(R.rule(id))
    for id in b[2]: reactions.append(R.rule(id))
    for mark in [-1,0,1,2]:
        var events=R.new().simulate(p,reactions,cfg,mark)
        var end=events[-1]
        var skips=[]
        for e in events:
            if e.kind=="skip" and not e.text in skips: skips.append(e.text)
        result.append({"build":b[0],"mark":mark,"victory":end.victory,"hp":end.state.hp,"rounds":end.state.round,"peak_burn":end.peak_burn,"skips":skips})
return result'''
r=c.call('editor_manage',{'session_id':session,'op':'game_eval','params':{'code':code.replace('    ','\t')}})
if r.get('isError'):raise RuntimeError(r)
data=r.get('structuredContent',{}).get('result')
(EVIDENCE/'v2-build-comparison.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(data,ensure_ascii=False,indent=2))
