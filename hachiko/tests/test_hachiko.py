import asyncio
import os
import pathlib

import watchdog.observers

from hachiko.hachiko import AIOWatchdog, AIOEventHandler


class SubclassEventHandler(AIOEventHandler):
    """An asyncio-compatible event handler."""

    def __init__(self, loop=None):
        AIOEventHandler.__init__(self, loop=loop)

    async def on_moved(self, event): print('File moved!')

    async def on_created(self, event): print('File created!')

    async def on_deleted(self, event): print('File deleted!')


async def check_output_is_expected(directory, capsys):
    """Create, move, and delete a file."""
    # Create file
    original_filename = os.path.join(directory, 'file.txt')
    pathlib.Path(original_filename).touch()
    await asyncio.sleep(0.1)  # force release to stdout
    captured = capsys.readouterr()
    assert captured.out == 'File created!\n'
    # Move file
    new_filename = os.path.join(directory, 'new_filename.txt')
    os.rename(original_filename, new_filename)
    await asyncio.sleep(0.1)  # force release to stdout
    captured = capsys.readouterr()
    assert captured.out == 'File moved!\n'
    # Delete file
    os.remove(new_filename)
    await asyncio.sleep(0.1)  # force release to stdout
    captured = capsys.readouterr()
    assert captured.out == 'File deleted!\n'


def test_hachiko_aiowatchdog(tmpdir, capsys):
    """Test hachiko AIOWatchdog watcher."""
    WATCH_DIRECTORY = str(tmpdir)
    async def watch_fs():
        event_handler = SubclassEventHandler()  # hachinko style event handler
        watcher = AIOWatchdog(WATCH_DIRECTORY, event_handler=event_handler)
        watcher.start()
        await check_output_is_expected(WATCH_DIRECTORY, capsys)
        # Stop the directory watcher
        watcher.stop()
    # Start the event loop
    asyncio.get_event_loop().run_until_complete(watch_fs())


def test_hachiko_with_watchdog(tmpdir, capsys):
    """Test hachiko with a regular watchdog observer."""
    WATCH_DIRECTORY = str(tmpdir)
    async def watch_fs():
        event_handler = SubclassEventHandler()  # hachinko style event handler
        observer = watchdog.observers.Observer()  # a regular watchdog observer
        observer.schedule(event_handler, WATCH_DIRECTORY, recursive=True)
        observer.start()
        await check_output_is_expected(WATCH_DIRECTORY, capsys)
        # Stop the directory watcher
        observer.stop()
    # Start the event loop
    asyncio.get_event_loop().run_until_complete(watch_fs())