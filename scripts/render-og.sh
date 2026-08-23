#!/bin/sh
set -eu

repo=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
source="$repo/public/og.svg"
target="$repo/public/og.jpg"

if command -v sips >/dev/null 2>&1; then
  sips -s format jpeg -s formatOptions 88 "$source" --out "$target" >/dev/null
elif command -v magick >/dev/null 2>&1; then
  magick -background '#f3f0e8' "$source" -quality 88 "$target"
else
  printf 'render-og: install ImageMagick, or run this script on macOS with sips\n' >&2
  exit 1
fi

printf 'Rendered %s from %s\n' "$target" "$source"
