import asyncio
import sys

from hachiko import AIOEventHandler, AIOWatchdog

WATCH_DIRECTORY = sys.argv[1] if len(sys.argv) > 1 else "."


class MyEventHandler(AIOEventHandler):
    """Subclass of asyncio-compatible event handler."""

    async def on_created(self, event):
        print("Created:", event.src_path)  # add your functionality here

    async def on_deleted(self, event):
        print("Deleted:", event.src_path)  # add your functionality here

    async def on_moved(self, event):
        print("Moved:", event.src_path, "->", event.dest_path)

    async def on_modified(self, event):
        print("Modified:", event.src_path)  # add your functionality here


async def watch_fs(watch_dir):
    evh = MyEventHandler()  # create handlers inside a running event loop
    watch = AIOWatchdog(watch_dir, event_handler=evh)
    watch.start()
    for _ in range(20):
        await asyncio.sleep(1)
    watch.stop()


asyncio.run(watch_fs(WATCH_DIRECTORY))
