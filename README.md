<p align="center">
  <img src="public/mark.svg" width="112" height="112" alt="Claude KISS geometric K mark">
</p>

# claude-kiss.com

The static source for [claude-kiss.com](https://claude-kiss.com): the companion site for
[Claude KISS](https://github.com/aphoristicartist/claude-kiss).

The launcher and website live in separate repositories on purpose. Product code, tests,
and release packaging stay with the launcher. This repository owns the public explanation,
design, domain installer, and immutable release mirrors.

## Kept simple

- One product page, one small 404 page, and one stylesheet.
- No client-side JavaScript, analytics, cookies, framework, or external fonts.
- Code-native HTML, CSS, and SVG artwork; `og.jpg` is rendered from `og.svg` for
  social-card compatibility.
- Automatic light and dark palettes, visible keyboard focus, reduced-motion support,
  and a responsive layout.
- A restrictive Content Security Policy and explicit browser security headers.

The global `no-transform` cache directive is deliberate: it prevents the CDN from
injecting analytics and keeps mirrored release bytes untouched. The policy permits
same-origin connections for browser tooling while continuing to disallow scripts.

The visual system follows the same rule as the product: a small set of useful primitives,
combined deliberately. Its Bauhaus palette is warm paper (`#f3f0e8`), near-black
(`#11100e`), red (`#d83a2e`), cobalt (`#1746a2`), and yellow (`#f2c230`). The reusable
geometric K is [`public/mark.svg`](public/mark.svg).

After editing the vector social card, rebuild its compatibility JPEG with:

```sh
./scripts/render-og.sh
```

## Preview

Any static server works. With Python:

```sh
python3 -m http.server 8765 --directory public
```

Then open <http://localhost:8765>.

## Check

The dependency-free test suite checks HTML structure, fragment and ARIA references,
metadata, local assets, version consistency, security policy files, SVG syntax,
social-card dimensions, responsive CSS affordances, shell syntax, and the no-JavaScript
budget:

```sh
./tests/test.sh
```

After staging a published launcher release, it also verifies the generated installer,
archive checksum, and release metadata:

```sh
./build.sh
./tests/test.sh --built
```

For visual changes, also inspect narrow and wide viewports in both color schemes and run
an accessibility/performance audit in a browser. The production site should remain usable
at 200% zoom and without CSS.

## Build a release

The build reads its release input from `RELEASE_VERSION`. It downloads that launcher
release from GitHub, validates the SHA-256 digest, extracts and syntax-checks the matching
installer, then stages the domain files:

```sh
./build.sh
```

For version `0.7.1`, the ignored build outputs are:

```text
public/install.sh
public/releases/v0.7.1/claude-kiss.tar.gz
public/releases/v0.7.1/claude-kiss.tar.gz.sha256
public/releases/v0.7.1/release.json
```

The build intentionally fails if the launcher release is missing, malformed, or does not
match its published checksum. Publish the launcher first; deploy the site second.

## Deploy

The site targets Cloudflare Pages through `wrangler.toml`:

```sh
./build.sh
wrangler pages deploy public --project-name claude-kiss --branch main
```

Before deploying a new launcher version:

1. Publish `claude-kiss.tar.gz` and `claude-kiss.tar.gz.sha256` on the matching launcher
   tag.
2. Update `RELEASE_VERSION`, the visible version and release link in `public/index.html`,
   and the latest aliases in `public/_redirects`.
3. Run `./tests/test.sh`, `./build.sh`, and `./tests/test.sh --built`.
4. Preview the complete `public/` directory, deploy it, then verify the homepage,
   `/install.sh`, `/releases/latest`, and the immutable archive over HTTPS.

Never deploy an unverified local launcher build under an official release URL.

## License and independence

[MIT](LICENSE) © Aleksandr Lisenko.

Claude KISS is an independent project. It is not produced by, endorsed by, or affiliated
with Anthropic.
