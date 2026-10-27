"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.readJournal = exports.flushClearQueue = exports.seedClearQueue = exports.COMPETITION_KEY = exports.CompetitionClient = exports.cloudCallError = exports.regionName = exports.REGIONS = void 0;
const RuntimeDiagnostics_1 = require("./RuntimeDiagnostics");
/** Stable official administrative codes; pinyin is explicit, never device-locale sorting. */
exports.REGIONS = [
    ['11', '北京', 'beijing'], ['12', '天津', 'tianjin'], ['13', '河北', 'hebei'], ['14', '山西', 'shanxi'], ['15', '内蒙古', 'neimenggu'],
    ['21', '辽宁', 'liaoning'], ['22', '吉林', 'jilin'], ['23', '黑龙江', 'heilongjiang'], ['31', '上海', 'shanghai'], ['32', '江苏', 'jiangsu'], ['33', '浙江', 'zhejiang'], ['34', '安徽', 'anhui'], ['35', '福建', 'fujian'], ['36', '江西', 'jiangxi'], ['37', '山东', 'shandong'],
    ['41', '河南', 'henan'], ['42', '湖北', 'hubei'], ['43', '湖南', 'hunan'], ['44', '广东', 'guangdong'], ['45', '广西', 'guangxi'], ['46', '海南', 'hainan'], ['50', '重庆', 'chongqing'], ['51', '四川', 'sichuan'], ['52', '贵州', 'guizhou'], ['53', '云南', 'yunnan'], ['54', '西藏', 'xizang'], ['61', '陕西', 'shanxi'], ['62', '甘肃', 'gansu'], ['63', '青海', 'qinghai'], ['64', '宁夏', 'ningxia'], ['65', '新疆', 'xinjiang'], ['71', '台湾', 'taiwan'], ['81', '香港', 'xianggang'], ['82', '澳门', 'aomen']
].map(([id, name, pinyin]) => ({ id, name, pinyin }));
const regionName = (id) => exports.REGIONS.find(r => r.id === id)?.name || '未选择';
exports.regionName = regionName;
/** Keep the actual cloud error code; function startup errors are not network outages. */
function cloudCallError(error) {
    const detail = String(error?.errMsg || error?.message || '');
    const code = detail.match(/errCode:\s*(-?\d+)/)?.[1] || String(error?.errCode || 'CLOUD_CALL');
    const message = /timeout|timed out/i.test(detail) ? '服务连接超时，请稍后重试。' :
        /functions execute fail|Cannot find module/i.test(detail) ? '挑战服务启动失败，请稍后重试。' :
            /network|disconnected|internet/i.test(detail) ? '网络连接中断，请检查网络后重试。' : '云服务连接失败，请稍后重试。';
    return Object.assign(Error(message + '（' + code + '）'), { code });
}
exports.cloudCallError = cloudCallError;
class CompetitionClient {
    constructor(environment = '', platform = () => globalThis.wx) {
        this.environment = environment;
        this.platform = platform;
        this.initialized = '';
        this.identityJob = null;
        this.identityEnvironment = '';
    }
    /** Server-derived account identity, once per launch/environment; never trust a local user id. */
    accountScope() {
        if (this.identityJob && this.identityEnvironment === this.environment)
            return this.identityJob;
        const environment = this.environment;
        this.identityEnvironment = environment;
        const job = this.call('profileGet').then(r => { const id = r.profile?.accountId; if (typeof id !== 'string' || !id)
            throw Error('账号暂未确认，通关记录已保留。'); return environment + '|' + id; });
        this.identityJob = job;
        void job.catch(() => { if (this.identityJob === job)
            this.identityJob = null; });
        return job;
    }
    async call(action, data = {}) {
        const finish = RuntimeDiagnostics_1.runtimeDiagnostics.span('cloud.' + action);
        try {
            const wx = this.platform();
            if (!this.environment)
                throw Error('排行榜和每日挑战尚未开放，请稍后再来。');
            if (!wx?.cloud?.callFunction)
                throw Error('请在支持云开发的微信小游戏内使用。');
            if (this.initialized !== this.environment) {
                RuntimeDiagnostics_1.runtimeDiagnostics.record('cloud-init');
                wx.cloud.init({ env: this.environment, traceUser: false });
                this.initialized = this.environment;
            }
            const reply = await new Promise((resolve, reject) => {
                let done = false;
                const timer = setTimeout(() => { if (!done) {
                    done = true;
                    RuntimeDiagnostics_1.runtimeDiagnostics.record('cloud-timeout', { action });
                    reject(Error('连接超时，请重试；重复提交不会重复计分。'));
                } }, 15000);
                const fail = (error) => { if (!done) {
                    done = true;
                    clearTimeout(timer);
                    console.error('[niteCompetition]', { action, environment: this.environment, errCode: error?.errCode, errMsg: error?.errMsg || error?.message });
                    reject(cloudCallError(error));
                } };
                try {
                    wx.cloud.callFunction({ name: 'niteCompetition', config: { env: this.environment }, data: { action, ...data }, success: (r) => { if (!done) {
                            done = true;
                            clearTimeout(timer);
                            resolve(r.result);
                        } }, fail });
                }
                catch (error) {
                    fail(error);
                }
            });
            if (!reply?.ok)
                throw Object.assign(Error(reply?.message || '服务暂不可用，请稍后重试。'), { code: reply?.code });
            finish('ok');
            return reply;
        }
        catch (error) {
            finish('error');
            RuntimeDiagnostics_1.runtimeDiagnostics.fault('cloud', error);
            throw error;
        }
    }
    publishFriends(count, reachedAt) {
        // Only publish the server-confirmed permanent score; never local completed.length.
        try {
            this.platform()?.setUserCloudStorage?.({ KVDataList: [{ key: 'nite-progress-v1', value: JSON.stringify({ count, reachedAt }) }], fail: () => { } });
        }
        catch { }
    }
}
exports.CompetitionClient = CompetitionClient;
exports.COMPETITION_KEY = 'nite-competition-v1';
/** Reconcile old saves only against receipts for this cloud environment/account. */
function seedClearQueue(journal, proofs, scope) {
    if (journal.synced?.scope !== scope)
        journal.synced = { scope, versions: {} };
    for (const proof of proofs) {
        const i = journal.pending.findIndex(p => p.levelId === proof.levelId);
        if (i < 0)
            journal.pending.push(proof);
        else if (journal.pending[i].version !== proof.version)
            journal.pending[i] = proof;
    }
    journal.pending = journal.pending.filter(p => journal.synced.versions[p.levelId] !== p.version);
}
exports.seedClearQueue = seedClearQueue;
/** Persist each acknowledgement atomically with dequeue; a failed save stays retryable. */
async function flushClearQueue(journal, client, persist) {
    if (!journal.synced)
        return;
    const attempted = new Set();
    // Clears arriving during an in-flight request belong to this batch too.
    for (let proof = journal.pending.find(p => !attempted.has(p)); proof; proof = journal.pending.find(p => !attempted.has(p))) {
        attempted.add(proof);
        try {
            const r = await client.call('clear', proof);
            if (!Number.isSafeInteger(r.count) || r.count < 0 || !Number.isFinite(r.reachedAt))
                throw Error('无效的成绩响应');
            const previous = journal.synced, pending = journal.pending;
            journal.synced = { ...previous, versions: { ...previous.versions, [proof.levelId]: proof.version }, score: { count: r.count, reachedAt: r.reachedAt } };
            journal.pending = pending.filter(p => p !== proof);
            if (!persist()) {
                journal.synced = previous;
                journal.pending = pending;
                break;
            }
        }
        catch (e) {
            if (e.code !== 'ANSWER')
                break;
        }
    }
    // One permanent-score publication per batch/resume, also repairs earlier platform failures.
    const score = journal.synced.score;
    if (score)
        client.publishFriends(score.count, score.reachedAt);
}
exports.flushClearQueue = flushClearQueue;
function readJournal(storage) {
    try {
        const s = JSON.parse(storage.getItem(exports.COMPETITION_KEY) || 'null');
        if (s && Array.isArray(s.pending) && s.pending.length <= 1000) {
            const pending = s.pending.filter((p) => p && typeof p.levelId === 'string' && Number.isSafeInteger(p.version) && p.placements && typeof p.placements === 'object' && !Array.isArray(p.placements));
            const daily = s.daily?.ticket?.level?.id && typeof s.daily.ticket.day === 'string' && exports.REGIONS.some(r => r.id === s.daily.ticket.region) && s.daily.save ? s.daily : undefined;
            let synced;
            const receipt = s.synced;
            if (receipt && typeof receipt.scope === 'string' && receipt.versions && typeof receipt.versions === 'object' && !Array.isArray(receipt.versions)) {
                const versions = Object.fromEntries(Object.entries(receipt.versions).filter(([id, v]) => id !== '__proto__' && Number.isSafeInteger(v)).slice(0, 1000));
                const score = receipt.score && Number.isSafeInteger(receipt.score.count) && receipt.score.count >= 0 && Number.isFinite(receipt.score.reachedAt) ? receipt.score : undefined;
                synced = { scope: receipt.scope, versions, score };
            }
            return { region: exports.REGIONS.some(r => r.id === s.region) ? s.region : '', daily, pending, synced };
        }
    }
    catch { }
    return { region: '', pending: [] };
}
exports.readJournal = readJournal;
