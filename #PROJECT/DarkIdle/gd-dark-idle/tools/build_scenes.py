"""Serialize editable Godot scenes; deploy and re-open using the real MCP client."""
import json, math, wave, struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def q(v): return json.dumps(v,ensure_ascii=False)
class Scene:
    def __init__(self, header):
        self.text=[header]
    def node(self,name,kind,parent=None,props=None,instance=None):
        a=f'[node name="{name}"'
        a+=f' type="{kind}"' if not instance else f' parent="{parent}" instance=ExtResource("{instance}")'
        if parent is not None and not instance:a+=f' parent="{parent}"'
        self.text.append(a+']')
        for k,v in (props or {}).items():self.text.append(f'{k} = {v}')
        self.text.append('')
    def rect(self,name,kind,parent,x,y,w,h,props=None):
        p={"layout_mode":0,"offset_left":x,"offset_top":y,"offset_right":x+w,"offset_bottom":y+h}
        p.update(props or {});self.node(name,kind,parent,p)
    def save(self,path): (ROOT/path).write_text('\n'.join(self.text),encoding="utf-8")
theme='''[gd_resource type="Theme" load_steps=3 format=3]
[sub_resource type="SystemFont" id="Font"]
font_names = PackedStringArray("Microsoft YaHei", "Noto Sans CJK SC")
[sub_resource type="StyleBoxFlat" id="Box"]
bg_color = Color(0.88, 0.81, 0.67, 1)
border_width_left = 1
border_width_top = 1
border_width_right = 1
border_width_bottom = 2
border_color = Color(0.32, 0.25, 0.19, 1)
corner_radius_top_left = 3
corner_radius_top_right = 3
corner_radius_bottom_left = 3
corner_radius_bottom_right = 3
content_margin_left = 10.0
content_margin_right = 10.0
[resource]
default_font = SubResource("Font")
default_font_size = 18
Label/colors/font_color = Color(0.16, 0.12, 0.1, 1)
Button/colors/font_color = Color(0.16, 0.12, 0.1, 1)
Button/styles/normal = SubResource("Box")
OptionButton/colors/font_color = Color(0.16, 0.12, 0.1, 1)
OptionButton/styles/normal = SubResource("Box")
OptionButton/styles/disabled = SubResource("Box")
OptionButton/colors/font_disabled_color = Color(0.37, 0.29, 0.22, 1)
Button/styles/disabled = SubResource("Box")
Button/colors/font_disabled_color = Color(0.37, 0.29, 0.22, 1)
CheckButton/colors/font_color = Color(0.16, 0.12, 0.1, 1)
CheckButton/colors/font_pressed_color = Color(0.16, 0.12, 0.1, 1)
CheckButton/colors/font_hover_color = Color(0.16, 0.12, 0.1, 1)
Panel/styles/panel = SubResource("Box")
'''
(ROOT/"resources/paper_theme.tres").write_text(theme,encoding="utf-8")
row=Scene('[gd_scene format=3]\n')
row.node("RuleRow","HBoxContainer",None,{"custom_minimum_size":"Vector2(0, 38)","theme_override_constants/separation":6})
for name,kind,w,props in [
    ("Enabled","CheckBox",34,{}),("Order","Label",24,{}),
    ("Skill","OptionButton",140,{}),("Cost","Label",64,{}),
    ("Condition","OptionButton",260,{}),("Target","OptionButton",200,{}),
    ("Up","Button",40,{"text":q("↑")}),("Down","Button",40,{"text":q("↓")}),
    ("Info","Button",40,{"text":q("?")})]:
    row.node(name,kind,".",{"custom_minimum_size":f"Vector2({w}, 36)","layout_mode":2,**props})
