# Hachiko

An extremely simple asyncio-based wrapper around [Watchdog](https://github.com/gorakhargosh/watchdog).

### Example usage

You need to subclass AIOEventHandler and either:

1. Use it directly with a Watchdog ``Observer`` object, or;
2. Pass it to ``AIOWatchdog`` and use it there.

```python
import asyncio
from hachiko.hachiko import AIOWatchdog

@asyncio.coroutine
def watch_fs():
    watch = AIOWatchdog('/Users/jbiesnecker/temp/forks/test')
    watch.start()
    for _ in range(20):
        yield from asyncio.sleep(1)
    watch.stop()

asyncio.get_event_loop().run_until_complete(watch_fs())
```