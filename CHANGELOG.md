# Changelog

## 0.5.0 (2026-11-04)

### Fixed

- `AIOWatchdog` failed with `TypeError` on watchdog 5 and newer, because it
  passed `recursive` to `Observer.schedule()` positionally (#19, thanks
  @claudiopastorini).
- With watchdog 7, metadata changes (including a plain `touch`) raised
  `KeyError: 'attrib'` in watchdog's observer thread, which stopped all
  further events. Unknown event types now go to `on_any_event` instead of
  raising.
- `on_opened` events (watchdog 2.3+) are now handled instead of raising
  `KeyError: 'opened'` on Linux (#15, thanks @Restitutor).
  This fix was merged after 0.4.0 but never released (#18).
- Handler tasks are now kept referenced until they finish, so the event loop
  can't garbage-collect them mid-run.
- Fixed a broken string literal in the README example (#17, thanks @nakidai).

### Added

- `on_closed_no_write` (watchdog 5+) and `on_attrib` (watchdog 7+) handlers.
- `AIOEventHandler` and `AIOWatchdog` can be imported directly from
  `hachiko`. `from hachiko.hachiko import ...` still works.

### Changed

- Declares its supported range for the first time: Python >= 3.6 and
  watchdog >= 2.1.6, the versions hachiko 0.4.0 was released against. CI
  covers Python 3.6–3.14 and watchdog 2.1.6–7.0 on Linux, macOS and Windows.
- Packaging moved from `setup.py`/distutils (removed in Python 3.12) to
  `pyproject.toml`. Wheels are now published alongside the sdist.
- Tests are no longer installed as part of the package.

## 0.4.0 (2021-11-17)

- Handle `closed` events (#11).
