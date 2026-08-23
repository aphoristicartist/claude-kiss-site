#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
public="$repo/public"
version=$(tr -d '\r\n' <"$repo/RELEASE_VERSION")

if ! printf '%s\n' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$'; then
  printf 'claude-kiss-site: invalid RELEASE_VERSION: %s\n' "$version" >&2
  exit 1
fi

release="$public/releases/v$version"
temporary=$(mktemp -d "${TMPDIR:-/tmp}/claude-kiss-site.XXXXXX")
base="https://github.com/aphoristicartist/claude-kiss/releases/download/v$version"

cleanup() {
  rm -rf "$temporary"
}
trap cleanup EXIT HUP INT TERM

mkdir -p "$temporary/package"

curl -fsSL --retry 3 "$base/claude-kiss.tar.gz" -o "$temporary/claude-kiss.tar.gz"
curl -fsSL --retry 3 "$base/claude-kiss.tar.gz.sha256" -o "$temporary/claude-kiss.tar.gz.sha256"

expected=$(awk 'NR == 1 {print $1}' "$temporary/claude-kiss.tar.gz.sha256")
if ! printf '%s\n' "$expected" | grep -Eq '^[0-9A-Fa-f]{64}$'; then
  printf 'claude-kiss-site: release checksum is not a SHA-256 digest\n' >&2
  exit 1
fi
expected=$(printf '%s' "$expected" | tr '[:upper:]' '[:lower:]')
if command -v sha256sum >/dev/null 2>&1; then
  actual=$(sha256sum "$temporary/claude-kiss.tar.gz" | awk '{print $1}')
else
  actual=$(shasum -a 256 "$temporary/claude-kiss.tar.gz" | awk '{print $1}')
fi
if [ "$actual" != "$expected" ]; then
  printf 'claude-kiss-site: release checksum mismatch\n' >&2
  exit 1
fi

for member in claude-kiss/install.sh claude-kiss/VERSION; do
  if ! tar -tzf "$temporary/claude-kiss.tar.gz" | grep -Fxq "$member"; then
    printf 'claude-kiss-site: release archive has no %s\n' "$member" >&2
    exit 1
  fi
done
tar -xzf "$temporary/claude-kiss.tar.gz" -C "$temporary/package" \
  claude-kiss/install.sh claude-kiss/VERSION
package_version=$(tr -d '\r\n' <"$temporary/package/claude-kiss/VERSION")
if [ "$package_version" != "$version" ]; then
  printf 'claude-kiss-site: archive VERSION %s does not match %s\n' \
    "$package_version" "$version" >&2
  exit 1
fi
sh -n "$temporary/package/claude-kiss/install.sh"
if ! grep -Fq "release_version=\${CLAUDE_KISS_VERSION:-$version}" \
  "$temporary/package/claude-kiss/install.sh"; then
  printf 'claude-kiss-site: installer does not embed release version %s\n' "$version" >&2
  exit 1
fi

mkdir -p "$release"
cp "$temporary/package/claude-kiss/install.sh" "$public/install.sh"
chmod 755 "$public/install.sh"
cp "$temporary/claude-kiss.tar.gz" "$release/claude-kiss.tar.gz"
cp "$temporary/claude-kiss.tar.gz.sha256" "$release/claude-kiss.tar.gz.sha256"
printf '{\n  "version": "%s",\n  "archive": "https://claude-kiss.com/releases/v%s/claude-kiss.tar.gz",\n  "installer": "https://claude-kiss.com/install.sh",\n  "release": "https://github.com/aphoristicartist/claude-kiss/releases/tag/v%s",\n  "sha256": "%s"\n}\n' \
  "$version" "$version" "$version" "$expected" >"$release/release.json"

printf 'Built claude-kiss.com %s\n' "$version"
printf '  installer: %s\n' "$public/install.sh"
printf '  archive:   %s\n' "$release/claude-kiss.tar.gz"
printf '  sha256:    %s\n' "$expected"
