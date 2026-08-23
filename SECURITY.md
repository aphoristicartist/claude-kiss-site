# Security policy

## Supported version

Security fixes are applied to the production site and the latest source on `main`.

## Report a vulnerability

Use GitHub's **Report a vulnerability** form in this repository's Security tab. Do not open a
public issue for installer integrity, release-mirror mismatch, header or redirect bypass,
Cloudflare Pages Functions behavior, credential exposure, or unintended production access.

Include the affected URL or commit, reproduction steps, observed headers or response details,
and impact. Remove tokens, cookies, private source, account identifiers, and personal paths
from supporting material. You should receive an acknowledgement within seven days.

Claude Code, Claude accounts, and the launcher itself have separate trust boundaries. Report
launcher vulnerabilities in the
[main repository](https://github.com/aphoristicartist/claude-kiss/security/advisories/new), and
report upstream product vulnerabilities to Anthropic unless this site introduced the issue.
