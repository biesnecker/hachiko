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

