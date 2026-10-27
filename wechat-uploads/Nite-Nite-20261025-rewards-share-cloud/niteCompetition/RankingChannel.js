"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.rankingJournalKey = exports.rankingFriendKey = exports.rankingChannel = void 0;
/** Unknown runtimes fail closed into the test namespace. This is routing, not anti-cheat auth. */
function rankingChannel(platform) {
    try {
        return platform?.getAccountInfoSync?.()?.miniProgram?.envVersion === 'release' ? 'release' : 'test';
    }
    catch {
        return 'test';
    }
}
exports.rankingChannel = rankingChannel;
const rankingFriendKey = (channel) => 'nite-highest-v2-' + channel;
exports.rankingFriendKey = rankingFriendKey;
const rankingJournalKey = (channel) => 'nite-competition-highest-v2-' + channel;
exports.rankingJournalKey = rankingJournalKey;
