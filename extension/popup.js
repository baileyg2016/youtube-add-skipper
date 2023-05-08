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
console.log('popup.js loaded')