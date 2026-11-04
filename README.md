# Hachiko

[![CI](https://github.com/biesnecker/hachiko/actions/workflows/ci.yml/badge.svg)](https://github.com/biesnecker/hachiko/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hachiko)](https://pypi.org/project/hachiko/)

An extremely simple asyncio-based wrapper around [Watchdog](https://github.com/gorakhargosh/watchdog).

```
pip install hachiko
```

Hachiko supports Python 3.6 and newer, and watchdog 2.1.6 and newer (including
watchdog 7). CI tests that whole range.

Hachiko includes type hints, so type checkers such as mypy check your handlers
against its API.

### Example usage

You need to subclass `AIOEventHandler` and either:

1. Use it directly with a Watchdog `Observer` object, or;
2. Pass it to `AIOWatchdog` and use it there.

```python
import asyncio

from hachiko import AIOEventHandler, AIOWatchdog

WATCH_DIRECTORY = "/path/to/watch/directory/"


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
    async with AIOWatchdog(watch_dir, event_handler=evh):
        await asyncio.sleep(20)  # events are handled while this runs


asyncio.run(watch_fs(WATCH_DIRECTORY))
```

On Python 3.6, which has no `asyncio.run()`, use
`asyncio.get_event_loop().run_until_complete(watch_fs(WATCH_DIRECTORY))`.

Create your handler while the event loop is running (as above), or pass the
loop explicitly with `MyEventHandler(loop=loop)`.

### Starting and stopping

`async with AIOWatchdog(...)` starts watching on entry and stops on exit, even
if the body raises. You can also manage it yourself:

- `watch.start()` starts watching.
- `await watch.astop()` stops watching and waits for watchdog's thread to
  finish without blocking the event loop.
- `watch.stop()` does the same but blocks the event loop while it waits.

### Watch options

`AIOWatchdog(path, recursive=True, event_handler=None, observer=None, **options)`

- `path` can be a directory or, with watchdog 7+, a single file.
- Any extra keyword `options` are passed to watchdog's `Observer.schedule()`,
  so you can use whatever your installed watchdog supports. If it doesn't
  support an option, you get a `TypeError`. Useful ones:
  - `event_filter=[FileCreatedEvent, FileDeletedEvent]` (watchdog 4+) only
    delivers those event classes, from `watchdog.events`.
  - `follow_symlink=True` (watchdog 7+) follows symbolic links.
- `observer` lets you supply your own watchdog observer, e.g.
  `PollingObserver()` for network filesystems. On macOS with watchdog 7+,
  `FSEventsObserver(latency=0.5)` (from `watchdog.observers.fsevents`) merges
  rapid repeated events into one.

### Events

Override any of these coroutines. Each receives the watchdog event object.

| Handler | Called for | Notes |
| --- | --- | --- |
| `on_any_event` | every event | Also called for event types hachiko doesn't know about yet |
| `on_created` | file or directory created | |
| `on_deleted` | file or directory deleted | |
| `on_modified` | file or directory modified | |
| `on_moved` | file or directory moved/renamed | `event.dest_path` is the new path |
| `on_closed` | file closed after writing | Linux only |
| `on_closed_no_write` | file closed without writing | Linux only, watchdog 5+ |
| `on_opened` | file opened | Linux only, watchdog 2.3+ |
| `on_attrib` | metadata changed (permissions, timestamps…) | watchdog 7+; older versions report these as `on_modified` |

Watchdog sometimes reports the same change more than once, so handlers should
be safe to run repeatedly for the same path.
