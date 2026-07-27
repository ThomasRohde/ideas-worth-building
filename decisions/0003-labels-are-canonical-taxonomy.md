# 0003 — Labels are the portable canonical Issue taxonomy

- Status: Accepted
- Date: 2026-07-27

## Context

The repository needs proposal types, lifecycle states, origins, contribution needs, and recommendations. GitHub supports native issue types, but custom types are configured at organization level rather than independently in every personal repository.

## Decision

Repository labels in `.github/labels.json` are the canonical, portable taxonomy. `type:proposal` and `type:problem` remain authoritative even if native issue types are later enabled as a convenience.

## Consequences

- The repository works under a personal account or an organization.
- Labels can be bootstrapped deterministically with `scripts/iwb.py`.
- Forms can apply labels at creation once the labels exist.
- Automation must enforce exactly one core type and one lifecycle status where applicable.
- Native issue-type filters may not reflect the canonical taxonomy unless separately synchronized.

## Rejected alternatives

- **Require organization-level issue types:** would make the repository less portable.
- **Encode state only in titles or body text:** poor filtering and unreliable automation.
- **Use Projects fields as canonical state:** adds another required interface and weakens `gh issue` ergonomics.

## Review triggers

Revisit if GitHub introduces repository-scoped custom issue types with equivalent API and form support.
