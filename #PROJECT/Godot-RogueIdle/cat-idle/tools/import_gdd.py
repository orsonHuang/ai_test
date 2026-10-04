"""Import the project's GDD CSVs as Inspector-editable resources through MCP."""
from __future__ import annotations

import csv
import json
import argparse
import re
from pathlib import Path
from mcp_bridge import GodotMCP, EVIDENCE, PROJECT

SOURCE = PROJECT.parent / "GDD" / "data"
GEOMETRY = {
    "castle": ([[190,45],[295,20],[410,45],[480,150],[300,165],[100,150]],[295,92],"#493b56","黯冠魔王"),
    "frost": ([[100,150],[300,165],[290,310],[220,310],[60,285],[55,225]],[172,223],"#34546a","白狼领主"),
    "ash": ([[300,165],[480,150],[550,215],[540,280],[385,300],[290,310]],[416,222],"#664641","余烬执政官"),
    "quarry": ([[60,285],[220,310],[210,420],[120,425],[72,375]],[136,350],"#4d574b","苔岩巨像"),
    "river": ([[220,310],[290,310],[385,300],[380,425],[300,445],[210,420]],[300,361],"#315762","逐月之影"),
    "ember": ([[385,300],[540,280],[535,375],[470,420],[380,425]],[465,348],"#724c3d","熔火祭司"),
    "briar": ([[120,425],[210,420],[300,445],[290,550],[215,550],[160,510]],[210,475],"#3c6553","古树守卫"),
    "ruins": ([[300,445],[380,425],[470,420],[440,510],[385,550],[290,550]],[378,476],"#4b5369","失落猎手"),
    "village": ([[215,550],[290,550],[385,550],[365,610],[250,610]],[300,575],"#786448","远征起点"),
}


def convert(text):
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def read(name):
    with (SOURCE / (name + ".csv")).open(encoding="utf-8-sig", newline="") as stream:
        return [{k: convert(v) for k, v in row.items()} for row in csv.DictReader(stream)]


def literal(value):
    return json.dumps(value, ensure_ascii=False)


def script_resource(script, properties):
    return ('[gd_resource type="Resource" format=3]\n\n'
            f'[ext_resource type="Script" path="res://scripts/expedition/data/{script}.gd" id="1"]\n\n'
            '[resource]\nscript = ExtResource("1")\n' + '\n'.join(f'{k} = {v}' for k,v in properties.items()) + '\n')


def resources():
    files = {}
    groups = {}
    for table in ["regions", "units", "activities", "equipment", "affixes", "sets", "skills", "events"]:
        groups[table] = []
        for row in read(table):
            if table == "events" and row["phase"] != "M1":
                continue
            key = str(row.get("id", row.get("slot", "")))
            if table == "sets":
                key = f'{row["set_id"]}_{row["piece_count"]}'
            path = f'res://resources/expedition/{table}/{key}.tres'
            groups[table].append(path)
            if table == "units":
                props = {("display_name" if k == "name" else k): literal(v) for k,v in row.items()}
                files[path] = script_resource("FogUnit", props)
            elif table == "regions":
                props = {("display_name" if k == "name" else k): literal(v) for k,v in row.items()}
                props["initial_landmark"] = "true" if row["initial_landmark"] else "false"
                for k in ["next_ids", "adjacent_ids"]:
                    props[k] = "PackedStringArray(" + ", ".join(literal(x) for x in str(row[k]).split('|') if x) + ")"
                polygon, label, color, boss = GEOMETRY[key]
                props["polygon"] = "PackedVector2Array(" + ", ".join(str(v) for point in polygon for v in point) + ")"
                props["label_position"] = f'Vector2({label[0]}, {label[1]})'
                props["tint"] = "Color(" + ", ".join(str(int(color[i:i+2],16)/255.0) for i in (1,3,5)) + ", 1)"
                props["boss_name"] = literal(boss)
                files[path] = script_resource("FogRegion", props)
            else:
                props = {"id": literal(key), "display_name": literal(row.get("name",key)),
                         "category": literal(table), "values": literal(row)}
                files[path] = script_resource("FogEntry", props)
    header = ['[gd_resource type="Resource" format=3]', '',
              '[ext_resource type="Script" path="res://scripts/expedition/data/FogCatalog.gd" id="1"]']
    arrays = {}
    index = 2
    for name, paths in groups.items():
        refs = []
        for path in paths:
            header.append(f'[ext_resource type="Resource" path="{path}" id="{index}"]')
            refs.append(f'ExtResource("{index}")')
            index += 1
        arrays[name] = 'Array[Resource]([' + ', '.join(refs) + '])'
    header += ['', '[resource]', 'script = ExtResource("1")',
               'rules_version = "gdd-v1-demo-1"',
               'rules = ' + literal({r['id']:r['value'] for r in read('rules')})]
    header += [f'{key} = {value}' for key,value in arrays.items()]
    files['res://resources/expedition/catalog.tres'] = '\n'.join(header) + '\n'
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overwrite-configs', action='store_true', help='Replace gameplay values from CSV; preserve existing map geometry and boss names')
    args = parser.parse_args()
    generated = resources()
    existing = [path for path in generated if (PROJECT / path.removeprefix('res://')).exists()]
    if existing and not args.overwrite_configs:
        raise SystemExit('Resources already exist. Edit them in Godot, or review CSV changes and explicitly use --overwrite-configs. Geometry is preserved when reimporting.')
    for path in existing:
        if '/regions/' not in path:
            continue
        previous = (PROJECT / path.removeprefix('res://')).read_text(encoding='utf-8')
        for key in ['polygon', 'label_position', 'tint', 'boss_name']:
            value = re.search(r'^' + key + r' = .+$', previous, re.MULTILINE)
            if value is None:
                raise SystemExit('Cannot preserve edited map property: ' + path + ':' + key)
            generated[path] = re.sub(r'^' + key + r' = .+$', lambda _: value.group(0), generated[path], flags=re.MULTILINE)
    client = GodotMCP()
    client.call('session_activate', {'session_id':'cat-idle'})
    scan = client.call('filesystem_manage', {'op':'scan'})
    print('Class registration:',json.dumps(scan.get('structuredContent',scan),ensure_ascii=False),flush=True)
    outcomes = []
    for path, content in generated.items():
        result = client.call('filesystem_manage', {'op':'write_text','params':{'path':path,'content':content}})
        if result.get('isError'):
            raise RuntimeError(result)
        outcomes.append({'path':path,'result':result})
    (EVIDENCE/'resource-import.json').write_text(json.dumps(outcomes,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Imported',len(outcomes),'editable .tres resources through Godot MCP',flush=True)
    for tool,args in [('filesystem_manage',{'op':'scan'}),('resource_manage',{'op':'load','params':{'path':'res://resources/expedition/catalog.tres'}})]:
        result=client.call(tool,args)
        print(tool,json.dumps(result.get('structuredContent',result),ensure_ascii=False),flush=True)
        if result.get('isError'):raise RuntimeError(result)


if __name__ == '__main__':
    main()
