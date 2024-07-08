import os
import cv2
import time
import numpy as np
import subprocess
import logging
from multiprocessing import SimpleQueue, Process
from datetime import datetime
from mss.linux import MSS as mss
from window_recorder import cfg
from typing import Iterable, AnyStr

logger = logging.getLogger(__name__)


def _record_loop(q: SimpleQueue, filename, monitor, frame_rate):
    with mss() as sct:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # adjust monitor to crop out the parts not visible
        if monitor['left'] < 0:
            monitor['width'] += monitor['left']
            monitor['left'] = 0
        if monitor['top'] < 0:
            monitor['height'] += monitor['top']
            monitor['top'] = 0
        monitor['height'] = min(monitor['height'], sct.monitors[0]['height'] - monitor['top'])
        monitor['width'] = min(monitor['width'], sct.monitors[0]['width'] - monitor['left'])
        out = cv2.VideoWriter(filename, fourcc, frame_rate, (monitor['width'], monitor['height']))
        period = 1. / frame_rate
        while q.empty():
            start_time = time.time()

            img = np.array(sct.grab(monitor))
            out.write(img[:, :, :3])

            # wait for frame rate time
            elapsed = time.time() - start_time
            if elapsed < period:
                time.sleep(period - elapsed)
        out.release()


class WindowRecorder:
    """Programatically video record a window in Linux (requires xwininfo)"""

    def __init__(self, window_names: Iterable[AnyStr] = None, frame_rate=30.0, name_suffix="", save_dir=None,
                 record=True):
        self.record = record
        if not self.record:
            return
        if window_names is None:
            logger.info("Select a window to record by left clicking with your mouse")
            output = subprocess.check_output(["xwininfo"], universal_newlines=True)
            logger.info(f"Selected {output}")
        else:
            for name in window_names:
                try:
                    output = subprocess.check_output(["xwininfo", "-name", name], universal_newlines=True)
                    break
                except subprocess.CalledProcessError as e:
                    logger.debug(f"Could not find window named {name}, trying next in list")
                    pass
            else:
                raise RuntimeError(f"Could not find any windows with names from {window_names}")

        properties = {}
        for line in output.split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                properties[parts[0].strip()] = parts[1].strip()

        left, top = int(properties["Absolute upper-left X"]), int(properties["Absolute upper-left Y"])
        width, height = int(properties["Width"]), int(properties["Height"])

        self.monitor = {"top": top, "left": left, "width": width, "height": height}
        self.frame_rate = frame_rate
        self.suffix = name_suffix
        self.save_dir = save_dir
        if self.save_dir is None:
            self.save_dir = cfg.CAPTURE_DIR

    def __enter__(self):
        if not self.record:
            return self
        os.makedirs(self.save_dir, exist_ok=True)
        output = os.path.join(self.save_dir,
                              f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_{self.suffix}.mp4")
        logger.debug(f"Recording video to {output}")
        self.q = SimpleQueue()
        self.record_process = Process(target=_record_loop,
                                      args=(self.q, output, self.monitor, self.frame_rate))
        self.record_process.start()
        return self

    def __exit__(self, *args):
        if not self.record:
            return
        self.q.put('die')
        self.record_process.join()
        cv2.destroyAllWindows()
