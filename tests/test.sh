#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)

sh -n "$repo/build.sh" "$repo/scripts/render-og.sh" "$repo/tests/test.sh"
python3 "$repo/tests/test_site.py" "$@"

printf 'claude-kiss-site: source checks passed\n'
