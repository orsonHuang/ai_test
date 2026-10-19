from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image
from io import BytesIO

root=Path(__file__).resolve().parents[3]/'#Game-TearDown'/'永远的蔚蓝星球-App'
items={
'king-overview':'FlbmbQWSReZb0Gls9YMLBQYSC4P3.jpg',
'king-talents':'FhZ2_avtKoiIdCaDHHA3Z3E-4FEU.png',
'cloak-panel':'FkTuK3_Aq_xls7CRTxzH76GDaR72.png',
'arena-board':'FgQNT49C2mu6CZF1gWS54iQiB9Be.jpg',
'rat-mine':'FrNQP2fXlsQm-20oHhyv0wKV7vPx.jpg',
}
for name,key in items.items():
    target=root/'assets'/(name+'.png')
    if not target.exists():
        req=Request('https://img2-tc.tapimg.com/moment/etag/'+key+'/_tap_ugc.jpg',headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.taptap.cn/'})
        with urlopen(req,timeout=40) as res: data=res.read()
        Image.open(BytesIO(data)).convert('RGB').save(target)
    im=Image.open(target)
    print(name, im.size)
