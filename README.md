## Installation
This only works on Linux systems. You should have `xwininfo` installed by default.

```shell
pip install window-recorder
```

If the above does not work (OpenCV can be finicky), then you can install the dependencies manually.
Install `opencv` and `mss` as dependencies (recommended with conda):
```
conda install opencv
conda install -c conda-forge python-mss
```
Then clone this repository anywhere and install locally with
```
pip install -e .
```

## Usage
The `WindowRecorder` class comes as a context manager.
You pass in a list of window names to record and it will try to find them
in the order given, recording the first one with a valid window configuration.
If you pass in None as the first argument, then instead it will prompt you
to click on a window (cursor turns into a cross and blocks until you click).

The video will start and end recording according to the life cycle of the
context manager.

```python
from window_recorder import WindowRecorder
import time

# passing in nothing as the window name will allow you to select the window by clicking
# want to capture an RViz window, which could have name "RViz*" as well
with WindowRecorder(["RViz*", "RViz"], frame_rate=30.0, name_suffix="rviz"):
    # do things...
    time.sleep(0.1)
    start = time.time()
    while time.time() - start < 2:
        time.sleep(0.1)
```

You can test it out with `scripts/text.py` which will prompt you to
click a window that it will then record for 2 seconds
(see the log for the default location the video will be saved to)

To not record, a `record=False` argument can be passed to the constructor for better convenience than unindenting the block
and not using the context manager.
```python
from window_recorder import WindowRecorder
import time
with WindowRecorder(["RViz*", "RViz"], frame_rate=30.0, name_suffix="rviz", record=False):
    # will not record; the arguments above also won't be checked and you won't be asked to click a window
    time.sleep(0.1)
    start = time.time()
    while time.time() - start < 2:
        time.sleep(0.1)
```

### Limitations
The original location of the window will be what is actually recorded,
so if you move the window during the recording or another window comes
in front of it, that will also be recorded.
