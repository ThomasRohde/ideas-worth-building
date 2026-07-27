# 0006 — Content and software use separate licenses

- Status: Accepted
- Date: 2026-07-27

## Context

The repository contains two materially different kinds of work: public prose and idea documentation intended for reuse with attribution, and executable scripts or automation that benefit from a conventional permissive software license.

## Decision

Non-software content is licensed under CC BY 4.0. Software, tests, and workflow automation are licensed under MIT. The root `LICENSE` explains the boundary and points to full license texts under `LICENSES/`.

## Consequences

- Others may remix and build on curated writing with attribution.
- Scripts are straightforward to reuse in other repositories.
- Contributors must not submit confidential, proprietary, patent-sensitive, or third-party material they cannot license.
- The licenses govern expression, not ownership, novelty, viability, safety, or freedom to operate for an underlying idea.

## Rejected alternatives

- **MIT for everything:** a software license is a poor semantic fit for prose and idea documentation.
- **CC BY for everything:** Creative Commons advises against using its licenses for software.
- **No explicit license:** leaves reuse rights ambiguous and undermines collaborative purpose.

## Review triggers

Revisit if a contributor agreement, patent policy, or different stewardship organization becomes necessary.
