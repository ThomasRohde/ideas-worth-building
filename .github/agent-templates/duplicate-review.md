# Agent task: duplicate and adjacency review

## Goal

Determine whether the target proposal is a duplicate, an adjacent proposal, a useful synthesis, or materially distinct. Do not decide closure autonomously.

## Required preparation

1. Read `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, and `SCHEMA.md`.
2. Read the target Issue and material comments.
3. Search open and closed Issues using:
   - title terms and synonyms;
   - beneficiary or affected system;
   - underlying capability;
   - desired experience or outcome;
   - present alternatives;
   - broader and narrower formulations.
4. Inspect the closest matches rather than relying on search snippets.

## Output

Post a concise comment with:

```markdown
## Contribution: Duplicate review

### Searches performed
- `...`

### Closest matches
- #N — overlap and difference

### Comparison
- **Shared core:** ...
- **Distinctive delta:** ...
- **Would combining them obscure either proposal?** ...

### Recommendation
Duplicate / adjacent / synthesis / distinct / uncertain

### What should be preserved if merged
...
```

Append the agent disclosure from `contribution-disclosure.md`.

## Guardrails

- Compare propositions, not titles alone.
- Do not claim global novelty.
- Do not close or relabel a contested Issue.
- Preserve credit for any distinctive contribution.
- Prefer “uncertain” over a forced decision when the delta depends on taste or intent.
