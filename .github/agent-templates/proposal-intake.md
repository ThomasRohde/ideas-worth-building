# Agent task: proposal intake through `gh`

## Goal

Capture one genuine proposal without generating noise, duplicating an existing Issue, or manufacturing completeness.

## Required sequence

1. Read `README.md`, `principles/`, `CONTRIBUTING.md`, `AGENTS.md`, and `SCHEMA.md`.
2. Search open and closed Issues using more than the proposed title:
   - synonyms and neighboring language;
   - the underlying capability or mechanism;
   - who or what might be served;
   - the desired experience or outcome;
   - broader and narrower formulations.
3. Inspect the closest results, not only the snippets.
4. Prefer a contribution to an existing Issue when the distinctive delta is weak.
5. Prepare JSON from `proposal-input.example.json`. Use `null`, empty arrays, or explicit uncertainty rather than plausible invention.
6. Validate and preview it:

   ```bash
   python scripts/iwb.py create-proposal --input proposal.json --check-only
   ```

7. Only after reviewing the preview and search record, create the Issue:

   ```bash
   python scripts/iwb.py create-proposal \
     --input proposal.json \
     --confirm-reviewed-search-results
   ```

## One-proposal rule

Create at most one new proposal in a run unless a human explicitly asked for a bounded set and reviewed the candidates. Do not turn brainstorming output directly into Issues.

## Minimum quality at entry

Only these are required:

- an authentic spark;
- a proposition that can be discussed;
- a documented open-and-closed Issue search;
- truthful disclosure of agent involvement.

Beneficiaries, evidence, alternatives, and purpose may still be unknown. State that directly.

## Stop instead of creating when

- an existing Issue contains substantially the same proposition;
- the only distinction is wording, branding, or a fashionable model;
- you would need to invent evidence or a user narrative;
- the proposal is one item in an uncurated generated list;
- a material legal, safety, privacy, or confidentiality concern requires human review.
