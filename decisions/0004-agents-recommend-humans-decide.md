# 0004 — Agents recommend; humans decide

- Status: Accepted
- Date: 2026-07-27

## Context

The repository is intentionally optimized for agent-assisted contribution. Agents can perform useful research and synthesis at scale, but promotion and archival are judgments about meaning, distinctiveness, taste, and attention—not only classification tasks.

## Decision

Agents may analyze, draft, recommend, and prepare. Identifiable human curators retain authority over candidate designation, promotion, archival, contested duplicate resolution, and merging promotion pull requests.

## Consequences

- Agent contributions must disclose the tool/model, research use, review status, and uncertainty.
- Recommendation labels are separate from lifecycle labels.
- Scripts require an explicit human-approval flag for protected transitions.
- Repository automation must not merge or promote based solely on model output or numeric thresholds.
- Human decisions should include reasons rather than unexplained authority.

## Rejected alternatives

- **Fully autonomous curation:** optimizes consistency and throughput at the cost of accountable judgment and risks synthetic consensus.
- **Ban agents from substantive contribution:** discards valuable research, critique, and synthesis capacity.
- **Human click as nominal approval of an agent score:** preserves ceremony but not meaningful responsibility.

## Review triggers

Revisit only through a governance decision that addresses accountability, manipulation, model monoculture, and the nature of taste—not merely improved benchmark performance.
