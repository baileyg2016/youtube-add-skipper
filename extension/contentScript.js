console.log('contentScript.js loaded')
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === 'getTimestamp') {
        const video = document.querySelector('video');
        if (video) {
        sendResponse({ success: true, timestamp: video.currentTime });
        } else {
        sendResponse({ success: false });
        }
    }
    return true;
});
  