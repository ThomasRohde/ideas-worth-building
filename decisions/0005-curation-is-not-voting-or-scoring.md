# 0005 — Curation is not voting or scoring

- Status: Accepted
- Date: 2026-07-27

## Context

Reactions, comment volume, stars, rubric totals, and model-generated scores are easy to measure. They can also reward familiarity, campaigning, controversy, contributor reach, or synthetic activity rather than quality.

## Decision

No popularity metric or aggregate score determines candidate status, promotion, dormancy, or archival. Review dimensions may structure reasoning, but the decision is a qualitative human judgment with a recorded rationale.

## Consequences

- Reactions may be treated as weak signals of interest, never votes with binding force.
- Curators cannot hide a decision behind an opaque score.
- Less familiar or initially unpopular proposals can receive serious attention.
- Decisions may be contestable and slower; their reasons should make that contest productive.

## Rejected alternatives

- **Community vote threshold:** vulnerable to audience size and coordination effects.
- **Weighted expert scorecard:** creates false precision and encourages rubric gaming.
- **Agent ensemble ranking:** creates synthetic consensus and embeds correlated model judgments.

## Review triggers

Revisit if the repository grows to require additional triage mechanisms. Any mechanism must preserve the distinction between allocating review attention and making a promotion decision.
