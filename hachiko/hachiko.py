import asyncio
from watchdog.observers import Observer

EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"


class AIOEventHandler(object):
    """An asyncio-compatible event handler."""

    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        # prefer asyncio.create_task starting from Python 3.7
        if hasattr(asyncio, "create_task"):
            self._ensure_future = asyncio.create_task
        else:
            self._ensure_future = asyncio.ensure_future
        self._method_map = {
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
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

    def dispatch(self, event):
        handler = self._method_map[event.event_type]
        self._loop.call_soon_threadsafe(self._ensure_future, self.on_any_event(event))
        self._loop.call_soon_threadsafe(self._ensure_future, handler(event))


class AIOWatchdog(object):
    def __init__(self, path=".", recursive=True, event_handler=None, observer=None):
        if observer is None:
            self._observer = Observer()
        else:
            self._observer = observer

        evh = event_handler or AIOEventHandler()

        self._observer.schedule(evh, path, recursive)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()
