## Problem

What visitor, contributor, release, or operations problem does this solve?

## Change

Describe the content, design, build, routing, security-policy, or deployment change.

## Validation

- [ ] `./tests/test.sh`
- [ ] `./build.sh && ./tests/test.sh --built` when release or published assets are affected
- [ ] `git diff --check`
- [ ] Narrow and wide layouts were inspected when presentation changed
- [ ] Light, dark, keyboard, and no-CSS behavior were considered when presentation changed

If a check could not run, explain why and identify the remaining risk.

## Scope and deployment

- [ ] The change contains no generated release files, unrelated formatting, or telemetry.
- [ ] Security headers, static routes, redirects, and cache behavior remain intentional.
- [ ] Logs, screenshots, and fixtures contain no credentials, private source, or personal paths.
- [ ] Any required post-merge production verification is described.
