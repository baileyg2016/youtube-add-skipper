Goal is to create a chrome extension that will skip youtube ads in video based on the transcript of the video.

okay plan, need to use download transcript with youtube-dl and transcribe with whisper. Then combine the two and use the timestamps to skip the ads because whisper transcription is so much better.

example execution:
```python engine.py https://www.youtube.com/watch\?v\=Q_1Bco0AkcM```

no ads: ```python engin.py https://www.youtube.com/watch?v=Q_1Bco0AkcM```
ads: ```python engine.py https://www.youtube.com/watch?v=xZDqVubBZZg&t=2392s&ab_channel=ThisWeekinStartups```

note to bailey: use chess env