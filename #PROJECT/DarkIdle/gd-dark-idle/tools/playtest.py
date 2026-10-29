"""Native Godot MCP input smoke test. Uses game_eval only for inspection/fixtures."""
import json, time
from mcp_bridge import GodotMCP, compact_images, EVIDENCE

c = GodotMCP()
session = c.project_session()
records, checks = [], []

def call(name, **args):
    r = compact_images(c.call(name, {"session_id": session, **args}), "playtest_"+str(len(records)))
    records.append({"tool":name,"args":args,"result":r})
    (EVIDENCE/"playtest.json").write_text(json.dumps({"checks":checks,"calls":records},ensure_ascii=False,indent=2),encoding="utf-8")
    if r.get("isError"): raise RuntimeError(r)
    return r.get("structuredContent",r)

def ev(code):
    return call("editor_manage",op="game_eval",params={"code":"var s = get_tree().current_scene\n"+code}).get("result")

def check(name, ok, detail=None):
    checks.append({"name":name,"passed":bool(ok),"detail":detail})
    print(name, "PASS" if ok else "FAIL",flush=True)
    if not ok: raise AssertionError((name,detail))

def click(path):
    p=ev('return s.get_viewport().get_final_transform() * s.get_node('+json.dumps(path)+').get_global_rect().get_center()')
    for pressed in (True,False):
        call("game_manage",op="input_mouse",params={"event":"button","position":[p["x"],p["y"]],"pressed":pressed})

def key(key):
    for pressed in (True,False): call("game_manage",op="input_key",params={"key":key,"pressed":pressed})

def choose(path, keys):
    click(path)
    time.sleep(.2)
    index=keys.count("Down")
    p=ev('var p = s.get_node('+json.dumps(path)+').get_popup()\nreturn {"visible":p.visible,"position":p.position,"size":p.size,"count":p.item_count,"scale":s.get_viewport().get_final_transform().x.x}')
    if not p["visible"]: raise AssertionError(("Popup did not open",path,p))
    point=[(p["position"]["x"]+p["size"]["x"]/2)*p["scale"],(p["position"]["y"]+(index+.5)*p["size"]["y"]/p["count"])*p["scale"]]
    for pressed in (True,False):
        call("game_manage",op="input_mouse",params={"event":"button","position":point,"pressed":pressed})

def snap(name):
    r=compact_images(c.call("editor_screenshot",{"session_id":session,"source":"game","max_resolution":0}),name)
    records.append({"tool":"editor_screenshot","result":r})

def status():
    return ev('return {"running":s.running,"paused":s.paused,"cursor":s.cursor,"result":s.result_data,"kind":s.events[s.cursor].kind if s.cursor >= 0 else "ready"}')

def await_result(limit=40):
    deadline=time.monotonic()+limit
    while time.monotonic()<deadline:
        st=status()
        if st["result"]: return st["result"]
        time.sleep(.35)
    raise TimeoutError(status())

