import asyncio
from hachiko.hachiko import AIOWatchdog


async def watch_fs():
    watch = AIOWatchdog('/home/genevieve/Documents/Projects/watchdir/code/data/watch_dir/')
    watch.start()
    for _ in range(20):
        await asyncio.sleep(1)
    watch.stop()

asyncio.get_event_loop().run_until_complete(watch_fs())