row.save("scenes/rule_row.tscn")
unit=Scene('[gd_scene format=3]\n')
unit.node("Combatant","Control",None,{"custom_minimum_size":"Vector2(230, 292)","mouse_filter":2})
unit.rect("Art","TextureRect",".",5,12,220,210,{"expand_mode":1,"stretch_mode":5,"mouse_filter":2,"pivot_offset":"Vector2(110, 200)"})
unit.rect("Plate","ColorRect",".",0,218,230,76,{"color":"Color(0.86,0.79,0.65,0.94)","mouse_filter":2})
unit.rect("Name","Label",".",0,218,230,26,{"text":q("单位"),"horizontal_alignment":1})
unit.rect("Health","ProgressBar",".",20,248,190,14,{"show_percentage":"false","value":100})
unit.rect("Numbers","Label",".",20,264,190,26,{"text":q("100 / 100"),"horizontal_alignment":1,"theme_override_font_sizes/font_size":16})
unit.rect("BurnPlate","ColorRect",".",0,188,230,30,{"visible":"false","color":"Color(0.15,0.09,0.04,0.94)","mouse_filter":2})
unit.rect("Burn","Label",".",0,188,230,30,{"text":q(""),"horizontal_alignment":1,"theme_override_font_sizes/font_size":18,"theme_override_colors/font_color":"Color(1,0.69,0.31,1)"})
unit.save("scenes/combatant.tscn")
s=Scene('''[gd_scene load_steps=7 format=3]
[ext_resource type="Theme" path="res://resources/paper_theme.tres" id="1"]
[ext_resource type="Texture2D" path="res://assets/orchard.png" id="2"]
[ext_resource type="PackedScene" path="res://scenes/rule_row.tscn" id="3"]
[ext_resource type="PackedScene" path="res://scenes/combatant.tscn" id="4"]
[ext_resource type="Script" path="res://scripts/battle_view.gd" id="5"]
[ext_resource type="Script" path="res://scripts/battle_fx.gd" id="6"]
''')
s.node("DarkIdle","Control",None,{"layout_mode":3,"anchors_preset":15,"anchor_right":1.0,"anchor_bottom":1.0,"grow_horizontal":2,"grow_vertical":2,"theme":'ExtResource("1")',"script":'ExtResource("5")'})
s.rect("Paper","ColorRect",".",0,0,1600,900,{"color":"Color(0.82,0.75,0.62,1)","mouse_filter":2})
s.rect("Header","Label",".",28,12,920,60,{"text":q("DARK IDLE   /   燃爆法师"),"theme_override_font_sizes/font_size":32})
s.rect("Subtitle","Label",".",1030,20,540,40,{"text":q("铺火 · 翻倍 · 扩散 · 核爆"),"horizontal_alignment":2})
s.rect("Battle","Control",".",28,78,1544,320)
s.rect("Backdrop","TextureRect","Battle",0,0,1544,320,{"texture":'ExtResource("2")',"expand_mode":1,"stretch_mode":6,"mouse_filter":2})
for i,(x,idx) in enumerate([(110,0),(660,1),(965,2),(1250,3)]):
    s.node("Mage" if i==0 else f"Enemy{i}","", "Battle", {"offset_left":x,"offset_top":22,"offset_right":x+230,"offset_bottom":314},instance="4")
