import asyncio
import inspect
import os
import pathlib
import threading
import time

import pytest
import watchdog.observers

from hachiko import AIOEventHandler, AIOWatchdog

ALL_EVENT_TYPES = [
    "created",
    "deleted",
    "modified",
    "moved",
    "closed",
    "closed_no_write",
    "opened",
    "attrib",
]


def run(coro):
    """asyncio.run() for every Python we support (it was added in 3.7)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def wait_until(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            return False
        await asyncio.sleep(0.02)
    return True


class FakeEvent(object):
    def __init__(self, event_type, src_path="/watched/file.txt", is_directory=False):
        self.event_type = event_type
        self.src_path = src_path
        self.is_directory = is_directory


class RecordingEventHandler(AIOEventHandler):
    """Records (handler name, event) for every coroutine hachiko invokes."""

    def __init__(self, loop=None):
        AIOEventHandler.__init__(self, loop=loop)
        self.calls = []

    async def on_any_event(self, event):
        self.calls.append(("on_any_event", event))

    async def on_created(self, event):
        self.calls.append(("on_created", event))

    async def on_deleted(self, event):
        self.calls.append(("on_deleted", event))

    async def on_modified(self, event):
        self.calls.append(("on_modified", event))

    async def on_moved(self, event):
        self.calls.append(("on_moved", event))

    async def on_closed(self, event):
        self.calls.append(("on_closed", event))

    async def on_closed_no_write(self, event):
        self.calls.append(("on_closed_no_write", event))

    async def on_opened(self, event):
        self.calls.append(("on_opened", event))

    async def on_attrib(self, event):
        self.calls.append(("on_attrib", event))

    def names_for(self, event):
        return sorted(name for name, seen in self.calls if seen is event)


@pytest.mark.parametrize("event_type", ALL_EVENT_TYPES)
def test_dispatch_routes_event_to_matching_handler(event_type):
    async def scenario():
        handler = RecordingEventHandler()
        event = FakeEvent(event_type)
        handler.dispatch(event)
        assert await wait_until(lambda: len(handler.calls) == 2)
        assert handler.names_for(event) == sorted(["on_any_event", "on_" + event_type])

    run(scenario())


def test_dispatch_tolerates_event_types_from_newer_watchdog():
    async def scenario():
        handler = RecordingEventHandler()
        event = FakeEvent("some_future_event_type")
        handler.dispatch(event)  # must not raise in watchdog's observer thread
        assert await wait_until(lambda: len(handler.calls) == 1)
        assert handler.names_for(event) == ["on_any_event"]

    run(scenario())


def test_base_handler_accepts_every_event_type():
    async def scenario():
        handler = AIOEventHandler()
        for event_type in ALL_EVENT_TYPES:
            handler.dispatch(FakeEvent(event_type))
        await asyncio.sleep(0.05)

    run(scenario())


def test_dispatch_is_safe_to_call_from_observer_thread():
    async def scenario():
        handler = RecordingEventHandler()
        event = FakeEvent("created")
        thread = threading.Thread(target=handler.dispatch, args=(event,))
        thread.start()
        thread.join()
        assert await wait_until(lambda: len(handler.calls) == 2)
        assert handler.names_for(event) == ["on_any_event", "on_created"]

    run(scenario())


def test_handler_uses_explicit_loop():
    loop = asyncio.new_event_loop()
    try:
        handler = RecordingEventHandler(loop=loop)
        event = FakeEvent("deleted")
        handler.dispatch(event)
        loop.run_until_complete(
            wait_until(lambda: len(handler.calls) == 2, timeout=1.0)
        )
        assert handler.names_for(event) == ["on_any_event", "on_deleted"]
    finally:
        loop.close()


class FakeObserver(object):
    def __init__(self):
        self.scheduled = []
        self.calls = []
        self.join_thread = None

    def schedule(self, event_handler, path, recursive=False, **kwargs):
        self.scheduled.append((event_handler, path, recursive, kwargs))

    def start(self):
        self.calls.append("start")

    def stop(self):
        self.calls.append("stop")

    def join(self):
        self.calls.append("join")
        self.join_thread = threading.current_thread()


@pytest.mark.parametrize("recursive", [True, False])
def test_aiowatchdog_schedules_handler_on_observer(recursive):
    async def scenario():
        observer = FakeObserver()
        handler = AIOEventHandler()
        AIOWatchdog("/some/dir", recursive=recursive, event_handler=handler, observer=observer)
        assert observer.scheduled == [(handler, "/some/dir", recursive, {})]

    run(scenario())


def test_aiowatchdog_passes_extra_options_to_schedule():
    async def scenario():
        observer = FakeObserver()
        handler = AIOEventHandler()
        AIOWatchdog(
            "/some/dir",
            event_handler=handler,
            observer=observer,
            event_filter=["filter"],
            follow_symlink=True,
        )
        assert observer.scheduled == [
            (handler, "/some/dir", True, {"event_filter": ["filter"], "follow_symlink": True})
        ]

    run(scenario())


def test_aiowatchdog_rejects_options_watchdog_does_not_support(tmp_path):
    async def scenario():
        with pytest.raises(TypeError):
            AIOWatchdog(str(tmp_path), not_a_watchdog_option=True)

    run(scenario())


def test_async_with_starts_and_stops_observer():
    async def scenario():
        observer = FakeObserver()
        watcher = AIOWatchdog("/some/dir", observer=observer)
        async with watcher as entered:
            assert entered is watcher
            assert observer.calls == ["start"]
        assert observer.calls == ["start", "stop", "join"]

    run(scenario())


def test_async_with_stops_observer_when_body_raises():
    class Boom(Exception):
        pass

    async def scenario():
        observer = FakeObserver()
        with pytest.raises(Boom):
            async with AIOWatchdog("/some/dir", observer=observer):
                raise Boom()
        assert observer.calls == ["start", "stop", "join"]

    run(scenario())


def test_astop_waits_for_observer_without_blocking_event_loop():
    async def scenario():
        observer = FakeObserver()
        watcher = AIOWatchdog("/some/dir", observer=observer)
        watcher.start()
        await watcher.astop()
        assert observer.calls == ["start", "stop", "join"]
        # join() blocks until watchdog's thread exits, so it must not run on
        # the event loop's thread.
        assert observer.join_thread is not threading.current_thread()

    run(scenario())


def test_stop_still_blocks_until_observer_joins():
    async def scenario():
        observer = FakeObserver()
        watcher = AIOWatchdog("/some/dir", observer=observer)
        watcher.start()
        watcher.stop()
        assert observer.calls == ["start", "stop", "join"]
        assert observer.join_thread is threading.current_thread()

    run(scenario())


def test_package_ships_py_typed_marker():
    import hachiko

    # Without this marker, type checkers ignore hachiko's type hints.
    assert (pathlib.Path(hachiko.__file__).parent / "py.typed").is_file()


def test_package_exposes_version():
    import hachiko

    assert hachiko.__version__ == ".".join(str(p) for p in hachiko.__version_info__)


# Integration tests against a real watchdog observer. Watchdog may report an
# event more than once (see issue #14), so these wait for the event to show up
# rather than asserting on an exact sequence.


async def exercise_filesystem(directory, handler):
    def seen(event_type, name):
        return any(
            ev.event_type == event_type
            and os.path.basename(getattr(ev, "dest_path", "") or ev.src_path) == name
            for _, ev in handler.calls
        )

    original = os.path.join(directory, "file.txt")
    pathlib.Path(original).touch()
    assert await wait_until(lambda: seen("created", "file.txt"))

    renamed = os.path.join(directory, "new_filename.txt")
    os.rename(original, renamed)
    assert await wait_until(lambda: seen("moved", "new_filename.txt"))

    os.remove(renamed)
    assert await wait_until(lambda: seen("deleted", "new_filename.txt"))


def test_aiowatchdog_reports_filesystem_events(tmp_path):
    directory = os.path.realpath(str(tmp_path))

    async def scenario():
        handler = RecordingEventHandler()
        watcher = AIOWatchdog(directory, event_handler=handler)
        watcher.start()
        try:
            await exercise_filesystem(directory, handler)
        finally:
            watcher.stop()

    run(scenario())


def test_handler_works_with_plain_watchdog_observer(tmp_path):
    directory = os.path.realpath(str(tmp_path))

    async def scenario():
        handler = RecordingEventHandler()
        observer = watchdog.observers.Observer()
        observer.schedule(handler, directory, recursive=True)
        observer.start()
        try:
            await exercise_filesystem(directory, handler)
        finally:
            observer.stop()
            observer.join()

    run(scenario())


def test_async_with_aiowatchdog_reports_filesystem_events(tmp_path):
    directory = os.path.realpath(str(tmp_path))

    async def scenario():
        handler = RecordingEventHandler()
        async with AIOWatchdog(directory, event_handler=handler):
            await exercise_filesystem(directory, handler)

    run(scenario())


def watchdog_supports(option):
    params = inspect.signature(watchdog.observers.Observer().schedule).parameters
    return option in params


@pytest.mark.skipif(
    not watchdog_supports("event_filter"), reason="event_filter needs watchdog 4+"
)
def test_event_filter_option_reaches_watchdog(tmp_path):
    from watchdog.events import FileCreatedEvent

    directory = os.path.realpath(str(tmp_path))

    async def scenario():
        handler = RecordingEventHandler()
        async with AIOWatchdog(
            directory, event_handler=handler, event_filter=[FileCreatedEvent]
        ):
            path = os.path.join(directory, "file.txt")
            pathlib.Path(path).touch()
            assert await wait_until(lambda: handler.calls)
            os.remove(path)
            await asyncio.sleep(0.5)
        assert {ev.event_type for _, ev in handler.calls} == {"created"}

    run(scenario())
