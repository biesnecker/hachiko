#!/usr/bin/env bash
# Prints the CHANGELOG.md section for a version, without its heading.
set -euo pipefail

awk -v h="## $1 " '
    index($0, "## ") == 1 { in_section = index($0, h) == 1; next }
    in_section
' CHANGELOG.md | sed '/./,$!d'
