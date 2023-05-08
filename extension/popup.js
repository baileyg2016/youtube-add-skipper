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

function updateTimestamp() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { message: 'getTimestamp' }, (response) => {
        if (response && response.success) {
            document.getElementById('timestamp').textContent = response.timestamp.toFixed(2);
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
        })
        .catch((error) => {
          console.error('Error sending data:', error);
        });
  
      updateTimestamp();
    });
});