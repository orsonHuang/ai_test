"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.nextHint = exports.publicPlacementHint = exports.check = exports.solve = exports.deduce = exports.validateLevel = exports.residentCountRegion = exports.isResidentCount = exports.residentDirectionRegion = exports.residentNeighborRegion = exports.matches = exports.clueText = exports.formatClueText = exports.floorCountState = exports.floorCountText = exports.generalSatisfied = exports.generalRegion = exports.generalRuleText = exports.clueHighlight = exports.related = exports.primaryClueIssues = exports.clueOwner = exports.roomName = exports.resumeLevelIndex = exports.normalizeLevel = exports.allRules = exports.floorRules = exports.storyClues = exports.levelCaption = exports.clueConcept = exports.NEW_CONCEPTS = exports.roomHas = exports.isGeneral = void 0;
/** Engine-independent rules. Floors are 1-based; columns are 0-based. */
const Themes_1 = require("./Themes");
const isGeneral = (c) => ['roomEmpty', 'adjacentCount', 'cornerOccupancy', 'facilityNeighborCount', 'facilityOccupancy'].includes(c.type);
exports.isGeneral = isGeneral;
/** "any" is a clue selector, never an actual room facility. */
const roomHas = (r, f) => !r.locked && (f === 'any' ? r.features.length > 0 : r.features.includes(f));
exports.roomHas = roomHas;
exports.NEW_CONCEPTS = ['adjacent', 'differentFloor', 'lower', 'between', 'residentNeighborCount', 'featureChoice:any', 'featureChoice:exactlyOne', 'residentDirectionCount'];
const clueConcept = (c) => c.type === 'featureChoice' ? `${c.type}:${c.mode}` : c.type;
exports.clueConcept = clueConcept;
const levelCaption = (level, fallback = 1) => `第 ${level.sequence ?? fallback} 夜`;
exports.levelCaption = levelCaption;
const storyClues = (level) => level.clues.filter(c => c.type !== 'quota');
exports.storyClues = storyClues;
function floorRules(level) {
    return level.floorQuotas === undefined ? level.clues.filter(c => c.type === 'quota') : Object.entries(level.floorQuotas).map(([f, count]) => ({ id: `floor-${f}`, type: 'quota', floor: Number(f), count }));
}
exports.floorRules = floorRules;
const allRules = (level) => [...(0, exports.storyClues)(level), ...floorRules(level)];
exports.allRules = allRules;
/** Import legacy drafts explicitly; live validation never silently ignores conflicting quota sources. */
function normalizeLevel(level) {
    return { ...level, rooms: level.rooms.map(r => r.locked ? { ...r, features: [] } : r), themeId: level.themeId ?? 'moonlight', title: '', floorQuotas: level.floorQuotas ?? Object.fromEntries(floorRules(level).map(c => [String(c.floor), c.count])), clues: (0, exports.storyClues)(level) };
}
exports.normalizeLevel = normalizeLevel;
function resumeLevelIndex(levels, saved) {
    const stableId = saved.currentId || (Number.isInteger(saved.current) ? `night-${saved.current + 1}` : '');
    const idIndex = levels.findIndex(l => l.id === stableId);
    return idIndex >= 0 ? idIndex : Number.isInteger(saved.current) && saved.current >= 0 && saved.current < levels.length ? saved.current : 0;
}
exports.resumeLevelIndex = resumeLevelIndex;
const roomName = (r) => `${r.floor}${String.fromCharCode(65 + r.col)}`;
exports.roomName = roomName;
const clueOwner = (c) => c.role === 'supplement' || (0, exports.isGeneral)(c) || c.type === 'quota' ? '' : c.owner ?? c.a ?? '';
exports.clueOwner = clueOwner;
/** Authoring contract, separate from satisfiability so audits can remove rules to test necessity. */
function primaryClueIssues(l) {
    const clues = (0, exports.storyClues)(l), issues = [];
    for (const [i, a] of Array.from(l.animals.entries())) {
        if (clues.filter(c => (0, exports.clueOwner)(c) === a.id).length !== 1)
            issues.push(`${a.name}必须且只能有1条主线索`);
        if (!clues[i] || (0, exports.clueOwner)(clues[i]) !== a.id)
            issues.push(`第${i + 1}条必须是第${i + 1}位住客${a.name}的主线索`);
    }
    if (clues.slice(l.animals.length).some(c => (0, exports.clueOwner)(c)))
        issues.push('补充线索必须排在全部住客主线索之后，且无来源住客');
    return issues;
}
exports.primaryClueIssues = primaryClueIssues;
const related = (c, id) => !(0, exports.isGeneral)(c) && (c.a === id || c.b === id || c.c === id || c.type === 'quota');
exports.related = related;
const clueHighlight = (c, id) => !id ? 'none' : (0, exports.clueOwner)(c) === id ? 'primary' : (0, exports.related)(c, id) ? 'related' : 'none';
exports.clueHighlight = clueHighlight;
function generalRuleText(level, c) {
    const facility = (0, Themes_1.facilityName)(level, c.feature);
    switch (c.type) {
        case 'roomEmpty': return `${c.has ? '有' : '没有'}${facility}的房间没有住户`;
        case 'adjacentCount': return `全屋恰好${c.count}对住户${c.axis === 'horizontal' ? '左右' : '上下'}紧邻`;
        case 'cornerOccupancy': return c.has ? '至少1位住户住在房屋角落' : '房屋角落没有住户';
        case 'facilityOccupancy': return `恰好有${c.count}位住户的房间有${facility}`;
        case 'facilityNeighborCount': return `所有${facility}房${{ around: '上下左右', above: '正上方', below: '正下方', left: '左侧', right: '右侧' }[c.direction]}邻房共${c.count}位住户（去重）`;
        default: throw new Error('未知通用规则');
    }
}
exports.generalRuleText = generalRuleText;
/** Neighbor areas are a union of grid cells, not a sum of counts per anchor. */
function generalRegion(l, c) {
    const open = l.rooms.filter(r => !r.locked);
    if (c.type === 'cornerOccupancy')
        return open.filter(r => (r.floor === 1 || r.floor === l.floors) && (r.col === 0 || r.col === l.cols - 1));
    if (c.type === 'roomEmpty')
        return open.filter(r => (0, exports.roomHas)(r, c.feature) === c.has);
    const anchors = open.filter(r => (0, exports.roomHas)(r, c.feature));
    if (c.type === 'facilityOccupancy')
        return anchors;
    if (c.type === 'facilityNeighborCount')
        return open.filter(r => anchors.some(a => {
            const dx = r.col - a.col, dy = r.floor - a.floor;
            return c.direction === 'around' ? Math.abs(dx) + Math.abs(dy) === 1 : c.direction === 'above' ? dx === 0 && dy === 1 : c.direction === 'below' ? dx === 0 && dy === -1 : c.direction === 'left' ? dx === -1 && dy === 0 : dx === 1 && dy === 0;
        }));
    return [];
}
exports.generalRegion = generalRegion;
function generalSatisfied(l, c, occupied) {
    if (c.type === 'adjacentCount') {
        const rooms = l.rooms.filter(r => !r.locked && occupied.has(r.id));
        let pairs = 0;
        for (let i = 0; i < rooms.length; i++)
            for (let j = i + 1; j < rooms.length; j++) {
                const a = rooms[i], b = rooms[j];
                if (c.axis === 'horizontal' ? a.floor === b.floor && Math.abs(a.col - b.col) === 1 : a.col === b.col && Math.abs(a.floor - b.floor) === 1)
                    pairs++;
            }
        return pairs === c.count;
    }
    const n = generalRegion(l, c).filter(r => occupied.has(r.id)).length;
    return c.type === 'cornerOccupancy' ? (n > 0) === c.has : n === (c.type === 'roomEmpty' ? 0 : c.count);
}
exports.generalSatisfied = generalSatisfied;
/** Single global-constraint support plus all-different; never assumes a full puzzle answer. */
function generalSupport(l, c, d, deadline) {
    const open = l.rooms.filter(r => !r.locked), ids = l.animals.map(a => a.id), n = ids.length;
    const choices = ids.map(id => d[id].map(r => open.findIndex(x => x.id === r)).filter(i => i >= 0));
    const support = ids.map(() => new Set());
    const canMatch = (mask, fixedA = -1, fixedR = -1) => {
        const owners = new Array(open.length).fill(-1);
        if (fixedA >= 0)
            owners[fixedR] = fixedA;
        const augment = (a, seen) => {
            for (const r of choices[a]) {
                if (!(mask & (1 << r)) || seen.has(r) || r === fixedR)
                    continue;
                seen.add(r);
                if (owners[r] === -1 || augment(owners[r], seen)) {
                    owners[r] = a;
                    return true;
                }
            }
            return false;
        };
        for (let a = 0; a < n; a++)
            if (a !== fixedA && !augment(a, new Set()))
                return false;
        return true;
    };
    for (let mask = 0; mask < (1 << open.length); mask++) {
        if (Date.now() >= deadline)
            throw new Error('RULE_BUDGET_EXCEEDED');
        let bits = mask, count = 0;
        while (bits) {
            bits &= bits - 1;
            count++;
        }
        if (count !== n)
            continue;
        if (choices.some(rs => !rs.some(r => mask & (1 << r))))
            continue;
        if (!generalSatisfied(l, c, new Set(open.filter((_, i) => mask & (1 << i)).map(r => r.id))) || !canMatch(mask))
            continue;
        for (let a = 0; a < n; a++)
            for (const r of choices[a])
                if ((mask & (1 << r)) && !support[a].has(r) && canMatch(mask, a, r))
                    support[a].add(r);
        if (choices.every((rs, a) => rs.every(r => support[a].has(r))))
            break;
    }
    return Object.fromEntries(ids.map((id, a) => [id, Array.from(support[a]).map(i => open[i].id)]));
}
/** Only public quota clues supply targets. Missing quota stays unknown, never a hidden check. */
function floorCountText(level, placement, floor) {
    const current = Object.values(placement).filter(id => level.rooms.some(r => r.id === id && r.floor === floor)).length;
    const quota = floorRules(level).find(c => c.floor === floor);
    return quota ? `${current}/${quota.count}` : '?';
}
exports.floorCountText = floorCountText;
function floorCountState(level, placement, floor) {
    const quota = floorRules(level).find(c => c.floor === floor);
    if (!quota)
        return 'normal';
    const current = Object.values(placement).filter(id => level.rooms.some(r => r.id === id && r.floor === floor)).length;
    return current === quota.count ? 'perfect' : current > quota.count ? 'error' : 'normal';
}
exports.floorCountState = floorCountState;
/** Keep explanatory asides in the glossary and give every numeric quantity breathing room. */
function formatClueText(text) {
    return text.replace(/（(?:去重|不要求紧邻|可以都有|不能都有)）/g, '').replace(/[ \t]*(\d+(?:\.\d+)?)[ \t]*/g, ' $1 ').trim();
}
exports.formatClueText = formatClueText;
function clueText(level, c) { return formatClueText(rawClueText(level, c)); }
exports.clueText = clueText;
function rawClueText(level, c) {
    const name = (id) => level.animals.find(a => a.id === id)?.name || id || '';
    if ((0, exports.isGeneral)(c)) {
        const rule = generalRuleText(level, c);
        return c.text?.trim() && c.text.trim() !== rule ? `${c.text.trim()}\n规则：${rule}` : rule;
    }
    switch (c.type) {
        case 'adjacent': return `${name(c.a)}和${name(c.b)}同层，左右紧邻`;
        case 'differentFloor': return `${name(c.a)}和${name(c.b)}不在同一层`;
        case 'lower': return `${name(c.a)}的楼层比${name(c.b)}低`;
        case 'between': return `${name(c.a)}住在${name(c.b)}、${name(c.c)}之间`;
        case 'residentDirectionCount': return `${name(c.a)}${c.direction === 'left' ? '同层左边' : c.direction === 'right' ? '同层右边' : c.direction === 'above' ? '同列上方' : '同列下方'}的房间，恰好住${c.count}位`;
        case 'residentNeighborCount': return c.direction !== 'around' ? `${name(c.a)}${{ above: '正上方', below: '正下方', left: '左边', right: '右边' }[c.direction]}紧邻的房间${c.count === 1 ? '有人' : '没人'}` : `${name(c.a)}${{ around: '上下左右', above: '正上方', below: '正下方', left: '左边', right: '右边' }[c.direction]}紧邻的房间，恰好住${c.count}位`;
        case 'featureChoice': return `${name(c.a)}的房间${c.mode === 'any' ? '至少' : '恰好'}有${(0, Themes_1.facilityName)(level, c.feature)}和${(0, Themes_1.facilityName)(level, c.feature2)}中的一种`;
        case 'roomEmpty': {
            const rule = generalRuleText(level, c);
            return c.text?.trim() && c.text.trim() !== rule ? `${c.text.trim()}\n规则：${rule}` : rule;
        }
        case 'feature': {
            const first = (0, Themes_1.facilityName)(level, c.feature);
            if (c.feature2) {
                const second = (0, Themes_1.facilityName)(level, c.feature2);
                return `${name(c.a)}住在${c.has && c.has2 ? `有${first}和${second}` : `${c.has ? '有' : '没有'}${first}、${c.has2 ? '有' : '没有'}${second}`}的房间`;
            }
            return `${name(c.a)}住在${c.has ? '有' : '没有'}${first}的房间`;
        }
        case 'floor': return `${name(c.a)}住在${c.floor}楼`;
        case 'higher': return `${name(c.a)}的楼层比${name(c.b)}高`;
        case 'same': return `${name(c.a)}和${name(c.b)}住在同一层`;
        case 'left': return `${name(c.a)}住在${name(c.b)}左边第${c.distance ?? 1}个房间`;
        case 'right': return `${name(c.a)}住在${name(c.b)}右边第${c.distance ?? 1}个房间`;
        case 'below': return `${name(c.a)}住在${name(c.b)}正下方1层`;
        case 'above': return `${name(c.a)}住在${name(c.b)}正上方1层`;
        case 'apart': return `${name(c.a)}和${name(c.b)}同层，但不左右紧邻`;
        case 'quota': return `${c.floor}楼恰好住${c.count}位`;
    }
}
function matches(c, a, b, third) {
    switch (c.type) {
        case 'adjacent': return a.floor === b.floor && Math.abs(a.col - b.col) === 1;
        case 'differentFloor': return a.floor !== b.floor;
        case 'lower': return a.floor < b.floor;
        case 'between': return a.floor === b.floor && a.floor === third.floor && a.col > Math.min(b.col, third.col) && a.col < Math.max(b.col, third.col);
        case 'featureChoice': {
            const n = Number((0, exports.roomHas)(a, c.feature)) + Number((0, exports.roomHas)(a, c.feature2));
            return c.mode === 'any' ? n >= 1 : n === 1;
        }
        case 'roomEmpty': return (0, exports.roomHas)(a, c.feature) !== c.has;
        case 'feature': return (0, exports.roomHas)(a, c.feature) === c.has && (c.feature2 === undefined || (0, exports.roomHas)(a, c.feature2) === c.has2);
        case 'floor': return a.floor === c.floor;
        case 'higher': return a.floor > b.floor;
        case 'same': return a.floor === b.floor;
        case 'left': return a.floor === b.floor && a.col + (c.distance ?? 1) === b.col;
        case 'right': return a.floor === b.floor && a.col === b.col + (c.distance ?? 1);
        case 'below': return a.floor + 1 === b.floor && a.col === b.col;
        case 'above': return a.floor === b.floor + 1 && a.col === b.col;
        case 'apart': return a.floor === b.floor && Math.abs(a.col - b.col) > 1;
        case 'quota': return true;
        default: throw new Error('全屋规则须使用generalSatisfied判定');
    }
}
exports.matches = matches;
/** Only orthogonal adjacent cells; closed rooms never count or bridge a gap. */
function residentNeighborRegion(l, c, anchor) {
    return l.rooms.filter(r => !r.locked && (c.direction === 'around' ? Math.abs(r.col - anchor.col) + Math.abs(r.floor - anchor.floor) === 1 : c.direction === 'left' ? r.floor === anchor.floor && r.col === anchor.col - 1 : c.direction === 'right' ? r.floor === anchor.floor && r.col === anchor.col + 1 : c.direction === 'above' ? r.col === anchor.col && r.floor === anchor.floor + 1 : r.col === anchor.col && r.floor === anchor.floor - 1));
}
exports.residentNeighborRegion = residentNeighborRegion;
/** Directional rays include adjacent rooms, skip maintenance cells, and continue beyond them. */
function residentDirectionRegion(l, c, anchor) {
    return l.rooms.filter(r => !r.locked && (c.direction === 'left' ? r.floor === anchor.floor && r.col < anchor.col : c.direction === 'right' ? r.floor === anchor.floor && r.col > anchor.col : c.direction === 'above' ? r.col === anchor.col && r.floor > anchor.floor : c.direction === 'below' ? r.col === anchor.col && r.floor < anchor.floor : false));
}
exports.residentDirectionRegion = residentDirectionRegion;
const isResidentCount = (c) => c.type === 'residentNeighborCount' || c.type === 'residentDirectionCount';
exports.isResidentCount = isResidentCount;
const residentCountRegion = (l, c, anchor) => c.type === 'residentDirectionCount' ? residentDirectionRegion(l, c, anchor) : residentNeighborRegion(l, c, anchor);
exports.residentCountRegion = residentCountRegion;
/** Local count bounds on public candidates, not a search for the puzzle's answer. */
function residentNeighborSupport(l, c, d) {
    const open = l.rooms.filter(r => !r.locked), others = l.animals.filter(a => a.id !== c.a), support = Object.fromEntries(l.animals.map(a => [a.id, new Set()]));
    for (const anchorId of d[c.a]) {
        const anchor = open.find(r => r.id === anchorId);
        const region = new Set((0, exports.residentCountRegion)(l, c, anchor).map(r => r.id));
        const feasible = (fixedId = '', fixedRoom = '') => {
            const choices = others.map(a => ({ id: a.id, rs: d[a.id].filter(r => r !== anchorId && (a.id === fixedId ? r === fixedRoom : r !== fixedRoom)) }));
            if (choices.some(x => !x.rs.length))
                return false;
            const forced = choices.filter(x => x.rs.every(r => region.has(r))).length, possible = choices.filter(x => x.rs.some(r => region.has(r))).length;
            const inside = new Set(choices.flatMap(x => x.rs.filter(r => region.has(r)))), outside = new Set(choices.flatMap(x => x.rs.filter(r => !region.has(r))));
            return forced <= c.count && possible >= c.count && inside.size >= c.count && outside.size >= others.length - c.count;
        };
        if (!feasible())
            continue;
        support[c.a].add(anchorId);
        for (const a of others)
            for (const r of d[a.id])
                if (r !== anchorId && feasible(a.id, r))
                    support[a.id].add(r);
    }
    return Object.fromEntries(l.animals.map(a => [a.id, Array.from(support[a.id])]));
}
function validateLevel(l) {
    if (!l || !Array.isArray(l.rooms) || !Array.isArray(l.animals) || !Array.isArray(l.clues))
        throw new Error('缺少房间、住客或约定数组');
    const theme = (0, Themes_1.themeFor)(l), features = new Set(theme.facilities.map(f => f.id));
    if (l.learning !== undefined && (!l.learning || !Array.isArray(l.learning.introduces) || l.learning.introduces.some(x => !exports.NEW_CONCEPTS.includes(x)) || new Set(l.learning.introduces).size !== l.learning.introduces.length || typeof l.learning.explanation !== 'string' || l.learning.explanation.length > 500))
        throw new Error('教学配置须包含不重复的新概念和500字以内的教学说明');
    if (l.floorQuotas !== undefined) {
        if (!l.floorQuotas || typeof l.floorQuotas !== 'object' || Array.isArray(l.floorQuotas) || Object.keys(l.floorQuotas).some(k => !/^\d+$/.test(k) || String(Number(k)) !== k))
            throw new Error('楼层人数配置无效');
        if (l.clues.some(c => c.type === 'quota'))
            throw new Error('楼层人数不能同时放在固定信息和约定列表中');
    }
    if (!l.id || typeof l.title !== 'string' || !l.lesson || !Number.isInteger(l.version) || l.version < 1 || !Number.isInteger(l.seed))
        throw new Error('关卡标识、标题、教学文字、版本或种子无效');
    if (l.sequence !== undefined && (!Number.isInteger(l.sequence) || l.sequence < 1))
        throw new Error('关卡序号必须为正整数');
    if (!Number.isInteger(l.cols) || l.cols < 1 || l.cols > 4 || !Number.isInteger(l.floors) || l.floors < 1 || l.floors > 3)
        throw new Error('当前房型支持 1–4 列、1–3 层');
    if (l.animals.length < 1 || l.animals.length > 12 || (0, exports.storyClues)(l).length > 16)
        throw new Error('住客支持 1–12 位，约定最多 16 条（不含固定人数）');
    if (l.rooms.length !== l.cols * l.floors)
        throw new Error('房间必须覆盖完整房型；停用房间请设为关闭');
    const coords = new Set();
    for (const r of l.rooms) {
        if (!r || !Number.isInteger(r.floor) || r.floor < 1 || r.floor > l.floors || !Number.isInteger(r.col) || r.col < 0 || r.col >= l.cols || r.id !== (0, exports.roomName)(r) || typeof r.locked !== 'boolean')
            throw new Error('房间坐标、房牌或关闭状态无效');
        if (!Array.isArray(r.features) || r.features.some(f => !features.has(f)) || new Set(r.features).size !== r.features.length)
            throw new Error('房间设施不属于当前主题或重复');
        if (coords.has(`${r.floor}:${r.col}`))
            throw new Error('房间坐标重复');
        coords.add(`${r.floor}:${r.col}`);
    }
    if (l.animals.some(a => !a || typeof a.id !== 'string' || !/^[a-z][a-z0-9-]*$/.test(a.id) || typeof a.name !== 'string' || !a.name.trim()))
        throw new Error('住客标识或名称无效');
    if (l.animals.some(a => !theme.residents.includes(a.id)))
        throw new Error('住客不属于当前主题');
    if (l.clues.some(c => !c || typeof c.id !== 'string' || !c.id))
        throw new Error('约定缺少标识');
    const quotas = floorRules(l);
    if (new Set(quotas.map(c => c.floor)).size !== quotas.length)
        throw new Error('每层只能有一条人数约定');
    if (l.animals.length > l.rooms.filter(r => !r.locked).length)
        throw new Error('Not enough open rooms');
    if (new Set(l.rooms.map(r => r.id)).size !== l.rooms.length || new Set(l.animals.map(a => a.id)).size !== l.animals.length)
        throw new Error('Duplicate ID');
    if (new Set(l.clues.map(c => c.id)).size !== l.clues.length)
        throw new Error('Duplicate clue ID');
    for (const c of (0, exports.allRules)(l)) {
        if (exports.NEW_CONCEPTS.includes((0, exports.clueConcept)(c))) {
            const fields = ['id', 'type', 'role', 'owner', 'a', ...(c.type === 'featureChoice' ? ['feature', 'feature2', 'mode'] : (0, exports.isResidentCount)(c) ? ['direction', 'count'] : c.type === 'between' ? ['b', 'c'] : ['b'])];
            if (Object.keys(c).some(k => !fields.includes(k)))
                throw new Error('新条件包含不适用的字段，请清除旧类型残留配置');
        }
        if (c.role !== undefined && !['primary', 'supplement'].includes(c.role))
            throw new Error('未知线索角色');
        if (c.role === 'supplement' && c.owner !== undefined)
            throw new Error('补充线索不能配置来源住客');
        if (!['feature', 'floor', 'higher', 'same', 'left', 'right', 'below', 'above', 'apart', 'quota', 'adjacent', 'differentFloor', 'lower', 'between', 'residentNeighborCount', 'residentDirectionCount', 'featureChoice'].includes(c.type) && !(0, exports.isGeneral)(c))
            throw new Error('Unknown rule');
        if ((0, exports.isGeneral)(c)) {
            if (c.role === 'primary')
                throw new Error('通用线索不能作为住客主线索');
            if (c.a !== undefined || c.b !== undefined || c.owner !== undefined)
                throw new Error('通用线索不能归属或关联住客');
            if (c.text !== undefined && (typeof c.text !== 'string' || c.text.trim().length > 120))
                throw new Error('通用线索手写文字最多120字');
        }
        else if (c.owner !== undefined && !l.animals.some(a => a.id === c.owner))
            throw new Error('线索归属必须是本关住客');
        if (!(0, exports.isGeneral)(c) && c.text !== undefined)
            throw new Error('角色线索使用规则模板，不支持自定义文字');
        if (['feature', 'floor', 'quota', 'featureChoice', 'residentNeighborCount', 'residentDirectionCount'].includes(c.type) && c.b !== undefined)
            throw new Error('非关系约定不能包含第二位住客');
        if (c.c !== undefined && c.type !== 'between')
            throw new Error('只有两人之间条件可配置第三位住客');
        if (c.type === 'between' && (!l.animals.some(a => a.id === c.c) || new Set([c.a, c.b, c.c]).size !== 3))
            throw new Error('两人之间须选择三位不同住客');
        if (c.type === 'featureChoice' && (!features.has(c.feature) || !features.has(c.feature2) || c.feature === c.feature2 || !['any', 'exactlyOne'].includes(c.mode)))
            throw new Error('设施二选须选择两种不同的真实设施及至少一种/恰好一种');
        if (c.mode !== undefined && c.type !== 'featureChoice')
            throw new Error('设施选择模式仅用于设施二选条件');
        if (c.feature2 !== undefined && !['feature', 'featureChoice'].includes(c.type))
            throw new Error('第二设施仅用于设施条件');
        if (c.has2 !== undefined && c.type !== 'feature')
            throw new Error('第二设施有无仅用于设施同时满足条件');
        if (c.type === 'feature' && (c.feature2 !== undefined || c.has2 !== undefined) && (!features.has(c.feature) || !features.has(c.feature2) || c.feature === c.feature2 || typeof c.has2 !== 'boolean'))
            throw new Error('合并设施须配置两种不同的真实设施及各自的有无；不支持任意设施');
        if (c.type === 'residentNeighborCount' && (!['around', 'above', 'below', 'left', 'right'].includes(c.direction) || !Number.isInteger(c.count) || c.count < 0 || c.count > (c.direction === 'around' ? 4 : 1) || c.count > l.animals.length - 1))
            throw new Error('角色邻房人数：四周0–4位，单方向0–1位，不能超过其他住客数');
        if (c.type === 'residentDirectionCount' && (!['above', 'below', 'left', 'right'].includes(c.direction) || !Number.isInteger(c.count) || c.count < 0 || c.count > Math.min(l.animals.length - 1, (['left', 'right'].includes(c.direction) ? l.cols : l.floors) - 1)))
            throw new Error('方向范围人数：只选上下左右单方向，数量须为非负整数，不超过该行/列容量或其他住客数');
        if (c.type !== 'quota' && !(0, exports.isGeneral)(c) && !l.animals.some(a => a.id === c.a))
            throw new Error('Unknown subject');
        if (['higher', 'same', 'left', 'right', 'below', 'above', 'apart', 'adjacent', 'differentFloor', 'lower', 'between'].includes(c.type) && (!l.animals.some(a => a.id === c.b) || c.a === c.b))
            throw new Error('Unknown relation');
        if (c.distance !== undefined && (!['left', 'right'].includes(c.type) || !Number.isInteger(c.distance) || c.distance < 1 || c.distance > 3))
            throw new Error('左右位置必须为1–3个房间；正上方/正下方固定相差1层');
        if (['feature', 'roomEmpty'].includes(c.type) && (!(features.has(c.feature) || (c.type === 'feature' && c.feature === 'any')) || typeof c.has !== 'boolean'))
            throw new Error('Invalid feature');
        if (['floor', 'quota'].includes(c.type) && (!Number.isInteger(c.floor) || c.floor < 1 || c.floor > l.floors))
            throw new Error('Invalid floor');
        if (c.type === 'quota' && (!Number.isInteger(c.count) || c.count < 0 || c.count > l.cols))
            throw new Error('Invalid quota');
        if (['facilityNeighborCount', 'facilityOccupancy'].includes(c.type) && !features.has(c.feature))
            throw new Error('通用线索设施无效');
        if (c.type === 'adjacentCount' && !['horizontal', 'vertical'].includes(c.axis))
            throw new Error('请选择左右或上下紧邻');
        if (c.type === 'facilityNeighborCount' && !['around', 'above', 'below', 'left', 'right'].includes(c.direction))
            throw new Error('设施邻接方向无效');
        if (c.type === 'cornerOccupancy' && typeof c.has !== 'boolean')
            throw new Error('请选择角落有无住户');
        if (['adjacentCount', 'facilityNeighborCount', 'facilityOccupancy'].includes(c.type) && (!Number.isInteger(c.count) || c.count < 0 || c.count > 12))
            throw new Error('通用线索数量须为0–12的整数');
    }
}
exports.validateLevel = validateLevel;
/** Sound deductions only: unary filtering, binary support, fixed occupancy and floor quotas. No guessing. */
function deduce(l, initial, deadline = Infinity) {
    const rooms = Object.fromEntries(l.rooms.map(r => [r.id, r]));
    const open = l.rooms.filter(r => !r.locked).map(r => r.id);
    const d = Object.fromEntries(l.animals.map(a => [a.id, [...(initial?.[a.id] || open)]]));
    const steps = [];
    let changed = true;
    const narrow = (id, keep, reason, clueIds) => {
        const before = d[id], after = before.filter(keep);
        if (after.length === before.length)
            return;
        d[id] = after;
        changed = true;
        steps.push({ animal: id, removed: before.filter(r => !after.includes(r)), remaining: [...after], reason, clueIds });
    };
    while (changed && Object.values(d).every(a => a.length)) {
        changed = false;
        for (const c of (0, exports.allRules)(l)) {
            const text = c.type === 'quota' ? `固定人数：${clueText(l, c)}` : `约定 ${(0, exports.storyClues)(l).indexOf(c) + 1}：${clueText(l, c)}`;
            if (c.type === 'quota') {
                const forced = l.animals.filter(a => d[a.id].length && d[a.id].every(r => rooms[r].floor === c.floor));
                const possible = l.animals.filter(a => d[a.id].some(r => rooms[r].floor === c.floor));
                if (forced.length > c.count || possible.length < c.count) {
                    d[l.animals[0].id] = [];
                    break;
                }
                if (forced.length === c.count)
                    for (const a of l.animals.filter(a => !forced.includes(a)))
                        narrow(a.id, r => rooms[r].floor !== c.floor, `${text}；该层名额已被确定的住客占满`, [c.id]);
                if (possible.length === c.count)
                    for (const a of possible)
                        narrow(a.id, r => rooms[r].floor === c.floor, `${text}；能住这一层的住客数恰好等于人数要求`, [c.id]);
            }
            else if (c.type === 'roomEmpty') {
                for (const a of l.animals)
                    narrow(a.id, r => matches(c, rooms[r]), text, [c.id]);
            }
            else if ((0, exports.isGeneral)(c)) {
                const support = generalSupport(l, c, d, deadline);
                for (const a of l.animals)
                    narrow(a.id, r => support[a.id].includes(r), `${text}；按全屋人数和每房最多一位筛除无可行占用组合的位置`, [c.id]);
            }
            else if ((0, exports.isResidentCount)(c)) {
                const support = residentNeighborSupport(l, c, d);
                for (const a of l.animals)
                    narrow(a.id, r => support[a.id].includes(r), `${text}；逐个检查中心房的${c.type === 'residentDirectionCount' ? '方向范围' : '邻区'}：必住人数不能超额，可住人数及可用房数必须足额（不含中心住客）`, [c.id]);
            }
            else if (c.type === 'between') {
                const ids = [c.a, c.b, c.c], support = Object.fromEntries(ids.map(id => [id, new Set()]));
                for (const a of d[c.a])
                    for (const b of d[c.b])
                        for (const z of d[c.c])
                            if (new Set([a, b, z]).size === 3 && matches(c, rooms[a], rooms[b], rooms[z])) {
                                support[c.a].add(a);
                                support[c.b].add(b);
                                support[c.c].add(z);
                            }
                for (const id of ids)
                    narrow(id, r => support[id].has(r), `${text}；同层三人中，主语必须处于另两人的列号之间，两端顺序不限`, [c.id]);
            }
            else if (!c.b)
                narrow(c.a, r => matches(c, rooms[r]), text, [c.id]);
            else {
                narrow(c.a, r => d[c.b].some(s => r !== s && matches(c, rooms[r], rooms[s])), `${text}；排除找不到对应位置的房间`, [c.id]);
                narrow(c.b, s => d[c.a].some(r => r !== s && matches(c, rooms[r], rooms[s])), `${text}；排除找不到对应位置的房间`, [c.id]);
            }
        }
        for (const a of l.animals)
            if (d[a.id].length === 1) {
                const room = d[a.id][0];
                for (const b of l.animals)
                    if (a.id !== b.id)
                        narrow(b.id, r => r !== room, `${a.name}已只能住${room}；每间最多一位`, []);
            }
    }
    return { domains: d, steps, solved: Object.values(d).every(a => a.length === 1), contradiction: Object.values(d).some(a => !a.length) };
}
exports.deduce = deduce;
function solve(l, options = {}) {
    validateLevel(l);
    const start = Date.now(), solutions = [];
    let nodes = 0, timedOut = false, cutOff = false;
    const limit = Math.max(2, options.limit || 2);
    function visit(domains) {
        if (solutions.length >= limit) {
            cutOff = true;
            return;
        }
        if (++nodes > (options.maxNodes ?? 100000) || Date.now() - start >= (options.timeoutMs ?? 5000)) {
            timedOut = true;
            return;
        }
        let result;
        try {
            result = deduce(l, domains, start + (options.timeoutMs ?? 5000));
        }
        catch (e) {
            if (e.message !== 'RULE_BUDGET_EXCEEDED')
                throw e;
            timedOut = true;
            return;
        }
        if (result.contradiction)
            return;
        if (result.solved) {
            const answer = Object.fromEntries(Object.entries(result.domains).map(([id, rooms]) => [id, rooms[0]]));
            if (check(l, answer).ok)
                solutions.push(answer);
            return;
        }
        const [id, candidates] = Object.entries(result.domains).filter(([, rs]) => rs.length > 1).sort((a, b) => a[1].length - b[1].length)[0];
        for (const r of candidates) {
            visit({ ...result.domains, [id]: [r] });
            if (timedOut || solutions.length >= limit) {
                cutOff = solutions.length >= limit;
                return;
            }
        }
    }
    visit();
    return { solutions, nodes, elapsedMs: Date.now() - start, complete: !timedOut && !cutOff, status: timedOut ? 'unverified' : solutions.length > 1 ? 'multiple' : solutions.length === 1 ? 'unique' : 'none' };
}
exports.solve = solve;
function check(l, p) {
    const values = Object.values(p);
    if (Object.keys(p).some(id => !l.animals.some(a => a.id === id)) || values.some(id => !l.rooms.some(r => r.id === id && !r.locked)))
        return { ok: false, message: '入住数据不合法，请取回后重试', clues: [] };
    if (new Set(values).size !== values.length)
        return { ok: false, message: '一间房只能住一位', clues: [] };
    if (l.animals.some(a => !p[a.id]))
        return { ok: false, message: '还有住客没有入住', clues: [] };
    const byId = Object.fromEntries(l.rooms.map(r => [r.id, r]));
    const occupied = new Set(values);
    const bad = (0, exports.allRules)(l).filter(c => c.type === 'quota' ? values.filter(r => byId[r].floor === c.floor).length !== c.count : (0, exports.isGeneral)(c) ? !generalSatisfied(l, c, occupied) : (0, exports.isResidentCount)(c) ? (0, exports.residentCountRegion)(l, c, byId[p[c.a]]).filter(r => occupied.has(r.id)).length !== c.count : !matches(c, byId[p[c.a]], c.b ? byId[p[c.b]] : undefined, c.c ? byId[p[c.c]] : undefined));
    return { ok: !bad.length, message: bad.length ? `再看看：${clueText(l, bad[0])}` : '每一条约定都实现了，晚安！', clues: bad.map(c => c.id) };
}
exports.check = check;
/** Explanation for a requested resident, derived from public constraints only. */
function publicPlacementHint(l, id) {
    let proof;
    try {
        proof = deduce(l, undefined, Date.now() + 1500);
    }
    catch {
        return null;
    }
    const a = l.animals.find(a => a.id === id), rs = proof.domains[id];
    if (!a || proof.contradiction || rs?.length !== 1)
        return null;
    const end = proof.steps.findIndex(s => s.animal === id && s.remaining.length === 1), trail = proof.steps.slice(0, end + 1);
    return { key: `${id}:${rs[0]}`, animal: id, room: rs[0], title: '一个有依据的发现', text: trail.map(s => `${l.animals.find(a => a.id === s.animal).name}：${s.reason}，候选剩 ${s.remaining.join('、')}`).join('\n') + `\n所以${a.name}只能住${rs[0]}。`, clueIds: Array.from(new Set(trail.flatMap(s => s.clueIds))) };
}
exports.publicPlacementHint = publicPlacementHint;
function nextHint(l, p, notes, delivered) {
    const proof = deduce(l);
    if (proof.contradiction)
        return null;
    const known = l.animals.filter(a => proof.domains[a.id].length === 1);
    const a = known.find(a => p[a.id] && p[a.id] !== proof.domains[a.id][0]) || known.find(a => notes[`${a.id}:${proof.domains[a.id][0]}`] === 2) || known.find(a => !p[a.id] && !delivered.includes(`${a.id}:${proof.domains[a.id][0]}`));
    if (!a)
        return null;
    const room = proof.domains[a.id][0], finalIndex = proof.steps.findIndex(s => s.animal === a.id && s.remaining.length === 1);
    // Include the prerequisite deductions in chronological order, not just a naked solution lookup.
    const trail = proof.steps.slice(0, finalIndex + 1);
    const reasons = trail.map(s => `${l.animals.find(a => a.id === s.animal).name}：${s.reason}，候选剩 ${s.remaining.join('、') || '无'}`);
    const wrong = p[a.id] && p[a.id] !== room;
    return { key: `${a.id}:${room}`, animal: a.id, room, title: wrong ? '先修正一处入住' : '一个有依据的发现', text: `${reasons.join('\n')}\n所以${a.name}只能住${room}。${wrong ? `当前${p[a.id]}不满足这些推导。` : notes[`${a.id}:${room}`] === 2 ? '这里被误记为排除，请先修正笔记。' : ''}`, clueIds: Array.from(new Set(trail.flatMap(s => s.clueIds))) };
}
exports.nextHint = nextHint;
