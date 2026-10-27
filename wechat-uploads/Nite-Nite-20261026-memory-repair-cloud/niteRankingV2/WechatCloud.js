"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.wechatCloud = void 0;
// wx.cloud is a lazy SDK getter. Re-reading it can decorate the same methods again.
// Share one handle across services without replacing any platform property.
const handles = new WeakMap();
function wechatCloud(platform) {
    if (!platform || (typeof platform !== 'object' && typeof platform !== 'function'))
        return undefined;
    const cached = handles.get(platform);
    if (cached)
        return cached;
    const cloud = platform.cloud;
    if (cloud && typeof cloud.callFunction === 'function')
        handles.set(platform, cloud);
    return cloud;
}
exports.wechatCloud = wechatCloud;
