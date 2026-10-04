"""One-time native MCP scene authoring. Do not rerun over artist-edited scenes.

All nodes are created by Godot's editor handlers with native UndoRedo and owners.
Saved .tscn/.tres files, not this scaffold, are the continuing editing source.
"""
import json
from mcp_bridge import GodotMCP, EVIDENCE

client = GodotMCP()
trace = []
current = ""


def call(tool_name, **arguments):
    result = client.call(tool_name, arguments)
    trace.append({"tool": tool_name, "arguments": arguments, "result": result})
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "scene-authoring.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    data = result.get("structuredContent", {})
    if result.get("isError") or data.get("success") is False or data.get("error"):
        print(json.dumps(result, ensure_ascii=False), flush=True)
        raise RuntimeError(tool_name)
    return data


def node(kind, name, children=None, **props):
    spec = {"type": kind, "name": name, "properties": props}
    if children:
        spec["children"] = children
    return spec


def label(name, text, size=20, **props):
    return node("Label", name, text=text, **{"theme_override_font_sizes/font_size": size}, **props)


def button(name, text):
    return node("Button", name, text=text, custom_minimum_size={"x": 0, "y": 46})


def rich(name, text="", height=120, expand=False):
    return node("RichTextLabel", name, text=text, bbcode_enabled=True,
                custom_minimum_size={"x": 0, "y": height}, size_flags_vertical=3 if expand else 1,
                **{"theme_override_font_sizes/normal_font_size": 18})


def box(kind, name, children, **props):
    return node(kind, name, children, **{"theme_override_constants/separation": 12}, **props)


def full(spec):
    spec["anchor_preset"] = "full_rect"
    return spec


def create(name, kind="Control", folder=""):
    global current
    current = f"res://scenes/expedition/{folder}{name}.tscn"
    call("scene_manage", op="create", params={"path": current, "root_type": kind, "root_name": name})
    if kind in ["Control", "PanelContainer", "VBoxContainer", "HBoxContainer"]:
        call("ui_manage", op="set_anchor_preset", params={"path": "/" + name, "preset": "full_rect"})
    return "/" + name


def build(root, tree):
    call("ui_manage", op="build_layout", params={"parent_path": root, "tree": tree})


def prop(path, key, value):
    call("node_set_property", path=path, property=key, value=value, scene_file=current)


def attach(path, file):
    call("script_attach", path=path, script_path="res://scripts/expedition/ui/" + file)


def instance(parent, scene, name):
    call("node_create", parent_path=parent, scene_path="res://scenes/expedition/" + scene + ".tscn", name=name, scene_file=current)


def save():
    call("scene_save")
    print("Saved", current, flush=True)


call("session_activate", session_id="cat-idle")
theme = "res://resources/expedition/ExpeditionTheme.tres"
call("theme_manage", op="create", params={"path": theme})
for cls in ["Label", "Button", "OptionButton", "ItemList", "TabContainer"]:
    call("theme_manage", op="set_font_size", params={"theme_path": theme, "class_name": cls, "name": "font_size", "value": 20})
    for color_name, color in [("font_color", "#e8e3d8"), ("font_hover_color", "#fff4cf"), ("font_disabled_color", "#82908f")]:
        call("theme_manage", op="set_color", params={"theme_path": theme, "class_name": cls, "name": color_name, "value": color})
for cls, slots in {"PanelContainer": ["panel"], "Button": ["normal", "hover", "pressed", "disabled", "focus"],
                   "OptionButton": ["normal", "hover", "pressed", "disabled", "focus"],
                   "TabContainer": ["panel", "tab_selected", "tab_unselected", "tab_hovered"],
                   "ItemList": ["panel", "selected", "selected_focus"]}.items():
    for slot in slots:
        active = slot in ["hover", "pressed", "tab_selected", "tab_hovered", "selected", "selected_focus"]
        call("theme_manage", op="set_stylebox_flat", params={"theme_path": theme, "class_name": cls, "name": slot,
             "bg_color": "#284a4e" if active else ("#0c191f" if slot == "disabled" else "#15272f"),
             "border_color": "#ad9869" if active else "#2c454d", "border": {"all": 1},
             "corners": {"all": 7}, "margins": {"all": 12}})
for slot, color in [("background", "#0c1b22"), ("fill", "#71bca7")]:
    call("theme_manage", op="set_stylebox_flat", params={"theme_path": theme, "class_name": "ProgressBar", "name": slot, "bg_color": color, "corners": {"all": 4}})

