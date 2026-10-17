"""Package public dist only, with a SHA-256 manifest for server/HTTPS checks."""
from pathlib import Path
import hashlib, json, tarfile, zipfile, datetime, re
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
release='game-ideas-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
# Change resource URLs whenever their contents change, including data-only updates.
entry=dist/'index.html'
html=entry.read_text(encoding='utf-8')
def version_asset(match):
    attr,name=match.groups()
    digest=hashlib.sha256((dist/name).read_bytes()).hexdigest()[:16]
    return f'{attr}="./{name}?v={digest}"'
html,count=re.subn(r'(src|href)="\./([\w-]+\.(?:js|css))(?:\?[^"\s]*)?"',version_asset,html)
assert count==7, f'Expected 7 entry scripts/styles, found {count}'
if html!=entry.read_text(encoding='utf-8'):
    entry.write_text(html,encoding='utf-8')
files=sorted(p for p in dist.rglob('*') if p.is_file())
assert all(p.suffix in {'.html','.js','.css','.svg','.png'} or (p.parent==dist/'reference' and p.name in {'growth-config.json','growth-levels.csv','growth-calculator.mjs'}) for p in files)
allowed=json.loads((root/'../../#Game-TearDown/public-media.json').resolve().read_text(encoding='utf-8'))['media']
assert len(list((dist/'media').glob('*')))==len(allowed)
manifest={p.relative_to(dist).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
out=root/'validation';out.mkdir(exist_ok=True)
(out/'release.json').write_text(json.dumps({'release':release,'files':manifest},indent=2),encoding='utf-8')
(out/'SHA256SUMS').write_text(''.join(f'{h}  {p}\n' for p,h in manifest.items()),encoding='utf-8')
with tarfile.open(out/(release+'.tar.gz'),'w:gz') as tf:
    for p in files: tf.add(p,arcname=p.relative_to(dist).as_posix())
with zipfile.ZipFile(root/'game-seeds-v0.2-static.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(dist).as_posix())
print(json.dumps({'release':release,'files':len(files),'bytes':sum(p.stat().st_size for p in files)}))
