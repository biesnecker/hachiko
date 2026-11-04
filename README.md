# Hachiko

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/biesnecker/hachiko/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/biesnecker/hachiko/tree/master)

An extremely simple asyncio-based wrapper around [Watchdog](https://github.com/gorakhargosh/watchdog). [Get it on PyPI](https://pypi.org/project/hachiko/).

### Example usage

You need to subclass AIOEventHandler and either:

1. Use it directly with a Watchdog `Observer` object, or;
2. Pass it to `AIOWatchdog` and use it there.

```python
import asyncio
from hachiko.hachiko import AIOWatchdog, AIOEventHandler

WATCH_DIRECTORY = '/path/to/watch/directory/'


class MyEventHandler(AIOEventHandler):
    """Subclass of asyncio-compatible event handler."""
    async def on_created(self, event):
        print('Created:', event.src_path)  # add your functionality here

    async def on_deleted(self, event):
        print('Deleted:', event.src_path)  # add your functionality here

    async def on_moved(self, event):
        print('Moved:', event.src_path)  # add your functionality here

    async def on_modified(self, event):
        print('Modified:', event.src_path)  # add your functionality here

    async def on_closed(self, event):
        print('Closed:', event.src_path)  # add your functionality here

    async def on_opened(self, event):
        print('Opened:', event.src_path)  # add your functionality here


async def watch_fs(watch_dir):
    evh = MyEventHandler()
    watch = AIOWatchdog(watch_dir, event_handler=evh)
    watch.start()
    for _ in range(20):
        await asyncio.sleep(1)
    watch.stop()


asyncio.get_event_loop().run_until_complete(watch_fs(WATCH_DIRECTORY))
```