root = create("UnitCard", "PanelContainer", "components/")
prop(root, "custom_minimum_size", {"x": 230, "y": 138})
build(root, box("VBoxContainer", "Rows", [label("Name", "01  远征者", 21),
    node("ProgressBar", "Health", value=100, show_percentage=False, custom_minimum_size={"x": 0, "y": 9}),
    label("HealthText", "生命 160 / 160   护盾 0", 16), label("Stats", "攻 24    甲 5    速 12", 17), label("Status", "就绪", 15)]))
attach(root, "FogUnitCard.gd")
save()

root = create("RegionTile", folder="components/")
prop(root, "size", {"x": 600, "y": 640})
build(root, node("Polygon2D", "Land"))
build(root, node("Line2D", "Border", width=2.0, closed=True))
build(root, label("Caption", "地图地区", 21, horizontal_alignment=1, mouse_filter=2))
build(root, label("Detail", "套装地标", 15, horizontal_alignment=1, mouse_filter=2))
attach(root, "FogRegionTile.gd")
prop(root, "definition", "res://resources/expedition/regions/briar.tres")
save()

root = create("MapPage")
build(root, full(box("HBoxContainer", "MapColumns", [
    box("VBoxContainer", "SquadColumn", [label("SquadHeading", "远征小队", 24),
        label("Budget", "整备后出发", 21), node("ProgressBar", "BudgetBar", max_value=6, value=6, show_percentage=False, custom_minimum_size={"x": 0, "y": 8}),
        box("VBoxContainer", "PartyCards", []), label("SetSummary", "尚未成套", 19),
        label("PartyNote", "前排承受多数攻击", 16, autowrap_mode=2),
        label("Legend", "金色 · 所在地区 / 选中\n青色边界 · 可以前往\n深色 · 未探明地区", 16)], custom_minimum_size={"x": 265, "y": 0}),
    box("VBoxContainer", "AtlasColumn", [label("AtlasTitle", "向北，穿越迷雾", 28, horizontal_alignment=1),
        node("Control", "MapBoard", [node("Control", "World", mouse_filter=2)], size_flags_horizontal=3, size_flags_vertical=3, custom_minimum_size={"x": 500, "y": 400}, mouse_filter=2),
        label("AtlasCaption", "鹿鸣村 → 三个地区 → 魔王城", 17, horizontal_alignment=1)], size_flags_horizontal=3),
    box("VBoxContainer", "RegionColumn", [label("RegionTitle", "荆棘林地", 28), rich("RegionDescription", height=225),
        button("EnterRegion", "选择相邻前方地区"), node("HSeparator", "Divider"), label("ActivityHeading", "当前地区 · 可用行动", 20),
        *[button(f"Activity{i}", "活动") for i in range(5)],
        label("ActivityHint", "可提前离开，无法回头。", 16, autowrap_mode=2)], custom_minimum_size={"x": 350, "y": 0})
])))
for i in range(3):
    instance(root + "/MapColumns/SquadColumn/PartyCards", "components/UnitCard", f"Party{i}")
board = root + "/MapColumns/AtlasColumn/MapBoard"
attach(board, "FogMapBoard.gd")
for region in ["castle", "frost", "ash", "quarry", "river", "ember", "briar", "ruins", "village"]:
    instance(board + "/World", "components/RegionTile", region.capitalize())
    prop(board + "/World/" + region.capitalize(), "definition", f"res://resources/expedition/regions/{region}.tres")
save()

root = create("LoadoutPage")
build(root, full(box("VBoxContainer", "LoadoutRows", [label("LoadoutTitle", "战前整备", 30),
    label("Formation", "前排  主角 → 牧师  后排", 22),
    box("HBoxContainer", "FormationActions", [button("SwapFront", "交换 1 ↔ 2"), button("SwapRear", "交换 2 ↔ 3")]),
    box("HBoxContainer", "LoadoutColumns", [
        box("VBoxContainer", "TacticsColumn", [label("TacticsHeading", "自动战术", 24),
            label("ActiveLabel", "主角主动技能", 17), node("OptionButton", "ActiveChoice"),
            label("PassiveLabel", "主角被动", 17), node("OptionButton", "PassiveChoice"),
            label("TargetLabel", "攻击目标", 17), node("OptionButton", "TargetChoice"),
            label("PolicyLabel", "技能释放时机", 17), node("OptionButton", "PolicyChoice"),
            button("ApplyTactics", "应用战术"), rich("TacticHelp", "调整仅在战外生效。\n\n铁壁可等待重击威胁；重击可等待标记，最多等一次自身行动。\n\n改变生命上限不会免费治疗。", 130)], custom_minimum_size={"x": 340, "y": 0}),
        box("VBoxContainer", "EquipmentColumn", [label("EquipmentHeading", "主角当前装备", 24), rich("Equipped", "三个部位尚未装备", 320, True)], size_flags_horizontal=3),
        box("VBoxContainer", "InventoryColumn", [label("InventoryHeading", "远征背包", 24),
            node("ItemList", "Inventory", size_flags_vertical=3, custom_minimum_size={"x": 365, "y": 200}),
            rich("Comparison", "选择装备查看详情。", 220), button("EquipItem", "装备到对应部位")], size_flags_horizontal=3)
    ], size_flags_vertical=3)])))
