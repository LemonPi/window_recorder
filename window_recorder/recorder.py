from mss.linux import MSS as mss
import cv2
import time
import numpy as np
import subprocess
import logging
from multiprocessing import SimpleQueue, Process
from datetime import datetime


def _record_loop(q: SimpleQueue, filename, monitor, frame_rate):
    with mss() as sct:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, frame_rate, (monitor['width'], monitor['height']))
        period = 1. / frame_rate
        while q.empty():
            start_time = time.time()

            img = np.array(sct.grab(monitor))
            out.write(img[:, :, :3])

            # wait for frame rate time
            elapsed = time.time() - start_time
            if elapsed < period:
                time.sleep(period - elapsed - 0.0002)
        out.release()


class WindowRecorder:
    """Programatically video record a window in Linux (requires xwininfo)"""

    def __init__(self, window_names=("RViz*", "RViz"), frame_rate=30.0, name_suffix=""):
        for name in window_names:
            try:
                output = subprocess.check_output(["xwininfo", "-name", name], universal_newlines=True)
                break
            except subprocess.CalledProcessError as e:
                logging.debug("Could not find window named {}, trying next in list".format(name))
                pass
        else:
            raise RuntimeError("Could not find any windows with names from {}".format(window_names))

        properties = {}
        for line in output.split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                properties[parts[0].strip()] = parts[1].strip()

        top, left = int(properties["Absolute upper-left X"]), int(properties["Absolute upper-left Y"])
        width, height = int(properties["Width"]), int(properties["Height"])
        # seems to need a little offset to avoid capturing background
        left += 2

        self.monitor = {"top": top, "left": left, "width": width, "height": height}
        self.frame_rate = frame_rate
        self.suffix = name_suffix

    def __enter__(self):
        output = "{}_{}.mp4".format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'), self.suffix)
        self.q = SimpleQueue()
        self.record_process = Process(target=_record_loop,
                                      args=(self.q, output, self.monitor, self.frame_rate))
        self.record_process.start()
        return self

    def __exit__(self, *args):
        self.q.put('die')
        self.record_process.join()
        cv2.destroyAllWindows()