s.rect("FX","Control","Battle",0,0,1544,320,{"mouse_filter":2,"script":'ExtResource("6")'})
s.rect("Banner","Label","Battle",360,5,720,46,{"text":q("战前准备"),"horizontal_alignment":1,"theme_override_font_sizes/font_size":24,"theme_override_colors/font_color":"Color(0.97,0.87,0.68,1)","theme_override_colors/font_outline_color":"Color(0.16,0.09,0.05,1)","theme_override_constants/outline_size":6})
s.rect("Status","Label",".",28,408,1544,36,{"text":q("AP 6    RP 3    燃烧：每层 8 伤害 · 回合末引爆清空"),"theme_override_font_sizes/font_size":21})
s.rect("ActivePanel","Panel",".",28,455,1000,350)
s.rect("Title","Label","ActivePanel",16,8,970,34,{"text":q("主动序列   /   每回合自上而下，各执行一次"),"theme_override_font_sizes/font_size":22})
s.rect("Columns","Label","ActivePanel",14,44,970,26,{"text":q("启用 / 序号     施放技能          费用      发动条件                                目标偏好                   排序 / 详情"),"theme_override_font_sizes/font_size":15})
s.rect("Rows","VBoxContainer","ActivePanel",14,74,970,266,{"theme_override_constants/separation":0})
for i in range(7):s.node(f"Row{i}","","ActivePanel/Rows",{"layout_mode":2},instance="3")
s.rect("PassivePanel","Panel",".",1048,455,524,176)
s.rect("Title","Label","PassivePanel",14,8,490,30,{"text":q("被动反应   /   每次消耗 1 RP"),"theme_override_font_sizes/font_size":22})
for i in range(3):
    s.rect(f"P{i}","HBoxContainer","PassivePanel",12,48+i*40,495,38)
    for name,kind,w in [("Enabled","CheckBox",30),("Name","Label",196),("Condition","OptionButton",180),("Info","Button",40)]:
        s.node(name,kind,f"PassivePanel/P{i}",{"custom_minimum_size":f"Vector2({w}, 34)","layout_mode":2,**({"text":q("?")} if name=="Info" else {}),**({"theme_override_font_sizes/font_size":17} if name=="Name" else {})})
s.rect("LogPanel","Panel",".",1048,645,524,160)
s.rect("Log","RichTextLabel","LogPanel",14,8,495,145,{"bbcode_enabled":"true","scroll_following":"true","theme_override_colors/default_color":"Color(0.18,0.13,0.1,1)","theme_override_font_sizes/normal_font_size":16})
s.rect("Controls","HBoxContainer",".",28,825,1544,48,{"theme_override_constants/separation":10})
for name,kind,w,props in [
    ("Preset","OptionButton",218,{}),("Start","Button",158,{"text":q("开始战斗")}),
    ("Pause","Button",92,{"text":q("暂停")}),("Step","Button",108,{"text":q("单步")}),
    ("Speed","OptionButton",100,{}),("Reset","Button",135,{"text":q("返回编排")}),
    ("Save","Button",125,{"text":q("保存战术")}),("Motion","CheckButton",140,{"text":q("减弱闪震")}),
    ("Sound","CheckButton",115,{"text":q("音效")}),("Help","Button",75,{"text":q("规则")})]:
    s.node(name,kind,"Controls",{"custom_minimum_size":f"Vector2({w}, 46)","layout_mode":2,**props})
s.node("Details","AcceptDialog",".",{"title":q("法术说明"),"size":"Vector2i(680, 400)"})
s.rect("Text","RichTextLabel","Details",22,24,636,300,{"bbcode_enabled":"true","theme_override_colors/default_color":"Color(0.95,0.88,0.74,1)"})
s.node("SoundPlayer","AudioStreamPlayer",".",{"volume_db":-16.0})
s.node("Playback","Timer",".",{"wait_time":0.55})
s.save("scenes/main.tscn")
# Original synthesized game cues, no third-party audio dependencies.
for name,freq,dur in [("cast",440,.20),("hit",110,.13),("blast",60,.45),("buff",660,.25)]:
    path=ROOT/"assets"/(name+".wav")
    with wave.open(str(path),"wb") as f:
        f.setparams((1,2,22050,0,"NONE","not compressed"))
        data=[]
        for i in range(int(22050*dur)):
            t=i/22050; env=(1-t/dur)**2
            signal=math.sin(2*math.pi*(freq*t-freq*.2*t*t/dur))
            if name=="blast": signal=.7*signal+.3*math.sin(2*math.pi*193*t)*math.sin(2*math.pi*71*t)
            data.append(struct.pack("<h",int(11000*env*signal)))
        f.writeframes(b"".join(data))
print("Created native scene resources and four original sound cues.")
