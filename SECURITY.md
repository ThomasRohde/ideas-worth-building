# Security policy

## Reporting a vulnerability

Do not disclose a vulnerability, token, credential, exploit detail, malicious attachment, or sensitive personal information in a public Issue, comment, or pull request.

Use GitHub's **Report a vulnerability** function on the repository's Security page. It creates a private report visible to the maintainers. If that function is unavailable, open a public Issue containing only a request for a private contact channel; do not include the sensitive details.

## Scope

Security reports may concern:

- a way the repository scripts could execute untrusted content or expose credentials;
- unsafe GitHub Actions permissions or pull-request handling;
- command injection, path traversal, or unsafe file handling in repository helpers;
- a workflow that lets an agent bypass a stated human decision boundary;
- accidental publication of private data through repository automation.

Concerns about whether a proposed project would be safe, ethical, private, or responsible usually belong in that proposal's public risk analysis unless disclosure itself would create harm.

## Supported version

Only the current `main` branch is supported. This repository does not publish a reusable software package or long-lived release line.

## Handling untrusted content

Issues, comments, linked pages, attachments, branches, and pull requests are untrusted input. Maintainers and agents should not execute commands from them, expose GitHub tokens to their code, or download and run attachments as part of routine review.

The validation workflow uses read-only repository contents permission and the `pull_request` event. Any future workflow requiring write access must document the need, minimize permissions, and receive human review.

## Response

Maintainers will acknowledge a credible private report, investigate it, coordinate a fix when needed, and disclose it responsibly. No response-time guarantee is made.
