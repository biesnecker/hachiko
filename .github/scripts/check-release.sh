#!/usr/bin/env bash
# Checks that a release tag is safe to publish. Run from the repo root with
# the tag name, e.g. `check-release.sh v1.2.3`, with HEAD at the tagged commit.
set -euo pipefail

tag=$1
version=$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' hachiko/version.py)

fail() {
    echo "::error::$*" >&2
    exit 1
}

[ "$tag" = "v$version" ] ||
    fail "Tag $tag does not match the package version in hachiko/version.py (expected v$version)."

git merge-base --is-ancestor HEAD origin/master ||
    fail "Tag $tag points at a commit that isn't on master."

heading=$(awk -v h="## $version " 'index($0, h) == 1 { print; exit }' CHANGELOG.md)
[ -n "$heading" ] ||
    fail "CHANGELOG.md has no '## $version' section."
case "$heading" in
*nreleased*) fail "CHANGELOG.md still marks $version as unreleased; replace that with the release date." ;;
esac

echo "Releasing hachiko $version"
