import asyncio
from watchdog.observers import Observer

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

    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        # prefer asyncio.create_task starting from Python 3.7
        if hasattr(asyncio, "create_task"):
            self._ensure_future = asyncio.create_task
        else:
            self._ensure_future = asyncio.ensure_future
        # The event loop only keeps weak references to tasks, so hold on to
        # them here until they finish or they may be garbage collected.
        self._tasks = set()
        self._method_map = {
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
            EVENT_TYPE_CLOSED: self.on_closed,
            EVENT_TYPE_OPENED: self.on_opened,
            EVENT_TYPE_CLOSED_NO_WRITE: self.on_closed_no_write,
            EVENT_TYPE_ATTRIB: self.on_attrib,
        }

    async def on_any_event(self, event):
        pass

    async def on_moved(self, event):
        pass

    async def on_created(self, event):
        pass

    async def on_deleted(self, event):
        pass

    async def on_modified(self, event):
        pass

    async def on_closed(self, event):
        pass

    async def on_opened(self, event):
        pass

    async def on_closed_no_write(self, event):
        pass

    async def on_attrib(self, event):
        pass

    def dispatch(self, event):
        # Called from watchdog's observer thread. Event types this class
        # doesn't know about (e.g. ones added in a newer watchdog) still go
        # to on_any_event rather than raising and killing that thread.
        self._loop.call_soon_threadsafe(self._spawn, self.on_any_event(event))
        handler = self._method_map.get(event.event_type)
        if handler is not None:
            self._loop.call_soon_threadsafe(self._spawn, handler(event))

    def _spawn(self, coro):
        task = self._ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)


class AIOWatchdog(object):
    def __init__(self, path=".", recursive=True, event_handler=None, observer=None):
        if observer is None:
            self._observer = Observer()
        else:
            self._observer = observer

        evh = event_handler or AIOEventHandler()

        self._observer.schedule(evh, path=path, recursive=recursive)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()
