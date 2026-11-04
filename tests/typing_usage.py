"""Type-checked by CI with `mypy --strict`, not run by pytest.

Exercises hachiko's public API the way a typed downstream project would, so
missing or wrong type hints fail CI.
"""

import asyncio
from typing import List, Optional

from watchdog.events import FileSystemEvent, FileCreatedEvent
from watchdog.observers.polling import PollingObserver

import hachiko
from hachiko import AIOEventHandler, AIOWatchdog
from hachiko.hachiko import AIOEventHandler as AIOEventHandlerFromModule


class Recorder(AIOEventHandler):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        super().__init__(loop=loop)
        self.paths: List[str] = []

    async def on_created(self, event: FileSystemEvent) -> None:
        self.paths.append(str(event.src_path))

    async def on_attrib(self, event: FileSystemEvent) -> None:
        await super().on_attrib(event)


class MyWatchdog(AIOWatchdog):
    pass


async def main() -> None:
    handler = Recorder()
    handler.dispatch(FileCreatedEvent("/tmp/x"))

    watcher = AIOWatchdog(".", recursive=False, event_handler=handler)
    watcher.start()
    watcher.stop()
    await watcher.astop()

    async with MyWatchdog(".", observer=PollingObserver(), event_filter=[FileCreatedEvent]) as w:
        mine: MyWatchdog = w  # __aenter__ returns the subclass type
        del mine

    version: str = hachiko.__version__
    info = hachiko.__version_info__
    major: int = info[0]
    del version, major

    other: AIOEventHandler = AIOEventHandlerFromModule()
    del other
