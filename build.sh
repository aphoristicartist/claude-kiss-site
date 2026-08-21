#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
public="$repo/public"
version=$(cat "$repo/RELEASE_VERSION")
release="$public/releases/v$version"
temporary=$(mktemp -d "${TMPDIR:-/tmp}/claude-kiss-site.XXXXXX")
base="https://github.com/aphoristicartist/claude-kiss/releases/download/v$version"

cleanup() {
  rm -rf "$temporary"
}
trap cleanup EXIT HUP INT TERM

mkdir -p "$release" "$temporary/package"

curl -fsSL "$base/claude-kiss.tar.gz" -o "$temporary/claude-kiss.tar.gz"
curl -fsSL "$base/claude-kiss.tar.gz.sha256" -o "$temporary/claude-kiss.tar.gz.sha256"

expected=$(awk 'NR == 1 {print $1}' "$temporary/claude-kiss.tar.gz.sha256")
if command -v sha256sum >/dev/null 2>&1; then
  actual=$(sha256sum "$temporary/claude-kiss.tar.gz" | awk '{print $1}')
else
  actual=$(shasum -a 256 "$temporary/claude-kiss.tar.gz" | awk '{print $1}')
fi
if [ "$actual" != "$expected" ]; then
  printf 'claude-kiss-site: release checksum mismatch\n' >&2
  exit 1
fi

tar -xzf "$temporary/claude-kiss.tar.gz" -C "$temporary/package"
cp "$temporary/package/claude-kiss/install.sh" "$public/install.sh"
chmod 755 "$public/install.sh"
cp "$temporary/claude-kiss.tar.gz" "$release/claude-kiss.tar.gz"
cp "$temporary/claude-kiss.tar.gz.sha256" "$release/claude-kiss.tar.gz.sha256"
printf '%s\n' \
  '{"version":"'$version'","archive":"https://claude-kiss.com/releases/v'$version'/claude-kiss.tar.gz","sha256":"'$expected'"}' \
  >"$release/release.json"

printf 'Built claude-kiss.com %s\n' "$version"
printf '  installer: %s\n' "$public/install.sh"
printf '  archive:   %s\n' "$release/claude-kiss.tar.gz"
printf '  sha256:    %s\n' "$expected"
