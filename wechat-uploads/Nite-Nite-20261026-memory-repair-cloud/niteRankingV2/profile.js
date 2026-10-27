'use strict';
/** Trust only WeChat-decrypted data belonging to this invocation's OPENID. */
async function resolveWechatProfile(cloud,uid,event){
 const invalid=()=>Object.assign(Error('头像昵称暂时无法获取，请稍后重试。'),{code:'PROFILE'});
 if(typeof event?.cloudID!=='string'||!event.cloudID||event.cloudID.length>2048)throw invalid();
 const result=await cloud.getOpenData({list:[event.cloudID]});
 const data=result?.list?.[0]?.data;
 const context=cloud.getWXContext();
 if(!data||data.openId!==uid||data.watermark?.appid&&data.watermark.appid!==context.APPID)throw invalid();
 const name=typeof data.nickName==='string'?data.nickName.trim():'',url=typeof data.avatarUrl==='string'?data.avatarUrl.replace(/^http:\/\//i,'https://'):data.avatarUrl;
 if(!name||Array.from(name).length>64||/[\u0000-\u001f\u007f]/.test(name)||typeof url!=='string'||url.length>2048||!/^https:\/\/(?:[a-z0-9-]+\.)*(?:qlogo|qpic)\.cn\//i.test(url))throw invalid();
 return {name,avatarUrl:url};
}
module.exports={resolveWechatProfile};

