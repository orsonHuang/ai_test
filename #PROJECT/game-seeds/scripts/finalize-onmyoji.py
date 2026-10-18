from pathlib import Path
import json,re
P=Path(__file__).resolve().parents[1];G=P.parents[1]/'#Game-TearDown'/'阴阳师-国服App'
def edit(p,fn):
 s=p.read_text(encoding='utf-8-sig');p.write_text(fn(s),encoding='utf-8')
# Put conclusion and related links after the detailed rules, not before them.
endings=('## 适用与限制','## 评价与资源结构','## 我的评价','## 养成与公平感','## 数值与取舍','## 评价与边界')
for p in (G/'reader').glob('*.md'):
 if p.stem in ('式神与阴阳师养成','游戏分析'):continue
 def order(s):
  parts=re.split(r'(?m)(?=^## )',s)
  return ''.join([x for x in parts if not x.startswith(endings)]+[x for x in parts if x.startswith(endings)])
 edit(p,order)
edit(G/'reader'/'游戏分析.md',lambda s:s.replace('## 09 我的评价与下一步验证','## 11 我的评价与下一步验证').replace('## 10 全系统关系：资源最终回到哪一种能力','## 09 全系统关系：资源最终回到哪一种能力').replace('## 11 拆解覆盖与验收入口','## 10 拆解覆盖与验收入口'))
def overvieworder(s):
 parts=re.split(r'(?m)(?=^## )',s);return ''.join([x for x in parts if not x.startswith('## 11 ')]+[x for x in parts if x.startswith('## 11 ')])
edit(G/'reader'/'游戏分析.md',overvieworder)
edit(G/'systems'/'行动条与鬼火战斗.md',lambda s:s.replace('每人都有普攻','每人都有普攻；未特别注明的技能冷却为0、无额外状态'))
edit(G/'sources.json',lambda s:s.replace('位置、等级、属性章节已读','检索返回的位置、等级、属性正文摘录已读；直接打开受限'))
edit(P/'dist'/'library.js',lambda s:s.replace('展开查看有限范围的可开发参考规格，尚未实现或进行玩法测试。','展开查看本模块的参考规则、参数与验收要求；完整服务尚未实现。'))
edit(P/'tests'/'library.cjs',lambda s:s.replace('page.goto(base);','page.goto(base+\'#library\');').replace('p2.goto(base);','p2.goto(base+\'#library\');').replace('count(),31','count(),32').replace('count(),37','count(),38').replace('docs.length,56','docs.length,57').replace('31 default / 37 total','32 default / 38 total'))
edit(P/'tests'/'visual-reader.cjs',lambda s:s.replace("'.system-map a').count(),10","'.system-map a').count(),11"))
edit(P/'tests'/'reader-navigation.cjs',lambda s:s.replace("location.hash||'#library'","location.hash||'#games'").replace("await ready(page);assert.equal(new URL(page.url()).hash,'#library');\n  assert.equal(await page.locator('#library-list').isVisible(),true)","await ready(page);assert.equal(new URL(page.url()).hash,'#games');\n  assert.equal(await page.locator('#game-library').isVisible(),true)").replace("await ready(page);await page.selectOption('#game-filter'","await ready(page);await page.locator('[data-nav=library]').click();await ready(page);await page.selectOption('#game-filter'"))
edit(P/'tests'/'game-discovery.cjs',lambda s:s.replace("assert((await page.locator('#reading-position').innerText()).includes(await heading.innerText()));","assert.equal(await page.locator('#reading-position').count(),0);").replace("  assert(await page.locator('#reading-position').isVisible());\n",'').replace("document.querySelector('#reading-position').textContent.includes('我的用途与笔记')","document.querySelector('#case-toc [aria-current]')?.textContent.includes('我的用途与笔记')").replace("assert.equal(await page.locator('.system-card').count(),31);","assert.equal(new URL(page.url()).hash,'#games');assert(await page.locator('#game-library').isVisible());await go('#library');assert.equal(await page.locator('.system-card').count(),32);").replace('collapsed mobile reading hint','highlight only without reading declaration'))
# Keep authoring passes explicitly one-shot to avoid duplicating published sections.
for file,guard in [('expand-onmyoji.py',"if '## 11 我的评价与下一步验证' in (G/'reader'/'游戏分析.md').read_text(encoding='utf-8-sig'): raise SystemExit('Expansion already applied; edit source documents directly.')"),('specify-onmyoji.py',"if any(x['id']=='onmyoji-contract' for x in json.loads((G/'game.json').read_text(encoding='utf-8-sig'))['systems']): raise SystemExit('Specification pass already applied; edit source documents directly.')")]:
 edit(P/'scripts'/file,lambda s,guard=guard:s.replace('def write(p,s):',guard+'\n'+'def write(p,s):',1))

# Role entrypoints cover the complete group instead of three sample links.
g=json.loads((G/'game.json').read_text(encoding='utf-8-sig'))
for name,intro in [('策划阅读','先读整游的循环、节奏、系统关系和数值层，再沿目标问题进入各模块。'),('开发阅读','各系统的开发参考附录列出自设默认值、状态、交易边界与验收要求；原作事实与补充规则分开。除已标注演示与计算器外，完整服务未实现。'),('美术阅读','先看整游美术分析、原图和局部图，再看系统UI信息结构与叙事外观的资产交付清单。线框和机制图均为分析示意。')]:
 text=f'# 阴阳师 · {name}\n\n{intro}\n\n[整游分析与系统地图](../README.md)\n\n'+'\n\n'.join(f'- [{s["title"]}](../{s["path"]})' for s in g['systems'])+'\n'
 (G/'roles'/f'{name}.md').write_text(text,encoding='utf-8')
print('Polished reading order, metadata, navigation and tests.')
