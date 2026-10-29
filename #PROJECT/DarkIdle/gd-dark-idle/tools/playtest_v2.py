"""v2 native mouse acceptance. game_eval is inspection or explicitly noted fixture setup."""
import argparse, json, time
from mcp_bridge import GodotMCP, compact_images, EVIDENCE

parser=argparse.ArgumentParser(); parser.add_argument('phase',choices=['ui','combat','preview','final']); args=parser.parse_args()
c=GodotMCP(); session=c.project_session(); records=[]; checks=[]
prefix='v2-'+args.phase
def flush():
    (EVIDENCE/(prefix+'.json')).write_text(json.dumps({'checks':checks,'calls':records},ensure_ascii=False,indent=2),encoding='utf-8')
def call(name,**arguments):
    result=compact_images(c.call(name,{'session_id':session,**arguments}),prefix+'_'+str(len(records)))
    records.append({'tool':name,'args':arguments,'result':result}); flush()
    if result.get('isError'): raise RuntimeError(result)
    return result.get('structuredContent',result)
def ev(code):
    return call('editor_manage',op='game_eval',params={'code':'var s = get_tree().current_scene\n'+code}).get('result')
def check(name,value,detail=None):
    checks.append({'name':name,'passed':bool(value),'detail':detail}); flush(); print(name,'PASS' if value else 'FAIL',flush=True)
    if not value: raise AssertionError((name,detail))
def pointer(path,event='button'):
    p=ev('return s.get_viewport().get_final_transform()*s.get_node('+json.dumps(path)+').get_global_rect().get_center()')
    point=[p['x'],p['y']]
    call('game_manage',op='input_mouse',params={'event':'motion','position':point})
    if event=='button':
        for down in (True,False):call('game_manage',op='input_mouse',params={'event':'button','position':point,'pressed':down})
def click(path):pointer(path)
def hover(path):pointer(path,'motion')
def choose(path,index):
    click(path);time.sleep(.15)
    p=ev('var p = s.get_node('+json.dumps(path)+').get_popup()\nreturn {"visible":p.visible,"position":p.position,"size":p.size,"count":p.item_count,"scale":s.get_viewport().get_final_transform().x.x}')
    if not p['visible']:raise AssertionError(('dropdown',path,p))
    point=[(p['position']['x']+p['size']['x']/2)*p['scale'],(p['position']['y']+(index+.5)*p['size']['y']/p['count'])*p['scale']]
    for down in (True,False):call('game_manage',op='input_mouse',params={'event':'button','position':point,'pressed':down})
def snap(label):
    result=compact_images(c.call('editor_screenshot',{'session_id':session,'source':'game','max_resolution':0}),'v2-'+label)
    records.append({'tool':'screenshot','result':result});flush()
def st():return ev('return {"running":s.running,"previewing":s.previewing,"paused":s.paused,"cursor":s.cursor,"kind":s.events[s.cursor].kind if s.cursor>=0 else "ready","actor":s.events[s.cursor].actor if s.cursor>=0 else -1,"result":s.result_data,"transfer_played":s.fx.history.any(func(e):return e.text=="余烬转移" and e.actor==2)}')
def wait_done(limit=45):
    deadline=time.monotonic()+limit
    while time.monotonic()<deadline:
        value=st()
        if value['result']:return value['result']
        time.sleep(.2)
    raise TimeoutError(value)
