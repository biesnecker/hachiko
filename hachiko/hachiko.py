import asyncio
from watchdog.observers import Observer

EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'

class AIOEventHandler(object):
    """An asyncio-compatible event handler."""

    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def on_any_event(self, event): pass

    @asyncio.coroutine
    def on_moved(self, event): pass

    @asyncio.coroutine
    def on_created(self, event): pass

    @asyncio.coroutine
    def on_deleted(self, event): pass

    @asyncio.coroutine
    def on_modified(self, event): pass

    def dispatch(self, event):
        _method_map = {
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
        }
        handlers = [self.on_any_event, _method_map[event.event_type]]
        for handler in handlers:
            self._loop.call_soon_threadsafe(
                asyncio.async,
                handler(event))


class AIOWatchdog(object):

    def __init__(self, path='.', recursive=True, event_handler=None):
        self._observer = Observer()

        evh = event_handler or AIOEventHandler()

        self._observer.schedule(evh, path, recursive)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()

