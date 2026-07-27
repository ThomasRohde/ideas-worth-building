# Agent contribution templates

These templates are task instructions, not autonomous decision procedures. An agent should select the narrowest template that matches the needed contribution, read the repository's governing documents first, and append the required disclosure.

| Template | Use it for |
|---|---|
| [`proposal-intake.md`](proposal-intake.md) | Search, prepare JSON, preview, and create one proposal without manufactured completeness. |
| [`proposal-input.example.json`](proposal-input.example.json) | Starting shape for the machine proposal contract. |
| [`duplicate-review.md`](duplicate-review.md) | Compare a proposed spark with open and closed Issues. |
| [`research-note.md`](research-note.md) | Answer a decision-relevant factual question with sources. |
| [`critique.md`](critique.md) | Steelman and stress-test a proposal. |
| [`experiment-design.md`](experiment-design.md) | Design the smallest meaningful learning step. |
| [`synthesis.md`](synthesis.md) | Propose a revised canonical Issue body. |
| [`promotion-review.md`](promotion-review.md) | Assess the promotion boundary and recommend, not decide. |
| [`contribution-disclosure.md`](contribution-disclosure.md) | Standard footer for substantive agent contributions. |

Do not run every template on every Issue. That produces process theatre and noise. Use the contribution that addresses the proposal's most consequential uncertainty.

## Posting a prepared contribution

Draft the contribution in a local Markdown file, inspect it, then use `--body-file` so shell quoting does not alter the text:

```bash
gh issue comment ISSUE_NUMBER --body-file contribution.md
```

For promotion preparation, create a draft pull request and leave the final promotion decision to a human curator:

```bash
gh pr create --draft --title "Promote: proposal title" --body-file promotion-pr.md
```

Direct API clients should produce the same visible structure and disclosure. They do not gain additional decision authority by bypassing `gh`.
