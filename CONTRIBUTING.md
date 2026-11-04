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

1. Bump `__version__` in `hachiko/version.py`.
2. In `CHANGELOG.md`, change that version's heading from `(unreleased)` to
   the release date, e.g. `## 1.2.3 (2027-01-31)`.
3. Merge to `master`.
4. Tag that commit and push the tag:

   ```
   git tag v1.2.3
   git push origin v1.2.3
   ```

The release workflow (`.github/workflows/release.yml`) then:

- checks the tag matches the version, is on `master`, and has a dated
  changelog entry;
- runs the full CI matrix on the tagged commit;
- publishes the built distributions to PyPI;
- creates the GitHub release, using the changelog section as its notes.

Nothing is published if any check or test fails. Fix the problem, delete the
tag (`git push --delete origin v1.2.3 && git tag -d v1.2.3`) and tag again.
Once a version is on PyPI it can't be re-uploaded, so a broken release needs
a new version number.

### PyPI setup

The workflow uses
[trusted publishing](https://docs.pypi.org/trusted-publishers/), so there is
no API token to manage. PyPI is configured to trust:

- Owner: `biesnecker`
- Repository: `hachiko`
- Workflow: `release.yml`
- Environment: `pypi`

The `pypi` environment in the repository settings only allows deployments from
`v*` tags. If the workflow file or environment is renamed, update the
publisher at <https://pypi.org/manage/project/hachiko/settings/publishing/>.
