"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.facilityName = exports.themeFor = exports.THEMES = exports.RESIDENTS = void 0;
exports.RESIDENTS = [
    ['rabbit', '小兔'], ['cat', '小猫'], ['fox', '小狐'], ['owl', '猫头鹰'], ['hedgehog', '刺猬'], ['deer', '小鹿'],
    ['otter', '水獭'], ['bear', '小熊'], ['panda', '熊猫'], ['dog', '小狗'], ['koala', '考拉'], ['pig', '小猪']
].map(([id, name]) => ({ id, name }));
const basic = [{ id: 'window', name: '窗户', art: 'window' }, { id: 'lamp', name: '夜灯', art: 'lamp' }, { id: 'plant', name: '绿植', art: 'plant' }, { id: 'books', name: '书架', art: 'books' }];
exports.THEMES = [
    { id: 'moonlight', chapterStart: 1, name: '月光小屋', roomArt: 'room', residents: exports.RESIDENTS.map(a => a.id), facilities: basic },
    { id: 'forest', chapterStart: 101, authoredFurnishings: true, name: '森林树屋', roomArt: 'room-forest', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'fireplace', name: '壁炉', art: 'fireplace' }, { id: 'rug', name: '地毯', art: 'rug' },
            { id: 'clock', name: '挂钟', art: 'clock' }, { id: 'aquarium', name: '鱼缸', art: 'aquarium' }, { id: 'chime', name: '风铃', art: 'chime' }] },
    { id: 'seaside', chapterStart: 201, authoredFurnishings: true, name: '海风小屋', roomArt: 'room-seaside', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'shell', name: '贝壳摆件', art: 'shell' }, { id: 'sailboat', name: '帆船模型', art: 'sailboat' },
            { id: 'lifebuoy', name: '救生圈', art: 'lifebuoy' }, { id: 'telescope', name: '望远镜', art: 'telescope' }, { id: 'bottle', name: '漂流瓶', art: 'bottle' }] },
    { id: 'cloud', chapterStart: 301, authoredFurnishings: true, name: '云端小屋', roomArt: 'room-cloud', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'kite', name: '风筝', art: 'kite' }, { id: 'balloon', name: '热气球模型', art: 'balloon' }, { id: 'feather', name: '羽毛摆件', art: 'feather' }, { id: 'cloudMobile', name: '云朵吊饰', art: 'cloudMobile' }, { id: 'windsock', name: '风向袋', art: 'windsock' }] },
    { id: 'snow', chapterStart: 401, authoredFurnishings: true, name: '雪夜木屋', roomArt: 'room-snow', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'mittens', name: '手套', art: 'mittens' }, { id: 'skis', name: '滑雪板', art: 'skis' }, { id: 'snowglobe', name: '雪花球', art: 'snowglobe' }, { id: 'scarf', name: '围巾', art: 'scarf' }, { id: 'stove', name: '暖炉', art: 'stove' }] },
    { id: 'garden', chapterStart: 501, authoredFurnishings: true, name: '花园小屋', roomArt: 'room-garden', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'wateringCan', name: '喷壶', art: 'wateringCan' }, { id: 'birdhouse', name: '鸟屋', art: 'birdhouse' }, { id: 'wreath', name: '花环', art: 'wreath' }, { id: 'honeyJar', name: '蜂蜜罐', art: 'honeyJar' }, { id: 'seedBox', name: '种子盒', art: 'seedBox' }] },
    { id: 'desert', chapterStart: 601, authoredFurnishings: true, name: '沙丘驿站', roomArt: 'room-desert', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'hourglass', name: '沙漏', art: 'hourglass' }, { id: 'teapot', name: '茶壶', art: 'teapot' }, { id: 'lute', name: '鲁特琴', art: 'lute' }, { id: 'copperTray', name: '铜盘', art: 'copperTray' }, { id: 'ceramicVase', name: '陶罐', art: 'ceramicVase' }] },
    { id: 'starlight', chapterStart: 701, authoredFurnishings: true, name: '星河小屋', roomArt: 'room-starlight', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'globe', name: '地球仪', art: 'globe' }, { id: 'starChart', name: '星图', art: 'starChart' }, { id: 'rocket', name: '火箭模型', art: 'rocket' }, { id: 'moonMobile', name: '月亮吊饰', art: 'moonMobile' }, { id: 'meteorite', name: '陨石', art: 'meteorite' }] },
    { id: 'rain', chapterStart: 801, authoredFurnishings: true, name: '雨巷小屋', roomArt: 'room-rain', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'umbrella', name: '雨伞', art: 'umbrella' }, { id: 'rainBoots', name: '雨靴', art: 'rainBoots' }, { id: 'radio', name: '收音机', art: 'radio' }, { id: 'paperLantern', name: '纸灯笼', art: 'paperLantern' }, { id: 'teaCup', name: '茶杯', art: 'teaCup' }] },
    { id: 'candy', chapterStart: 901, authoredFurnishings: true, name: '糖果小屋', roomArt: 'room-candy', residents: exports.RESIDENTS.map(a => a.id), facilities: [...basic,
            { id: 'musicBox', name: '音乐盒', art: 'musicBox' }, { id: 'cookieJar', name: '饼干罐', art: 'cookieJar' }, { id: 'candyMachine', name: '糖果机', art: 'candyMachine' }, { id: 'gingerbread', name: '姜饼人', art: 'gingerbread' }, { id: 'cakeStand', name: '甜点架', art: 'cakeStand' }] },
    { id: 'reading', name: '阅读小屋（扩展样板）', roomArt: 'room-reading', residents: ['rabbit', 'cat', 'fox', 'owl', 'bear', 'panda', 'pig'], facilities: basic }
];
function themeFor(level) {
    const theme = exports.THEMES.find(t => t.id === (level.themeId ?? 'moonlight'));
    if (!theme)
        throw new Error('未知房屋主题');
    return theme;
}
exports.themeFor = themeFor;
const facilityName = (level, id) => id === 'any' ? '设施' : themeFor(level).facilities.find(f => f.id === id)?.name || id;
exports.facilityName = facilityName;
