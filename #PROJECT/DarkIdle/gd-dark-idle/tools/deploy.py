from mcp_bridge import GodotMCP, compact_images, EVIDENCE
import json
c=GodotMCP()
session=c.project_session()
results=[]
def call(name,args):
    args["session_id"]=session
    r=compact_images(c.call(name,args),"deploy_"+name)
    results.append({"name":name,"result":r})
    (EVIDENCE/"deploy.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    print(name,json.dumps(r,ensure_ascii=False)[:2200],flush=True)
    if r.get("isError"):raise RuntimeError(name)
    return r
call("editor_state",{})
call("filesystem_manage",{"op":"scan"})
for key,value in {
    "application/run/main_scene":"res://scenes/main.tscn",
    "display/window/size/viewport_width":1600,
    "display/window/size/viewport_height":900,
    "display/window/size/window_width_override":1440,
    "display/window/size/window_height_override":810,
    "display/window/stretch/mode":"canvas_items",
    "display/window/stretch/aspect":"keep",
    "application/config/name":"GD_DarkIdle",
    "application/run/max_fps":60
}.items():call("project_manage",{"op":"settings_set","params":{"key":key,"value":value}})
call("scene_open",{"path":"res://scenes/main.tscn"})
call("script_attach",{"path":".","script_path":"res://scripts/battle_view.gd"})
call("scene_save",{})
call("scene_get_hierarchy",{"depth":2})
call("project_run",{})
