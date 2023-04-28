Goal is to create a chrome extension that will skip youtube ads in video based on the transcript of the video.

Current bug is that there the code perpetually chunks the audio :/ 

example execution:
```python engine.py https://www.youtube.com/watch\?v\=Q_1Bco0AkcM```

no ads: https://www.youtube.com/watch?v=Q_1Bco0AkcM
ads: https://www.youtube.com/watch?v=xZDqVubBZZg&t=2392s&ab_channel=ThisWeekinStartups

note to bailey: use chess env