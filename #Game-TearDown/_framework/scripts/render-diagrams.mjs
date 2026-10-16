import fs from 'node:fs';
import path from 'node:path';

// Render authored mechanism diagrams, never recreate or alter game screenshots.
const input = process.argv[2];
if (!input) throw new Error('Usage: node render-diagrams.mjs <diagrams.json>');
const config = JSON.parse(fs.readFileSync(input, 'utf8'));
const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
for (const diagram of config) {
  if (!Array.isArray(diagram.nodes) || diagram.nodes.length < 2 || diagram.nodes.length > 4) throw new Error('A diagram needs 2–4 nodes');
  const count = diagram.nodes.length, width = 1200, box = (1080 - (count - 1) * 32) / count;
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620" role="img" aria-labelledby="title desc"><title id="title">${escape(diagram.title)}</title><desc id="desc">${escape(diagram.caption)}</desc><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#77d6c2" stroke-width="1.5"/></marker></defs><rect width="1200" height="620" rx="24" fill="#13212c"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif"><text x="60" y="62" fill="#77d6c2" font-size="17">GAME TEARDOWN · 原创机制示意</text><text x="60" y="115" fill="#f3f3ec" font-size="32" font-weight="700">${escape(diagram.title)}</text><text x="60" y="155" fill="#b2c2cb" font-size="19">${escape(diagram.subtitle)}</text>`;
  diagram.nodes.forEach((node, i) => {
    const x = 60 + i * (box + 32);
    svg += `<rect x="${x}" y="208" width="${box}" height="204" rx="14" fill="#203542" stroke="#3c5966"/><text x="${x+22}" y="245" fill="#77d6c2" font-size="15">${String(i+1).padStart(2,'0')}</text><text x="${x+22}" y="284" fill="#ffffff" font-size="23" font-weight="700">${escape(node.title)}</text>`;
    node.lines.forEach((line,j)=> {svg += `<text x="${x+22}" y="${325+j*29}" fill="#c5d1d7" font-size="18">${escape(line)}</text>`;});
    if (i<count-1 && diagram.flow !== false) svg += `<path d="M${x+box+4},306 H${x+box+27}" stroke="#77d6c2" stroke-width="2" marker-end="url(#arrow)"/>`;
  });
  svg += `<rect x="60" y="446" width="1080" height="80" rx="12" fill="#27363d"/><text x="82" y="479" fill="#f1d28c" font-size="18">设计问题</text><text x="82" y="509" fill="#e1e5e4" font-size="19">${escape(diagram.question)}</text><text x="60" y="567" fill="#91a6b2" font-size="16">${escape(diagram.caption)}</text><text x="60" y="593" fill="#91a6b2" font-size="14">图示用于解释机制关系，不代表原作 UI 或内部实现。</text></g></svg>`;
  const destination = path.resolve(path.dirname(input), diagram.file);
  if (path.dirname(destination) !== path.resolve(path.dirname(input))) throw new Error('Diagram output must stay beside its config');
  fs.writeFileSync(destination, svg + '\n');
}
console.log(`Rendered ${config.length} diagrams.`);
