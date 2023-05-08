let player;
let ads = []; // Add this line to store the ads information

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

function onYouTubeIframeAPIReady() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const videoId = new URL(tabs[0].url).searchParams.get('v');
    
        player = new YT.Player('player', {
            height: '0',
            width: '0',
            videoId,
            events: {
            onReady: onPlayerReady,
            },
        });
    });
}

function onPlayerReady(event) {
    updateTimestamp();
}

// function updateTimestamp() {
//     chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
//         chrome.tabs.sendMessage(tabs[0].id, { message: 'getTimestamp' }, (response) => {
//             if (response && response.success) {
//                 document.getElementById('timestamp').textContent = response.timestamp.toFixed(2);
//             } else {
//                 document.getElementById('timestamp').textContent = 'N/A';
//             }
//         });
//     });
// }

function updateTimestamp() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { message: 'getTimestamp' }, (response) => {
            if (response && response.success) {
                const currentTime = response.timestamp.toFixed(2);
                document.getElementById('timestamp').textContent = currentTime;

                // Check if the current timestamp is within an ad segment and skip it
                ads.forEach((ad) => {
                    if (currentTime >= ad.start && currentTime <= ad.end) {
                        player.seekTo(ad.end + 0.1, true);
                    }
                });
            } else {
                document.getElementById('timestamp').textContent = 'N/A';
            }
        });
    });
}

setInterval(updateTimestamp, 1000);
console.log('popup.js loaded');

document.addEventListener('DOMContentLoaded', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      // Send the YouTube URL as data
      postData('http://localhost:8080/', { youtube_url: tabs[0].url })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            return response.json();
        })
        .then((data) => {
            console.log('Data sent successfully:', data);
            if (data.success) {
                ads = data.ads; // Store the ads information
                data.ads.map((ad) => console.log(ad));
            }
            document.getElementById('ads').textContent = data.success;
        })
        .catch((error) => {
            console.error('Error sending data:', error);
        });
  
        updateTimestamp();
    });
});

// document.addEventListener('DOMContentLoaded', () => {
//     chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
//       // Send the YouTube URL as data
//       postData('http://localhost:8080/', { youtube_url: tabs[0].url })
//         .then((response) => {
//           if (!response.ok) {
//             throw new Error('Network response was not ok');
//           }
//           print(response);
//           return response.json();
//         })
//         .then((data) => {
//           console.log('Data sent successfully:', data);
//           if (data.success) {
//             data.ads.map((ad) => console.log(ad));
//           }
//           document.getElementById('ads').textContent = data.success; // JSON.parse(data);
//         })
//         .catch((error) => {
//           console.error('Error sending data:', error);
//         });
  
//       updateTimestamp();
//     });
// });