save()

root = create("BattlePage")
build(root, full(box("VBoxContainer", "BattleRows", [
    box("HBoxContainer", "BattleHeader", [label("RoundTitle", "等待第一场战斗", 28),
        node("Control", "HeaderSpacer", size_flags_horizontal=3), button("Pause", "暂停"),
        *[button(f"Speed{i}", f"{i}x") for i in [1, 2, 4]], button("Skip", "跳过回放"), button("Claim", "查看战报 / 领取")]),
    label("BattleIntent", "战斗全自动 · 速度决定回合顺序", 21, autowrap_mode=2),
    label("AllyHeading", "远征小队  ·  左侧为前排", 18), box("HBoxContainer", "Allies", []),
    label("EnemyHeading", "敌方阵列  ·  左侧为前排", 18), box("HBoxContainer", "Enemies", []),
    rich("CombatLog", "战斗事件将在这里显示。", 100, True)])))
for side, prefix in [("Allies", "Ally"), ("Enemies", "Enemy")]:
    for i in range(3):
        instance(root + "/BattleRows/" + side, "components/UnitCard", f"{prefix}{i}")
        prop(root + "/BattleRows/" + side + f"/{prefix}{i}", "size_flags_horizontal", 3)
prop(root + "/BattleRows/CombatLog", "scroll_following", True)
save()

root = create("DecisionModal", folder="components/")
prop(root, "mouse_filter", 0)
build(root, full(node("ColorRect", "Scrim", color="#071018e8", mouse_filter=0)))
build(root, full(node("CenterContainer", "Center", [node("PanelContainer", "Panel", [
    box("VBoxContainer", "ModalRows", [label("ModalTitle", "雾境远征", 32),
        rich("ModalDescription", "整备小队，穿越迷雾。", 330),
        node("OptionButton", "ModalOptionA"), node("OptionButton", "ModalOptionB"),
        box("HBoxContainer", "ModalButtons", [button(f"ModalAction{i}", f"选项{i+1}") for i in range(3)])])],
    custom_minimum_size={"x": 740, "y": 0})])))
save()

root = create("ExpeditionDemo")
prop(root, "size", {"x": 1600, "y": 900})
call("theme_manage", op="apply", params={"node_path": root, "theme_path": theme})
build(root, full(node("ColorRect", "Background", color="#0c171e", mouse_filter=2)))
build(root, full(node("MarginContainer", "SafeArea", [box("VBoxContainer", "Shell", [
    box("HBoxContainer", "Header", [box("VBoxContainer", "Brand", [label("Title", "雾境远征", 34), label("Subtitle", "FOGBOUND  /  三人小队 · 向北而行", 15)]),
        node("Control", "BrandSpacer", size_flags_horizontal=3), label("Summary", "小队 Lv.1   金币 15", 20),
        button("NewRun", "新远征"), button("ContinueRun", "继续"), button("Help", "手册")]),
    node("TabContainer", "Pages", size_flags_vertical=3),
    box("HBoxContainer", "FooterRow", [label("Footer", "准备出发", 17, size_flags_horizontal=3, text_overrun_behavior=3),
        button("Pending", "处理待结算内容"), label("SaveStatus", "准备出发", 16)])])],
    **{f"theme_override_constants/margin_{side}": 24 for side in ["left", "top", "right", "bottom"]})))
for page, name in [("MapPage", "远征地图"), ("LoadoutPage", "小队整备"), ("BattlePage", "自动战斗")]:
    instance(root + "/SafeArea/Shell/Pages", page, name)
instance(root, "components/DecisionModal", "Modal")
prop(root + "/Modal", "visible", False)
attach(root, "FogDemo.gd")
prop(root, "catalog", "res://resources/expedition/catalog.tres")
save()
for key, value in [("display/window/size/viewport_width", 1600), ("display/window/size/viewport_height", 900),
                   ("display/window/size/window_width_override", 1440), ("display/window/size/window_height_override", 810),
                   ("display/window/stretch/mode", "canvas_items")]:
    call("project_manage", op="settings_set", params={"key": key, "value": value})
print("Native editable scene generation completed.", flush=True)
