# Contributing to claude-kiss.com

This repository owns the public website, domain installer, release mirrors, static routing,
and Cloudflare Pages boundary for [Claude KISS](https://github.com/aphoristicartist/claude-kiss).
Product behavior belongs in the launcher repository.

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Use the issue forms
before substantial work so content and design changes remain aligned with the project.

## Design and implementation constraints

- Keep the site static, script-free, analytics-free, cookie-free, and dependency-light.
- Preserve keyboard access, semantic HTML, visible focus, responsive layouts, light and dark
  palettes, reduced-motion behavior, and usable no-CSS content.
- Keep assets local and the Content Security Policy restrictive.
- Do not weaken `no-transform`, release checksum verification, or immutable release paths.
- Update routing, headers, redirects, tests, and documentation together when an asset or URL
  changes.
- Product claims need direct evidence and explicit limits. Avoid universal benchmark claims.

## Local workflow

Preview with any static server, for example:

```sh
python3 -m http.server 8765 --directory public
```

Run the source checks:

```sh
./tests/test.sh
```

When release files or deploy behavior are involved, stage the published launcher artifacts
and run the complete suite:

```sh
./build.sh
./tests/test.sh --built
```

For visual work, inspect narrow and wide viewports in both color schemes, use the page with a
keyboard, check 200% zoom, and confirm the content remains usable without CSS. Run
`git diff --check` before opening a pull request.

## Pull requests and deployment

Pull requests target `main`. The protected branch requires the `site` CI check to pass and
all review conversations to be resolved. Maintainers use squash merges; keep the title clear
enough to become the final commit subject.

Do not commit generated `public/install.sh` or `public/releases/` files. Production deployment
runs only after a protected `main` update and only when the maintainer-controlled Cloudflare
credential gate is enabled. Contributors never need production credentials.
