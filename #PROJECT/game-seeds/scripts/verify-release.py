from pathlib import Path
import hashlib, json, urllib.request, concurrent.futures
root=Path(__file__).resolve().parents[1]
release=json.loads((root/'validation/release.json').read_text(encoding='utf-8'))
base='https://orson.games/game-ideas/'
def check(item):
    file,expected=item
    with urllib.request.urlopen(base+file,timeout=30) as response:
        data=response.read()
        assert response.status==200
        actual=hashlib.sha256(data).hexdigest()
        assert actual==expected,(file,actual,expected)
        return {'file':file,'sha256':actual,'status':200}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(check,release['files'].items()))
routes={}
for url in ['https://orson.games/game-ideas','https://orson.games/','https://orson.games/awakening']:
    with urllib.request.urlopen(url,timeout=30) as response:routes[url]={'status':response.status,'finalUrl':response.url}
assert routes['https://orson.games/game-ideas']['finalUrl']==base
(root/'validation/online-integrity.json').write_text(json.dumps({'release':release['release'],'passed':True,'files':results,'routes':routes},indent=2),encoding='utf-8')
print(f'HTTPS verified: {len(results)} matching files, trailing slash redirect, homepage and awakening reachable')
