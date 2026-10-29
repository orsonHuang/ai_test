"""Collect final verification counts, source hashes and local document link checks."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
docs=root.parent/'docs'; evidence=docs/'verification'
checks={}
for name in ['rules','ui','preview','combat','final']:
    data=json.loads((evidence/f'v2-{name}.json').read_text(encoding='utf-8-sig'))
    entries=data['checks']
    checks[name]={'passed':sum(bool(e['passed']) for e in entries),'failed':sum(not e['passed'] for e in entries)}
    assert checks[name]['failed']==0,(name,checks[name])
missing=[]
for path in [root.parent/'README.md',docs/'GDD-v2.md',docs/'v2-改版与验收.md',docs/'素材与依赖.md']:
    for dest in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if not dest.startswith(('https:','http:','#')) and not (path.parent/dest).exists():
            missing.append([str(path),dest])
assert not missing,missing
files=[root/'project.godot']
files+=list((root/'scripts').glob('tactical*.gd'))
files+=[root/'scripts'/n for n in ['combat_rules.gd','action_track.gd','tactics_store.gd']]
files+=list((root/'scenes').glob('tactical*.tscn'))
files+=list((root/'resources').glob('*_frames.tres'))
files+=[root/'resources'/n for n in ['balance_v2.tres','tactical_theme.tres']]
files+=list((root/'assets/v2').glob('*-grid.png'))
files+=[root/'assets/v2'/n for n in ['ground.png','icons.png','animation_metrics.json']]
result={'checks':checks,'native_passed':sum(checks[n]['passed'] for n in ['ui','preview','combat','final']),
        'missing_document_links':missing,'source_sha256':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(evidence/'v2-delivery-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},ensure_ascii=False))
