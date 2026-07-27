# 0007 — Machine intake mirrors human intake and requires a reviewed-search confirmation

- Status: Accepted
- Date: 2026-07-27

## Context

The repository is intended to work well with coding agents through `gh` and the GitHub API. GitHub Issue Forms provide a good human interface, but agents need a deterministic, non-interactive contract. Allowing each agent to invent its own body shape would weaken search, disclosure, labels, and promotion preparation. Allowing batch creation would amplify the exact volume problem the repository exists to resist.

## Decision

Agent-created proposals use a JSON input contract under `schemas/` and `scripts/iwb.py create-proposal`.

The helper:

- requires an authentic spark and proposition;
- accepts `null` and empty arrays for unknown information;
- records the actual queries used for duplicate and adjacency review;
- repeats those queries over open and closed Issues;
- provides a check-only preview;
- requires an explicit assertion that search results were reviewed before creation;
- renders the same semantic headings as the human Issue Form;
- applies deterministic type, status, origin, and contribution-needed labels;
- creates one Issue per invocation.

The confirmation is an accountability boundary, not proof that the search or distinctiveness judgment was correct.

## Consequences

- Agents have a stable interface that is easy to validate and generate.
- Human and machine submissions remain comparable and promotion tooling can parse both.
- Unknowns remain visible instead of being completed with synthetic narratives.
- Proposal creation requires a deliberate two-step interaction rather than one-shot generation.
- The helper cannot prevent a dishonest assertion or a low-quality search; repository review remains necessary.
- Direct API clients should reproduce the same body, labels, disclosure, and search discipline.

## Rejected alternatives

- **Raw `gh issue create` with arbitrary Markdown:** flexible but inconsistent and easy to bypass required disclosure.
- **Use the YAML Issue Form as an agent API:** optimized for interactive GitHub rendering rather than reliable structured agent input.
- **Autonomous duplicate classifier that blocks or merges submissions:** false confidence at a taste-sensitive boundary.
- **Batch intake of generated ideas:** rewards volume and consumes scarce attention.

## Review triggers

Revisit if GitHub exposes a stable structured Issue Form submission API, if the helper becomes a material maintenance burden, or if observed intake failures show that the two-step boundary is ineffective.
