import asyncio
from types import TracebackType
from typing import Any, Callable, Coroutine, Dict, Optional, Set, Type, TypeVar, cast

from watchdog.events import FileSystemEvent
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

# Type hints use the typing module (not `X | None`) and quote anything not
# subscriptable at runtime, so this still imports on Python 3.6.
_Handler = Callable[[FileSystemEvent], Coroutine[Any, Any, None]]
_W = TypeVar("_W", bound="AIOWatchdog")

EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"
EVENT_TYPE_CLOSED = "closed"
EVENT_TYPE_OPENED = "opened"
EVENT_TYPE_CLOSED_NO_WRITE = "closed_no_write"
EVENT_TYPE_ATTRIB = "attrib"


class AIOEventHandler(object):
    """An asyncio-compatible event handler."""

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._ensure_future: "Callable[[Coroutine[Any, Any, None]], asyncio.Future[None]]"
        # prefer asyncio.create_task starting from Python 3.7
        if hasattr(asyncio, "create_task"):
            self._ensure_future = asyncio.create_task
        else:
            self._ensure_future = asyncio.ensure_future
        # The event loop only keeps weak references to tasks, so hold on to
        # them here until they finish or they may be garbage collected.
        self._tasks: "Set[asyncio.Future[None]]" = set()
        self._method_map: Dict[str, _Handler] = {
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
            EVENT_TYPE_CLOSED: self.on_closed,
            EVENT_TYPE_OPENED: self.on_opened,
            EVENT_TYPE_CLOSED_NO_WRITE: self.on_closed_no_write,
            EVENT_TYPE_ATTRIB: self.on_attrib,
        }

    async def on_any_event(self, event: FileSystemEvent) -> None:
        pass

    async def on_moved(self, event: FileSystemEvent) -> None:
        pass

    async def on_created(self, event: FileSystemEvent) -> None:
        pass

    async def on_deleted(self, event: FileSystemEvent) -> None:
        pass

    async def on_modified(self, event: FileSystemEvent) -> None:
        pass

    async def on_closed(self, event: FileSystemEvent) -> None:
        pass

    async def on_opened(self, event: FileSystemEvent) -> None:
        pass

    async def on_closed_no_write(self, event: FileSystemEvent) -> None:
        pass

    async def on_attrib(self, event: FileSystemEvent) -> None:
        pass

    def dispatch(self, event: FileSystemEvent) -> None:
        # Called from watchdog's observer thread. Event types this class
        # doesn't know about (e.g. ones added in a newer watchdog) still go
        # to on_any_event rather than raising and killing that thread.
        self._loop.call_soon_threadsafe(self._spawn, self.on_any_event(event))
        handler = self._method_map.get(event.event_type)
        if handler is not None:
            self._loop.call_soon_threadsafe(self._spawn, handler(event))

    def _spawn(self, coro: Coroutine[Any, Any, None]) -> None:
        task = self._ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)


class AIOWatchdog(object):
    def __init__(
        self,
        path: str = ".",
        recursive: bool = True,
        event_handler: Optional[AIOEventHandler] = None,
        observer: Optional[BaseObserver] = None,
        **schedule_kwargs: Any
    ) -> None:
        self._observer: BaseObserver
        if observer is None:
            self._observer = Observer()
        else:
            self._observer = observer

        evh = event_handler or AIOEventHandler()

        # Extra keyword arguments (e.g. event_filter, follow_symlink) go
        # straight to watchdog, so whatever the installed version supports
        # works here, and anything it doesn't raises TypeError.
        # watchdog only ever calls dispatch(), so AIOEventHandler doesn't
        # subclass its FileSystemEventHandler; cast for its type hints.
        self._observer.schedule(
            cast(Any, evh), path=path, recursive=recursive, **schedule_kwargs
        )

    def start(self) -> None:
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()

    async def astop(self) -> None:
        """Like stop(), but waits for the observer thread without blocking the event loop."""
        self._observer.stop()
        await asyncio.get_event_loop().run_in_executor(None, self._observer.join)

    async def __aenter__(self: _W) -> _W:
        self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.astop()
