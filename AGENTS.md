# AGENTS.md

Guidance for AI coding agents working in this repository. Human contributors
should read [CONTRIBUTING.md](CONTRIBUTING.md), which covers the same release
process in less detail.

## Repository basics

- `hachiko/hachiko.py` is the whole library; the version lives in
  `hachiko/version.py`; tests are in `tests/`.
- Run tests with `uv run pytest` (add `--python 3.8` etc. for other versions).
- Supported range: Python >= 3.6 and watchdog >= 2.1.6. Don't use APIs newer
  than Python 3.6 in the library or tests (no `asyncio.run`,
  `asyncio.get_running_loop`, or unguarded `asyncio.create_task`), and don't
  raise either floor without the maintainer's agreement.
- `uv.lock` is deliberately not committed, so CI always tests the newest
  watchdog.

## Release workflow

Releases are fully automated from a git tag. Pushing a tag named `vX.Y.Z`
runs `.github/workflows/release.yml`, which:

1. **check:** runs `.github/scripts/check-release.sh <tag>`, which requires:
   - the tag to equal `v` + `__version__` from `hachiko/version.py`;
   - the tagged commit to be on `master`;
   - `CHANGELOG.md` to have a `## X.Y.Z (YYYY-MM-DD)` heading that isn't
     marked `unreleased`.
2. **ci:** runs the full test matrix by calling `ci.yml` as a reusable
   workflow. Its `build` job produces the `dist` artifact.
3. **publish:** uploads that `dist` artifact to PyPI from the `pypi`
   environment via trusted publishing (OIDC). No API token or secret exists.
4. **github-release:** creates the GitHub release for the tag, with notes from
   `.github/scripts/release-notes.sh X.Y.Z` (that version's changelog
   section).

Each job needs the previous one to succeed, so if anything fails before step
3, nothing is published.

### Preparing a release

Agents may prepare a release:

1. Bump `__version__` in `hachiko/version.py`.
2. Change the version's `CHANGELOG.md` heading from `(unreleased)` to today's
   date. Entries use `### Fixed` / `### Added` / `### Changed` subsections.
3. Check locally: `.github/scripts/check-release.sh vX.Y.Z` must print
   `Releasing hachiko X.Y.Z`, and `.github/scripts/release-notes.sh X.Y.Z`
   should print the intended notes.
4. Open a PR and get it merged.

### Publishing: get explicit approval first

**Never push a `v*` tag, create a GitHub release, or run `uv publish` /
`twine upload` without the maintainer's explicit go-ahead for that specific
version.** Pushing the tag is the publish step. PyPI uploads are permanent,
and a version number can never be uploaded again, even after deleting it.

Once approved, tag the merged commit on an up-to-date `master`:

```
git checkout master && git pull --ff-only
git tag -a vX.Y.Z -m "hachiko X.Y.Z"
git push origin vX.Y.Z
```

Then follow it with `gh run list --workflow release.yml` / `gh run watch`, and
confirm the version appears at <https://pypi.org/project/hachiko/>.

### When a release fails

- **Failed in check or ci (nothing published):** fix the problem on `master`,
  then delete and recreate the tag:
  `git push --delete origin vX.Y.Z && git tag -d vX.Y.Z`, and tag again.
- **Failed in publish with a trusted-publishing / OIDC error:** PyPI's
  publisher settings must match owner `biesnecker`, repository `hachiko`,
  workflow `release.yml`, environment `pypi`. Only the maintainer can change
  them on PyPI. Report the error rather than retrying.
- **Published, but github-release failed:** don't touch the tag. Re-run the
  failed job (`gh run rerun <run-id> --failed`).
- **A bad version reached PyPI:** don't try to replace it. Fix forward with a
  new patch version, and ask the maintainer whether to yank the bad one.

### Things that silently break publishing

- Renaming `release.yml` or the `pypi` environment. PyPI trusts those exact
  names, so the maintainer must update PyPI first.
- Renaming the `dist` artifact or the `build` job in `ci.yml`. The publish
  step downloads that artifact.
- Removing `workflow_call` from `ci.yml`.
- Tag names: the `pypi` environment only accepts `v*` tags. Older tags
  (`0.2.0`, `0.3.0`) have no prefix, and 0.4.0 was never tagged. Leave them
  as they are.

## Merging pull requests

Use a merge commit, not squash or rebase, for PRs that contain outside
contributors' commits. GitHub then shows their PRs as merged and keeps their
authorship.
