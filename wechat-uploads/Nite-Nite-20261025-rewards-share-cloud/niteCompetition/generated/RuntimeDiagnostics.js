"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runtimeDiagnostics = exports.RuntimeDiagnostics = exports.DIAGNOSTIC_REVISION = exports.DIAGNOSTIC_KEY = void 0;
/** Bounded, local-only breadcrumbs. Never wraps Promise/timers or calls cloud/log-upload APIs. */
exports.DIAGNOSTIC_KEY = 'nite-diagnostics-v1';
exports.DIAGNOSTIC_REVISION = 'cloud-step1-20261013';
const token = (value) => typeof value === 'string' ? value.slice(0, 80).replace(/[^a-zA-Z0-9_.:-]/g, '_') : '';
class RuntimeDiagnostics {
    constructor(now = () => Date.now()) {
        this.now = now;
        this.entries = [];
        this.first = {};
        this.storage = null;
        this.previous = null;
        this.recording = false;
        this.saving = false;
        this.canvases = new WeakSet();
        this.installed = new WeakSet();
        this.sequence = 0;
        this.faults = 0;
        this.lastFault = -Infinity;
        this.visibility = '';
        this.heartbeatAt = 0;
        this.background = false;
        this.blankSince = 0;
        this.blankReported = false;
        this.started = now();
    }
    attach(storage, api) {
        if (!this.storage) {
            this.storage = storage;
            try {
                const old = JSON.parse(storage.getItem(exports.DIAGNOSTIC_KEY) || 'null');
                if (old?.schema === 1)
                    this.previous = old.current;
            }
            catch { }
        }
        if (!api || typeof api !== 'object' || this.installed.has(api))
            return;
        this.installed.add(api);
        const bind = (name, fn) => { try {
            api[name]?.(fn);
        }
        catch { } };
        bind('onError', error => this.fault('uncaught', error));
        bind('onUnhandledRejection', event => this.fault('unhandled', event?.reason));
        bind('onMemoryWarning', event => { this.record('memory-warning', { level: Number(event?.level) || 0 }); this.persist(); });
    }
    attachCanvas(canvas) {
        if (!canvas || typeof canvas !== 'object' || this.canvases.has(canvas))
            return;
        this.canvases.add(canvas);
        for (const name of ['webglcontextlost', 'webglcontextrestored'])
            try {
                canvas.addEventListener?.(name, () => { this.record(name); this.persist(); });
            }
            catch { }
    }
    record(event, data = {}) {
        if (this.recording)
            return;
        this.recording = true;
        try {
            const safe = {};
            for (const [key, value] of Object.entries(data).slice(0, 8)) {
                if (typeof value === 'number' && Number.isFinite(value) || typeof value === 'boolean')
                    safe[token(key)] = value;
                else if (typeof value === 'string')
                    safe[token(key)] = token(value);
            }
            this.entries.push({ ms: Math.max(0, this.now() - this.started), event: token(event), data: safe });
            if (this.entries.length > 64)
                this.entries.shift();
        }
        catch { }
        finally {
            this.recording = false;
        }
    }
    mark(name) { if (Object.prototype.hasOwnProperty.call(this.first, name))
        return false; this.first[name] = Math.max(0, this.now() - this.started); this.record(name); return true; }
    span(name) { const id = ++this.sequence, start = this.now(); this.record('begin', { name, id }); let done = false; return (status) => { if (done)
        return; done = true; this.record('end', { name, id, status, durationMs: Math.max(0, this.now() - start) }); }; }
    fault(source, error) {
        if (this.recording || this.saving)
            return;
        // Bound error storms and never store user text, URLs, account IDs or cloud payloads.
        const now = this.now();
        this.faults++;
        if (now - this.lastFault < 1000)
            return;
        this.lastFault = now;
        try {
            const message = String(typeof error === 'string' ? error : error?.stack || error?.message || '').slice(0, 8192);
            const category = /Maximum call stack|stack overflow/i.test(message) ? 'stack-overflow' : /out of memory|allocation failed/i.test(message) ? 'memory' : /timeout/i.test(message) ? 'timeout' : 'exception';
            const frames = (message.match(/[A-Za-z0-9_.-]+\.js:\d+:\d+/g) || []).slice(0, 5).join(',');
            this.record('fault', { source, category, frames });
            this.persist();
        }
        catch { }
    }
    lifecycle(hidden) { this.background = hidden; this.heartbeatAt = 0; this.blankSince = 0; this.blankReported = false; this.record(hidden ? 'app-hide' : 'app-show'); this.persist(); }
    /** Called by the existing one-second UI tick, not an additional timer or per-frame sampler. */
    observe(visible, blocked) {
        if (this.background)
            return;
        const now = this.now();
        if (this.heartbeatAt && now - this.heartbeatAt > 4000)
            this.record('foreground-gap', { durationMs: now - this.heartbeatAt });
        this.heartbeatAt = now;
        const key = visible + ':' + blocked;
        if (key !== this.visibility) {
            this.visibility = key;
            this.record('visibility', { pages: visible, blocked });
        }
        if (!visible && !blocked) {
            if (!this.blankSince)
                this.blankSince = now;
            else if (!this.blankReported && now - this.blankSince >= 3000) {
                this.blankReported = true;
                this.record('no-visible-page');
                this.persist();
            }
        }
        else {
            this.blankSince = 0;
            this.blankReported = false;
        }
    }
    snapshot() { return { schema: 1, current: { revision: exports.DIAGNOSTIC_REVISION, startedAt: this.started, first: { ...this.first }, faults: this.faults, entries: this.entries.map(e => ({ ...e, data: { ...e.data } })) }, previous: this.previous }; }
    persist() { if (!this.storage || this.saving)
        return; this.saving = true; try {
        const snapshot = this.snapshot();
        let text = JSON.stringify(snapshot);
        if (text.length > 24000) {
            snapshot.previous = null;
            text = JSON.stringify(snapshot);
        }
        this.storage.setItem(exports.DIAGNOSTIC_KEY, text);
    }
    catch { }
    finally {
        this.saving = false;
    } }
}
exports.RuntimeDiagnostics = RuntimeDiagnostics;
exports.runtimeDiagnostics = new RuntimeDiagnostics();
