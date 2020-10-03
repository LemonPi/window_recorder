from window_recorder.recorder import WindowRecorder
import time
import logging

ch = logging.StreamHandler()

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s %(asctime)s %(pathname)s:%(lineno)d] %(message)s',
                    datefmt='%m-%d %H:%M:%S', handlers=[ch])


with WindowRecorder():
    start = time.time()
    i = 1
    while time.time() - start < 2:
        i += 1
        time.sleep(0.1)