try:
    original=ev('return {"plan":s.plan,"passives":s.passives}')
    click("ActivePanel/Rows/Row0/Down")
    check("原生排序按钮移动规则",ev('return s.plan[0].id == "double" and s.plan[1].id == "wall"'))
    click("ActivePanel/Rows/Row1/Up")
    click("ActivePanel/Rows/Row0/Enabled")
    check("原生复选框关闭规则",ev('return not s.plan[0].enabled'))
    click("ActivePanel/Rows/Row0/Enabled")
    choose("ActivePanel/Rows/Row2/Condition",["Home","Down"])
    choose("ActivePanel/Rows/Row2/Target",["Home","Down"])
    check("原生条件和目标下拉菜单",ev('return s.plan[2].condition == 1 and s.plan[2].target == 1'))
    choose("PassivePanel/P0/Condition",["Home","Down","Down"])
    check("原生被动附加条件",ev('return s.passives[0].condition == 2'))
    choose("PassivePanel/P0/Condition",["Home"])
    click("Controls/Motion")
    check("减弱闪震开关",ev('return s.fx.reduced'))
    click("Controls/Motion")
    click("Controls/Sound")
    check("音效开关",ev('return not s.get_node("Controls/Sound").button_pressed'))
    click("Controls/Sound")
    click("ActivePanel/Rows/Row4/Info")
    check("技能说明弹窗",ev('return s.get_node("Details").visible and s.get_node("Details/Text").text.contains("保留层数")'))
    key("Escape")
    check("关闭说明弹窗",ev('return not s.get_node("Details").visible'))
    saved=ev('return {"plan":s.plan,"passives":s.passives}')
    click("Controls/Save")
    call("project_manage",op="stop")
    call("project_run")
    check("停止进程并重开后恢复战术",ev('return {"plan":s.plan,"passives":s.passives}')==saved)
    choose("Controls/Preset",["Home","Down"])
    check("原生预设切换",ev('return s.plan[0].id == "ignite"'))
    choose("Controls/Preset",["Home"])
    click("Controls/Start")
    click("Controls/Pause")
    before=status()
    time.sleep(.35)
    after=status()
    check("开始后暂停保持游标",before["running"] and before["paused"] and before["cursor"]==after["cursor"],after)
    click("Controls/Step")
    check("单步恰好推进一个事件",status()["cursor"]==before["cursor"]+1)
    check("战斗中锁定编排",ev('return s.get_node("ActivePanel/Rows/Row0/Skill").disabled and s.get_node("Controls/Save").disabled'))
    click("Controls/Pause")
    captured=False
    deadline=time.monotonic()+40
    while time.monotonic()<deadline:
        st=status()
        if not captured and st["kind"] in ("detonate","blast"):
            snap("runtime-burn")
            captured=True
        if st["result"]:
            result=st["result"]
            break
        time.sleep(.15)
    else: raise TimeoutError("Default battle")
    check("原生播放完成胜利",result["victory"] and result["state"]["hp"]==78,result)
    check("结算后暂停单步禁用",ev('return s.get_node("Controls/Pause").disabled and s.get_node("Controls/Step").disabled'))
    snap("runtime-victory")
    click("Controls/Reset")
    check("返回编排清空结果与反馈",ev('return not s.running and s.result_data.is_empty() and s.fx.embers.is_empty() and s.get_node("Battle").position == Vector2(28,78)'))
    for i in range(7): click(f"ActivePanel/Rows/Row{i}/Enabled")
    for i in range(3): click(f"PassivePanel/P{i}/Enabled")
    choose("Controls/Speed",["Home","Down","Down"])
    check("原生四倍速",ev('return s.speed == 4.0'))
    click("Controls/Start")
    result=await_result()
    check("原生播放完成失败",not result["victory"] and result["state"]["hp"]==0,result)
    snap("runtime-defeat")
    click("Controls/Reset")
    ev('s.plan = '+json.dumps(original["plan"],ensure_ascii=False).replace("true","true")+'\ns.passives = '+json.dumps(original["passives"],ensure_ascii=False)+'\ns._refresh_rows()\nreturn true')
    choose("Controls/Speed",["Home"])
    click("Controls/Save")
    call("project_manage",op="stop")
    call("scene_open",path="res://scenes/main.tscn",force_reload=True)
    call("scene_save")
    call("project_run")
    check("最终保存重开恢复初始编排",ev('return {"plan":s.plan,"passives":s.passives}')==original)
    snap("runtime-ready")
    logs=call("logs_read",source="game",count=100)
    check("最终运行无错误日志",not any(line.get("level") in ("error","script_error") for line in logs.get("lines",[])),logs)
finally:
    (EVIDENCE/"playtest.json").write_text(json.dumps({"checks":checks,"calls":records},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"passed":sum(x["passed"] for x in checks),"failed":sum(not x["passed"] for x in checks)},ensure_ascii=False),flush=True)
