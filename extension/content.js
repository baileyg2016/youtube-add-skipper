console.log('contentScript.js loaded')

ads = [];

function postData(url = '', data = {}) {
    console.log('Sending data:', data);
    return fetch(url, {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('message received:', request.message);
    if (request.message === 'getTimestamp') {
        const video = document.querySelector('video');
        if (video) {
            sendResponse({ success: true, timestamp: video.currentTime });
        } else {
            sendResponse({ success: false });
        }
    }
    else if (request.message === 'skipAd') {
        console.log('skipAd:', request.skip);
        const video = document.querySelector('video');
        video.currentTime += request.skip;
    }

    return true;
});

(function() {
    console.log('making post request');
    postData('http://localhost:8080/', { youtube_url: window.location.href })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data) => {
        console.log('Data sent successfully:', data);
        if (data.success) {
          ads = data.ads;
          data.ads.map((ad) => console.log(ad));
        }
        document.getElementById('ads').textContent = data.success;
        
      })
      .catch((error) => {
        console.error('Error sending data:', error);
      });
})();

function checkToSkipAd() {
    console.log('Checking to skip ad');
    console.log(ads);
    if (ads.length !== 0) {
        const video = document.querySelector('video');
        ads.forEach((ad) => {
            if (video.currentTime >= ad.start && video.currentTime <= ad.end) {
                skip = ad.end + 0.1 - video.currentTime;
                video.currentTime += skip;
                console.log('Ad skipped');
            }
        });
    }
}

setInterval(checkToSkipAd, 1000);