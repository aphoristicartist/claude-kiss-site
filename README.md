# claude-kiss.com

The static source for the Claude KISS website. It is kept separate from the launcher so
the product repository contains product code and its release packaging, while this
repository contains only site copy and design.

The site remains deliberately small:

- one HTML page;
- one stylesheet;
- no JavaScript;
- no analytics;
- no external fonts;
- no framework.

## Build

The build downloads the official launcher release from GitHub, verifies its SHA-256
checksum, extracts the matching installer, and stages the immutable domain release files:

```sh
./build.sh
```

Generated files:

```text
public/install.sh
public/releases/v0.6.0/claude-kiss.tar.gz
public/releases/v0.6.0/claude-kiss.tar.gz.sha256
public/releases/v0.6.0/release.json
```

## Deploy

```sh
./build.sh
CLOUDFLARE_ACCOUNT_ID=5d109626b9a1582c1ad4e336076a40fd \
  wrangler pages deploy public --project-name claude-kiss --branch main
```

## Release update

1. Publish `claude-kiss.tar.gz` and `claude-kiss.tar.gz.sha256` on the launcher release.
2. Update `RELEASE_VERSION` and the latest redirect in `public/_redirects`.
3. Run `./build.sh`.
4. Deploy.

MIT licensed. Independent project. Not affiliated with or endorsed by Anthropic.