try:
    click('Controls/Reset')
    if args.phase=='ui':
        choose('Controls/Preset',0)
        check('固定四行动和二反应槽',ev('return s.get_node("Slots").get_child_count()==4 and s.get_node("Reactions").get_child_count()==2'))
        click('Slots/A0')
        check('点击槽打开装备库',ev('return s.get_node("Library").visible and s.selected_slot==0'))
        hover('Library/Choice5')
        check('候选悬停在右下显示炎爆效果',ev('return s.get_node("Details/Title").text=="炎爆" and s.get_node("Details/Text").text.contains("转移") and s.get_node("Details/Cost").text=="1 AP"'))
        snap('library')
        click('Library/Choice0');click('Library/Equip')
        check('装备后出现对应规则设置',ev('return s.plan[0].id=="ignite" and s.get_node("Details/Config").visible'))
        choose('Details/Config/Condition',1);choose('Details/Config/Target',2)
        check('条件与目标实际写入装备槽',ev('return s.plan[0].condition==1 and s.plan[0].target==2'))
        click('Details/Config/Enabled')
        check('禁用该规则',ev('return not s.plan[0].enabled'))
        click('Details/Config/Enabled')
        click('Slots/A0/Right')
        check('顺序按钮移动整条规则',ev('return s.plan[1].id=="ignite" and s.plan[1].condition==1 and s.plan[0].id=="double"'))
        click('Slots/A0/Tune')
        check('固定目标技能锁定目标选项',ev('return s.get_node("Details/Config/Target").disabled and s.get_node("Details/Config/Target").text=="燃烧最多"'))
        click('Reactions/P0');click('Library/Choice1');click('Library/Equip')
        check('反应槽装备回能且显示固定时机',ev('return s.passives[0].id=="mana" and s.get_node("Details/Config/Target").disabled and s.get_node("Reactions/P0/Cost").text.contains("AP 不足")'))
        choose('Details/Config/Condition',2)
        check('反应附加条件可调整',ev('return s.passives[0].condition==2'))
        click('Battle/Unit2/Inspect')
        check('点击怪物建立优先标识',ev('return s.marked==1 and s.units[2].selected and s.units[2].get_node("Mark").visible'))
        hover('Battle/Unit2/Reaction')
        check('敌人被动意图和RP可查',ev('return s.get_node("Details/Title").text=="枯木护身" and s.get_node("Details/Cost").text=="1 RP"'))
        snap('enemy-intent')
        hover('Battle/Unit3/Intent')
        check('敌人主动意图和AP可查',ev('return s.get_node("Details/Title").text=="横扫" and s.get_node("Details/Cost").text.contains("1 AP")'))
        hover('Battle/Unit0/Inspect')
        check('人物悬停统一详情面板',ev('return s.get_node("Details/Title").text=="烬火法师" and s.get_node("Details/Cost").text.contains("RP")'))
        hover('Track/Actor1')
        check('行动轴头像悬停统一详情面板',ev('return s.get_node("Details/Title").text=="灰烬刺球"'))
        click('Controls/Settings');click('Settings/ClickTarget');click('Settings/Close');click('Battle/Unit3/Inspect')
        check('关闭点击选目标后仅查看',ev('return s.marked==1 and not s.click_target and s.get_node("Details/Title").text=="枯枝稻人"'))
        click('Controls/Settings');click('Settings/ClickTarget');click('Settings/Motion');click('Settings/Sound')
        check('闪震和音效设置生效',ev('return s.fx.reduced and not s.get_node("Settings/Sound").button_pressed'))
        click('Settings/Motion');click('Settings/Sound');click('Settings/Close')
        saved=ev('return {"plan":s.plan,"passives":s.passives,"marked":s.marked,"click_target":s.click_target}')
        click('Controls/Save');call('project_manage',op='stop');call('project_run')
        check('保存后停止重开保持四加二规则及目标',ev('return {"plan":s.plan,"passives":s.passives,"marked":s.marked,"click_target":s.click_target}')==saved)
        choose('Controls/Preset',0)
        click('Reactions/P0');click('Library/Choice0');click('Library/Equip')
        check('重复反应交换装备槽而不浪费栏位',ev('return s.passives[0].id=="shield" and s.passives[1].id=="charge"'))
        click('Slots/A3');click('Library/Remove')
        check('装备槽可卸下并保留四槽结构',ev('return s.plan[3].id=="" and s.plan.size()==4 and s.get_node("Slots/A3/Name").text=="+ 装备"'))
        choose('Controls/Preset',2)
        check('超过AP预算明确提示',ev('return s.get_node("ActiveTitle").text.contains("6 / 4 AP") and s.get_node("ActiveTitle").modulate.g<0.8'))
        choose('Controls/Preset',0);click('Controls/Settings');click('Settings/ClearTarget');click('Settings/Close');click('Controls/Save')
        check('清除优先目标',ev('return s.marked==-1 and not s.units[2].selected'))
        snap('ready')
    elif args.phase=='preview':
        choose('Controls/Preset',0)
        before=ev('return {"plan":s.plan,"passives":s.passives,"marked":s.marked,"state":s.shown_state}')
        click('Slots/A3');click('Library/Choice5');click('Details/Preview')
        check('预览锁定装备与开战',ev('return s.previewing and s.get_node("Library/Equip").disabled and s.get_node("Controls/Start").disabled'))
        deadline=time.monotonic()+12;captured=False;transferred=False
        while time.monotonic()<deadline:
            value=st()
            transferred=transferred or value['transfer_played']
            if not captured and transferred:
                snap('burst-preview');captured=True
            if not value['previewing']:break
            time.sleep(.12)
        check('预览结束完整恢复战前状态',ev('return {"plan":s.plan,"passives":s.passives,"marked":s.marked,"state":s.shown_state}')==before)
        check('炎爆击杀实际播放五层转移',transferred)
        check('预览后可继续装备',ev('return not s.get_node("Library/Equip").disabled and not s.get_node("Details/Preview").disabled'))
        click('Details/Preview');click('Controls/Reset');click('Slots/A0');click('Library/Choice0');click('Library/Equip')
        check('中断预览后仍可装备',ev('return s.plan[0].id=="ignite" and not s.previewing'))
        choose('Controls/Preset',0)
        click('Reactions/P1');click('Library/Choice0');click('Details/Preview')
        deadline=time.monotonic()+10
        while time.monotonic()<deadline and st()['previewing']:time.sleep(.2)
        check('炎盾预览播放真实受击且结束',ev('return not s.previewing and s.events.any(func(e): return e.kind=="hurt" and e.amount==6)'))
        click('Library/Close');click('Controls/Reset')
    elif args.phase=='combat':
        choose('Controls/Preset',0);choose('Controls/Speed',0)
        check('重选当前预设恢复默认构筑',ev('return s.plan[0].id=="wall" and s.plan[1].id=="double" and s.passives[0].id=="charge"'))
        click('Controls/Start');click('Controls/Pause')
        before=st();time.sleep(.25);after=st()
        check('暂停冻结事件游标',before['paused'] and before['cursor']==after['cursor'])
        click('Controls/Step')
        check('原生单步只推进一次',st()['cursor']==before['cursor']+1)
        check('战斗中装备和选目标锁定',ev('return s.get_node("Slots/A0").disabled and s.get_node("Reactions/P0/Tune").disabled and s.get_node("Settings/ClickTarget").disabled'))
        # Advance using real Step button to observe each animation/axis/feedback event.
        seen=set();frames={};axis=False;reset=False;transfer=False;burn=False;allspent=False;next_round=False
        for index in range(170):
            value=st()
            if value['result']:break
            if value['kind']=='turn':
                time.sleep(.65)
                axis=axis or bool(ev('var i=s.shown_state.actor\nreturn s.shown_state.timeline[i]==1 and s.get_node("Track/Actor%d"%i).scale.x>1.2'))
            if value['kind']=='turn_end':reset=reset or bool(ev('var i=s.events[s.cursor].actor\nreturn s.shown_state.timeline[i]==0 and not s.get_node("Track/Actor%d"%i).visible and s.shown_state.done[i]'))
            if value['kind']=='end_round':
                allspent=bool(ev('return s.shown_state.ap==0 and s.shown_state.enemies.all(func(e):return e.ap==0) and s.get_node("Track").get_children().filter(func(n):return n is Button).all(func(n):return not n.visible) and s.get_node("Battle/Banner").text.contains("回合结束")'))
                snap('round-end')
            if value['kind']=='round' and ev('return s.shown_state.round')==2:
                next_round=bool(ev('return s.shown_state.ap==4 and s.shown_state.rp==3 and s.get_node("Track/Actor0").visible and s.get_node("Battle/Banner").text.contains("AP / RP 已恢复")'))
                snap('next-round')
            if value['kind'] in ['cast','enemy']:
                actor=int(value['actor']);time.sleep(.15)
                frame=ev('var a=s.units[%d].get_node("Art")\nvar result={"animation":a.animation,"frame":a.frame,"count":a.sprite_frames.get_frame_count("attack")}\na.pause()\nreturn result'%actor)
                if actor not in seen:
                    frames[actor]=frame;seen.add(actor);snap('attack-'+str(actor))
                ev('s.units[%d].get_node("Art").play()\nreturn true'%actor)
            if value['kind']=='transfer':transfer=True;snap('transfer')
            if value['kind']=='burn' and not burn:
                actor=ev('return s.events[s.cursor].target+1')
                hover('Battle/Unit%d/Burn'%actor)
                burn=bool(ev('return s.get_node("Details/Title").text=="燃烧" and s.get_node("Details/Text").text.contains("回合末")'))
                snap('burn-detail')
            if len(seen)==4 and axis and reset and allspent and next_round:break
            click('Controls/Step')
        check('四个单位真实播放非首帧攻击',len(seen)==4 and all(f['animation']=='attack' and f['frame']>0 and f['count']==5 for f in frames.values()),frames)
        check('轴到右端放大且行动结束退出',axis and reset)
        check('全员AP耗尽退出后提示本轮结束',allspent)
        check('下一轮恢复资源并明确提示重新入轴',next_round)
        check('燃烧标牌悬停显示详情',burn)
        history=ev('return s.fx.history')
        check('技能和buff名称飘到对应单位',any(e['actor']==0 and e['text']=='蓄能' for e in history) and any(e['actor']==2 and e['text']=='枯木护身' for e in history) and any(e['actor']==3 and e['text']=='横扫' for e in history),history)
        if not st()['result']:
            choose('Controls/Speed',2);click('Controls/Pause')
        result=wait_done()
        check('默认战术完整胜利',result['victory'] and result['state']['hp']==68,result)
        snap('victory')
        click('Controls/Reset')
        # Empty build is a deliberate fixture to exercise the actual defeat playback.
        ev('for row in s.plan: row.enabled=false\nfor row in s.passives: row.enabled=false\ns.refresh_slots()\nreturn true')
        choose('Controls/Speed',2);click('Controls/Start');result=wait_done()
        check('空构筑实际播放战败',not result['victory'] and result['state']['hp']==0,result)
        check('战斗复盘比较上一场结果',ev('return s.get_node("Details/Text").text.contains("较上一场：生命 -68")'))
        snap('defeat');click('Controls/Reset');choose('Controls/Preset',0);choose('Controls/Speed',0)
    else:
        choose('Controls/Preset',0);choose('Controls/Speed',0);click('Controls/Save')
        call('project_manage',op='stop');call('scene_open',path='res://scenes/tactical_main.tscn',force_reload=True);call('scene_save');call('project_run')
        check('最终原生保存重开主场景',ev('return s.scene_file_path=="res://scenes/tactical_main.tscn" and s.plan.size()==4 and s.passives.size()==2 and not s.running'))
        check('无旧状态条与详情弹窗',ev('return not s.has_node("Status") and s.find_children("*","AcceptDialog",true,false).is_empty() and s.get_node("Details").position==Vector2(1050,503)'))
        check('四单位脚底统一地面',ev('return s.units.all(func(u): return u.get_node("Art").position.y==245)'))
        check('指定行动位置立即映射到显示',ev('var state=s.shown_state.duplicate(true)\nstate.timeline[2]=0.35\ns.render_state(state)\nreturn is_equal_approx(s.get_node("Track/Actor2").position.x,555.0)'))
        ev('var state=s.shown_state.duplicate(true)\nstate.enemies[0].burn=2\ns.render_state(state)\nreturn true')
        hover('Battle/Unit1/Burn')
        check('悬停详情随燃烧状态变化',ev('var state=s.shown_state.duplicate(true)\nstate.enemies[0].burn=4\ns.render_state(state)\nreturn s.get_node("Details/Cost").text=="4 层" and s.get_node("Details/Text").text.contains("32")'))
        click('Controls/Reset')
        snap('final-ready')
        logs=call('logs_read',source='game',count=100,include_details=True)
        check('最终进程无脚本错误',not any(e.get('level') in ['error','script_error'] for e in logs.get('lines',[])),logs)
finally:
    flush();print(json.dumps({'phase':args.phase,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks)},ensure_ascii=False),flush=True)
