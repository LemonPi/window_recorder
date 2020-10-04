## Installation
This only works on Linux systems. You should have `xwininfo` installed by default.
Install `opencv` and `mss` as dependencies (recommended with conda):
```
conda install opencv
conda install -c conda-forge mss
```
Then clone this repository anywhere and install locally with
```
pip install -e .
```

## Usage
The `WindowRecorder` class comes as a context manager.
You pass in a list of window names to record and it will try to find them
in the order given, recording the first one with a valid window configuration.

The video will start and end recording according to the life cycle of the
context manager.

```python
from window_recorder.recorder import WindowRecorder
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
