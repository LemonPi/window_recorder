from window_recorder.recorder import WindowRecorder
import time

with WindowRecorder():
    start = time.time()
    i = 1
    while time.time() - start < 4:
        i += 1
        time.sleep(0.1)
