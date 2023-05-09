function loadYouTubeAPI() {
  const script = document.createElement('script');
  script.src = 'https://www.youtube.com/iframe_api';
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
}

loadYouTubeAPI();

let player;

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
  // ...
}
