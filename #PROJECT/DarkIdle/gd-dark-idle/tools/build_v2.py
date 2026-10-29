"""Author native v2 TSCN/SpriteFrames resources. Read raster alpha only for pivots; never edit raster pixels."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def q(value): return json.dumps(value,ensure_ascii=False)
class Scene:
    def __init__(self,header): self.lines=[header]
    def node(self,name,kind,parent=None,props=None,instance=None):
        head=f'[node name="{name}"'
        if kind: head+=f' type="{kind}"'
        if parent is not None:head+=f' parent="{parent}"'
        if instance:head+=f' instance=ExtResource("{instance}")'
        self.lines.append(head+']')
        for key,value in (props or {}).items():self.lines.append(f'{key} = {value}')
        self.lines.append('')
    def rect(self,name,kind,parent,x,y,w,h,props=None):
        self.node(name,kind,parent,{'layout_mode':0,'offset_left':x,'offset_top':y,'offset_right':x+w,'offset_bottom':y+h,**(props or {})})
    def label(self,name,parent,x,y,w,h,text,size=18,props=None):
        self.rect(name,'Label',parent,x,y,w,h,{'text':q(text),'theme_override_font_sizes/font_size':size,'mouse_filter':2,**(props or {})})
    def button(self,name,parent,x,y,w,h,text,props=None):
        self.rect(name,'Button',parent,x,y,w,h,{'text':q(text),**(props or {})})
    def image(self,name,parent,x,y,w,h,props=None):
        self.rect(name,'TextureRect',parent,x,y,w,h,{'expand_mode':1,'stretch_mode':5,'mouse_filter':2,**(props or {})})
    def save(self,path): (ROOT/path).write_text('\n'.join(self.lines),encoding='utf-8')

metrics={}
for key,height in [('mage',220),('soot',135),('antler',220),('straw',210)]:
    path=ROOT/'assets/v2'/f'{key}-grid.png'
    image=Image.open(path).convert('RGBA');w,h=image.size
    # A generous left cell includes extended staff/claws; actual transparent gutters were inspected.
    split=int(w*.5625); half=h//2
    regions=[(0,0,split,half),(split,0,w-split,half),(0,half,split,h-half),(split,half,w-split,h-half)]
    offsets=[];bounds=[]
    for x,y,rw,rh in regions:
        alpha=image.getchannel('A').crop((x,y,x+rw,y+rh))
        box=alpha.point(lambda a:255 if a>128 else 0).getbbox()
        bottom=box[3]-1
        feet=alpha.crop((0,max(0,bottom-22),rw,bottom+1)).point(lambda a:255 if a>128 else 0).getbbox()
        pivot=(feet[0]+feet[2])/2
        offsets.append([rw/2-pivot,rh/2-bottom]);bounds.append(list(box))
    scale=height/(bounds[0][3]-bounds[0][1])
    metrics[key]={'regions':regions,'offsets':offsets,'scale':scale,'bounds':bounds,'ground_y':245}
    lines=['[gd_resource type="SpriteFrames" load_steps=6 format=3]',f'[ext_resource type="Texture2D" path="res://assets/v2/{key}-grid.png" id="1"]']
    for i,rect in enumerate(regions):
        lines.extend([f'[sub_resource type="AtlasTexture" id="F{i}"]','atlas = ExtResource("1")','region = Rect2('+', '.join(map(str,rect))+')'])
    frames=', '.join('{"duration": 1.0, "texture": SubResource("F%d")}'%i for i in [0,1,2,3,0])
    lines.extend(['[resource]','animations = [{"frames": [{"duration": 1.0, "texture": SubResource("F0")}], "loop": true, "name": &"idle", "speed": 5.0}, {"frames": ['+frames+'], "loop": false, "name": &"attack", "speed": 9.0}]'])
    (ROOT/'resources'/f'{key}_frames.tres').write_text('\n'.join(lines),encoding='utf-8')
(ROOT/'assets/v2/animation_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')

theme=['[gd_resource type="Theme" load_steps=6 format=3]','[sub_resource type="SystemFont" id="Font"]','font_names = PackedStringArray("Microsoft YaHei", "Noto Sans CJK SC")']
for id,color,border in [('Box','0.14,0.12,0.10,1','0.43,0.34,0.23,1'),('Hover','0.22,0.18,0.13,1','0.88,0.62,0.27,1'),('Selected','0.29,0.20,0.12,1','1,0.72,0.32,1'),('Red','0.48,0.12,0.07,1','0.85,0.4,0.18,1')]:
    theme += [f'[sub_resource type="StyleBoxFlat" id="{id}"]',f'bg_color = Color({color})',f'border_color = Color({border})','border_width_left = 2','border_width_right = 2','border_width_top = 2','border_width_bottom = 2','corner_radius_top_left = 4','corner_radius_top_right = 4','corner_radius_bottom_left = 4','corner_radius_bottom_right = 4','content_margin_left = 10.0','content_margin_right = 10.0']
theme+=['[resource]','default_font = SubResource("Font")','default_font_size = 18']
for kind in ['Label','Button','OptionButton','CheckButton','CheckBox','PopupMenu']:
    for color in ['font_color','font_pressed_color','font_hover_color','font_focus_color']:
        theme += [f'{kind}/colors/{color} = Color(0.95,0.86,0.70,1)']
    theme += [f'{kind}/colors/font_disabled_color = Color(0.58,0.51,0.40,1)']
for kind in ['Button','OptionButton']:
    for state,id in [('normal','Box'),('disabled','Box'),('hover','Hover'),('pressed','Selected'),('focus','Hover')]:theme += [f'{kind}/styles/{state} = SubResource("{id}")']
theme += ['Panel/styles/panel = SubResource("Box")','PopupMenu/styles/panel = SubResource("Box")','ActionButton/base_type = &"Button"','ActionButton/styles/normal = SubResource("Red")']
(ROOT/'resources/tactical_theme.tres').write_text('\n'.join(theme),encoding='utf-8')

unit=Scene('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://scripts/tactical_unit.gd" id="1"]')
unit.node('Combatant','Control',None,{'script':'ExtResource("1")','mouse_filter':2})
unit.node('Art','AnimatedSprite2D','.',{'position':'Vector2(110,245)'})
unit.rect('Ring','Control','.',0,225,220,35,{'mouse_filter':2,'show_behind_parent':'true'})
unit.button('Inspect','.',0,72,220,178,'',{'flat':'true','mouse_default_cursor_shape':2})
unit.button('Intent','.',25,4,170,40,'')
unit.image('IntentIcon','Intent',8,4,32,32)
unit.label('IntentCost','Intent',47,5,115,28,'主动 · 1 AP',16)
unit.button('Reaction','.',45,48,130,28,'无被动 · 0 RP',{'theme_override_font_sizes/font_size':14})
unit.rect('Plate','Panel','.',0,262,220,75,{'mouse_filter':2})
unit.label('Mark','.',8,263,24,28,'◆',18,{'visible':'false','horizontal_alignment':1,'theme_override_colors/font_color':'Color(1,0.78,0.32,1)'})
unit.label('Name','.',8,265,204,22,'单位',17,{'horizontal_alignment':1})
unit.rect('Health','ProgressBar','.',14,291,192,8,{'show_percentage':'false','mouse_filter':2})
unit.label('Numbers','.',8,305,204,24,'',15,{'horizontal_alignment':1})
unit.button('Burn','.',37,232,146,28,'',{'visible':'false','theme_override_font_sizes/font_size':15})
unit.save('scenes/tactical_unit.tscn')

s=Scene('''[gd_scene load_steps=7 format=3]
[ext_resource type="Theme" path="res://resources/tactical_theme.tres" id="1"]
[ext_resource type="Texture2D" path="res://assets/v2/ground.png" id="2"]
[ext_resource type="Script" path="res://scripts/tactical_view.gd" id="3"]
[ext_resource type="PackedScene" path="res://scenes/tactical_unit.tscn" id="4"]
[ext_resource type="Script" path="res://scripts/tactical_fx.gd" id="5"]
[ext_resource type="Script" path="res://scripts/action_track.gd" id="6"]
''')
s.node('DarkIdle','Control',None,{'layout_mode':3,'anchors_preset':15,'anchor_right':1.0,'anchor_bottom':1.0,'grow_horizontal':2,'grow_vertical':2,'theme':'ExtResource("1")','script':'ExtResource("3")'})
s.rect('Paper','ColorRect','.',0,0,1600,900,{'color':'Color(0.075,0.065,0.055,1)','mouse_filter':2})
s.label('Header','.',28,8,800,44,'DARK IDLE   /   烬火试炼',28)
s.label('Round','.',1300,12,270,36,'战前编排',20,{'horizontal_alignment':2})
s.rect('Track','Panel','.',28,62,1544,64,{'script':'ExtResource("6")'})
s.label('Title','Track',14,16,100,30,'行动轴',17)
s.rect('Line','ColorRect','Track',122,31,1350,3,{'color':'Color(0.54,0.39,0.22,1)','mouse_filter':2})
s.label('End','Track',1465,10,65,42,'出手',16,{'horizontal_alignment':2})
for i in range(4):
    s.button(f'Actor{i}','Track',110,10,44,44,'',{'pivot_offset':'Vector2(22,22)'})
    s.image('Portrait',f'Track/Actor{i}',4,3,36,38)
s.rect('Battle','Control','.',28,138,1544,350)
s.rect('Backdrop','TextureRect','Battle',0,0,1544,350,{'texture':'ExtResource("2")','expand_mode':1,'stretch_mode':0,'mouse_filter':2})
for i,x in enumerate([110,610,925,1240]):
    s.node(f'Unit{i}',None,'Battle',{'offset_left':x,'offset_top':0,'offset_right':x+220,'offset_bottom':340},instance='4')
s.rect('FX','Control','Battle',0,0,1544,350,{'mouse_filter':2,'script':'ExtResource("5")'})
s.label('Banner','Battle',340,100,480,80,'',30,{'horizontal_alignment':1,'theme_override_colors/font_outline_color':'Color(0.12,0.07,0.04,1)','theme_override_constants/outline_size':6})
s.label('ActiveTitle','.',28,503,1000,30,'行动序列 · 4 个装备槽',21)
s.rect('Slots','Control','.',28,543,1000,162)
for i in range(4):
    p=f'Slots/A{i}'
    s.button(f'A{i}','Slots',i*246,0,232,158,'')
    s.label('Order',p,14,8,100,24,f'行动 0{i+1}',14)
    s.image('Icon',p,14,37,88,80)
    s.label('Name',p,110,42,110,28,'',21)
    s.label('Cost',p,110,78,100,24,'',17)
    s.label('Condition',p,14,123,140,24,'总是',14)
    s.button('Tune',p,174,7,45,25,'设置',{'theme_override_font_sizes/font_size':14})
    s.button('Left',p,158,122,28,26,'‹')
    s.button('Right',p,191,122,28,26,'›')
s.label('PassiveTitle','.',28,714,500,28,'反应装备 · 2 个装备槽',20)
s.rect('Reactions','Control','.',28,750,500,76)
for i in range(2):
    p=f'Reactions/P{i}'
    s.button(f'P{i}','Reactions',i*246,0,232,76,'')
    s.image('Icon',p,12,8,60,60)
    s.label('Name',p,82,10,140,27,'',19)
    s.label('Cost',p,82,39,140,26,'',14)
    s.button('Tune',p,188,5,35,22,'设',{'theme_override_font_sizes/font_size':13})
s.label('TargetHint','.',550,748,475,34,'优先目标：自动',18)
s.label('Feedback','.',550,782,475,38,'点击技能槽装备；悬停查看详情',16,{'autowrap_mode':2})
s.rect('Details','Panel','.',1050,503,522,323)
s.image('Icon','Details',16,16,76,76)
s.label('Title','Details',110,16,390,36,'战前准备',23)
s.label('Cost','Details',110,58,390,30,'',17)
s.rect('Text','RichTextLabel','Details',16,108,490,95,{'bbcode_enabled':'true','theme_override_colors/default_color':'Color(0.94,0.85,0.69,1)','theme_override_font_sizes/normal_font_size':18,'mouse_filter':2})
s.rect('Config','Control','Details',16,205,490,103,{'visible':'false'})
s.label('Label','Details/Config',0,0,470,23,'',14)
s.rect('Condition','OptionButton','Details/Config',0,29,237,32)
s.rect('Target','OptionButton','Details/Config',248,29,242,32)
s.rect('Enabled','CheckBox','Details/Config',0,67,140,30,{'text':q('启用规则')})
s.button('Preview','Details',328,281,177,30,'试放预览',{'visible':'false','theme_override_font_sizes/font_size':16})
s.rect('Library','Panel','.',28,503,1000,323,{'visible':'false'})
s.label('Title','Library',18,12,720,40,'选择技能',23)
s.button('Close','Library',935,12,46,34,'×')
for i in range(7):
    p=f'Library/Choice{i}'
    s.button(f'Choice{i}','Library',18+i*137,64,126,166,'')
    s.image('Icon',p,20,12,86,86)
    s.label('Name',p,4,105,118,27,'',20,{'horizontal_alignment':1})
    s.label('Cost',p,4,137,118,22,'',15,{'horizontal_alignment':1})
s.button('Equip','Library',18,263,190,40,'装备到当前槽',{'theme_type_variation':'&"ActionButton"'})
s.button('Remove','Library',222,263,125,40,'卸下')
s.label('Hint','Library',370,264,600,40,'悬停查看效果 · 点击选择 · 试放预览',16)
s.rect('Settings','Panel','.',1050,503,522,323,{'visible':'false'})
s.label('Title','Settings',18,12,450,40,'设置',23)
for name,y,text in [('ClickTarget',66,'点击怪物设置优先目标'),('Motion',118,'减弱闪震'),('Sound',170,'音效')]:s.rect(name,'CheckButton','Settings',18,y,478,40,{'text':q(text)})
s.button('ClearTarget','Settings',18,230,250,36,'清除优先目标')
s.button('Close','Settings',330,270,174,36,'返回')
s.rect('Controls','HBoxContainer','.',28,846,1544,38,{'theme_override_constants/separation':10})
for name,kind,w,text in [('Preset','OptionButton',240,''),('Start','Button',166,'开始战斗'),('Pause','Button',90,'暂停'),('Step','Button',80,'单步'),('Speed','OptionButton',110,''),('Reset','Button',126,'返回编排'),('Save','Button',126,'保存战术'),('Settings','Button',100,'设置')]:
    s.node(name,kind,'Controls',{'custom_minimum_size':f'Vector2({w},38)','layout_mode':2,'text':q(text),**({'theme_type_variation':'&"ActionButton"'} if name=='Start' else {})})
s.node('Playback','Timer','.',{'one_shot':'true','wait_time':0.4})
s.node('PreviewReset','Timer','.',{'one_shot':'true','wait_time':0.8})
s.node('SoundPlayer','AudioStreamPlayer','.',{'volume_db':-18.0})
s.save('scenes/tactical_main.tscn')
print('Native v2 scenes, theme, four SpriteFrames resources and pivot metadata authored.')
