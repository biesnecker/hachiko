# Contributing

## Development

```
uv run pytest                        # newest watchdog on the default Python
uv run --python 3.8 pytest           # a specific Python
```

CI (`.github/workflows/ci.yml`) runs the full matrix of Python versions,
watchdog versions and operating systems on every push and pull request, and
weekly against the newest watchdog to catch upstream changes.

## Releasing

1. Bump `__version__` in `hachiko/version.py` and move the `CHANGELOG.md`
   entries under the new version.
2. Merge to `master` and wait for CI to pass.
3. Create a GitHub release with tag `vX.Y.Z` (matching the version). The
   release workflow builds and uploads it to PyPI.

### One-time PyPI setup

The release workflow uses
[trusted publishing](https://docs.pypi.org/trusted-publishers/), so there is no
API token to manage. Before the first release, add a publisher on
<https://pypi.org/manage/project/hachiko/settings/publishing/> with:

- Owner: `biesnecker`
- Repository: `hachiko`
- Workflow: `release.yml`
- Environment: `pypi`
