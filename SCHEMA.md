# Repository Schema

This document defines the canonical metadata, document shapes, lifecycle invariants, and link conventions used by Ideas Worth Building.

## 1. Core entities

### Proposal Issue

A mutable working record with:

- exactly one `type:proposal` label;
- exactly one `status:*` label;
- zero or more `origin:*` labels;
- an Issue body containing the current synthesis;
- comments that preserve contributions, debate, evidence, and history.

### Problem Issue

A standalone problem, frustration, tension, or observation with:

- exactly one `type:problem` label;
- exactly one `status:*` label;
- zero or more origin or contribution labels;
- no requirement to link to a proposal.

### Curated idea document

A human-approved synthesis under `ideas/<slug>.md`, linked to its source Issue and merged through a promotion pull request.

### Pattern

A reusable quality, critique, contribution, or experiment pattern under `patterns/`. Patterns must be grounded in recurring repository experience or clearly identified external practice; they are not disguised lists of generated ideas.

### Decision record

A durable repository architecture or governance decision under `decisions/NNNN-short-title.md`.

## 2. Label schema

The canonical label definitions are in `.github/labels.json`.

### Type labels

Exactly one type label should be present on each core Issue:

- `type:proposal`
- `type:problem`
- `type:governance`

Repository maintenance tasks may use GitHub's standard labels without pretending to be proposals.

### Lifecycle labels

A proposal has exactly one:

- `status:spark`
- `status:exploring`
- `status:grounding`
- `status:candidate`
- `status:experimenting`
- `status:promoted`
- `status:dormant`
- `status:archived`

Status is a present-tense mode, not a quality score. `status:candidate` and `status:promoted` are reserved for `type:proposal` Issues. Standalone problems may be explored, grounded, experimented with, made dormant, or archived; a related proposal is promoted separately.

### Origin labels

Zero or more may be present:

- `origin:problem`
- `origin:capability`
- `origin:experience`
- `origin:observation`
- `origin:prototype`
- `origin:combination`
- `origin:unknown`

Origin describes how the proposal began. It is not a required justification.

### Contribution-needed labels

These labels invite specific help:

- `needs:duplicate-review`
- `needs:research`
- `needs:critique`
- `needs:experiment`
- `needs:design-judgment`
- `needs:synthesis`
- `needs:domain-knowledge`

### Recommendation labels

Advisory only:

- `recommend:candidate`
- `recommend:promotion`
- `recommend:dormancy`
- `recommend:archive`

A recommendation label is not a lifecycle transition.

## 3. Proposal Issue body

The Issue form renders the following headings. Only the first two are required at entry.

1. `### Duplicate and adjacency review`
2. `### The spark`
3. `### The proposition`
4. `### Origin`
5. `### Who or what might benefit, and why`
6. `### Current behaviours and alternatives`
7. `### The non-obvious insight`
8. `### What would make an implementation excellent`
9. `### Known uncertainties`
10. `### Risk that this is a solution looking for a problem`
11. `### Smallest meaningful exploration or experiment`
12. `### Contributions currently wanted`
13. `### Sources and supporting material`
14. `### AI or agent assistance`

The human form also renders a `### Search first` attestation. The machine path renders the same semantic headings and adds a contribution-integrity statement.

The body is expected to evolve. Empty sections may remain, or may explicitly say `Unknown`, until knowledge improves.

A proposal should not be rejected merely because later sections are incomplete. Before promotion, however, the curator must be able to synthesize all required curated-document sections.

## 4. Machine proposal input

Agents creating a proposal through `gh` should use [`schemas/proposal-input.schema.json`](schemas/proposal-input.schema.json) and [`scripts/iwb.py create-proposal`](scripts/iwb.py).

The contract requires:

- an authentic title, spark, and proposition;
- zero or more valid origins;
- the actual queries used to search open and closed Issues;
- a record that those results were reviewed;
- closest Issue numbers and a distinctive delta when a close match exists;
- explicit agent, model, research, human-review, and uncertainty disclosure.

Optional content uses `null` or empty arrays. This is deliberate: unknown information is not a validation failure and must not be generated merely to make the JSON appear complete.

The recommended two-step sequence is:

```bash
python scripts/iwb.py create-proposal --input proposal.json --check-only
python scripts/iwb.py create-proposal --input proposal.json --confirm-reviewed-search-results
```

The helper repeats the recorded searches with `--state all`, renders the canonical Issue headings, and applies deterministic labels. It does not verify truthfulness, establish distinctiveness, or replace human and agent judgment about whether an existing Issue should be improved instead.

## 5. Comment contribution shape

Comments need not follow a rigid template. Substantive agent contributions must include the disclosure specified in `AGENTS.md`.

When useful, comments should identify their mode:

```markdown
## Contribution: Research | Critique | Experiment | Synthesis | Connection | Design
```

Externally verifiable analysis should separate:

```markdown
### Facts and evidence
### Assumptions
### Speculation
```

Recommended relationship language:

- `Related to #12` — relevant but neither contains the other.
- `Builds on #12` — incorporates a material part of another proposal.
- `Contrasts with #12` — similar aim, meaningfully different response.
- `Possible duplicate of #12` — duplicate analysis is not yet decided.
- `Supersedes #12` — human decision that this formulation replaces another.
- `Experiment for #12` — work intended to reduce a named uncertainty.

## 6. Lifecycle transition guidance

The lifecycle is intentionally non-linear. Common transitions are:

```text
spark -> exploring | grounding | experimenting | dormant | archived
exploring -> grounding | experimenting | candidate | dormant | archived
grounding -> exploring | experimenting | candidate | dormant | archived
experimenting -> exploring | grounding | candidate | dormant | archived
candidate -> exploring | grounding | experimenting | promoted | dormant | archived
dormant -> exploring | grounding | experimenting | archived
promoted -> archived (only when the curated document is retired or superseded)
archived -> exploring (only with a human reopen decision and material new information)
```

A lifecycle change should remove the previous `status:*` label. `scripts/iwb.py transition` performs this mechanical step. It reserves candidate and promoted states for proposals, requires an explicit human rationale for protected decisions, and refuses to mark an open source Issue as promoted. `scripts/iwb.py prepare-promotion` normally requires the source proposal to be `status:candidate` before drafting curated memory.

## 7. Curated idea document

Every `ideas/*.md` file except `README.md` and `_template.md` must begin with restricted YAML front matter:

```yaml
---
schema_version: 1
title: "Clear human-readable title"
source_issue: 42
status: "promoted"
promoted_on: "2026-07-27"
origins: ["capability", "observation"]
themes: ["developer-tools"]
contributors: ["@original-author", "@researcher"]
promoted_by: ["@human-curator"]
---
```

### Metadata rules

- `schema_version` must be `1`.
- `title` must be non-empty.
- `source_issue` must be a positive integer.
- `status` must be `promoted` for a merged curated document.
- `promoted_on` must use `YYYY-MM-DD`.
- `origins` must contain zero or more origin names without the `origin:` prefix.
- `themes` is a small list of useful retrieval terms, not search-engine stuffing.
- `contributors` contains at least one GitHub handle and credits humans who made material contributions. Agent assistance is acknowledged in the document history when material.
- `promoted_by` must contain at least one human curator GitHub handle.

The restricted YAML subset exists so the dependency-free validator can parse it. Use quoted strings and JSON-style arrays as shown.

### Required headings

A curated document must contain these level-two headings in this order:

1. `## The spark`
2. `## The proposition`
3. `## Who or what it serves`
4. `## Why it matters`
5. `## Current behaviours and alternatives`
6. `## The non-obvious insight`
7. `## What would make an implementation excellent`
8. `## Evidence, assumptions, and speculation`
9. `## Known uncertainties and strongest counterargument`
10. `## Risk of solutionism`
11. `## Smallest meaningful exploration`
12. `## Promotion case`
13. `## History and attribution`

Each section must contain substantive text. `Unknown` is acceptable only where the promotion case explains why the remaining uncertainty does not undermine preservation.

### Content rules

A curated document:

- synthesizes rather than copies the Issue thread;
- cites externally verifiable claims;
- preserves material uncertainty and dissent;
- explains the distinctive insight or synthesis;
- describes qualities of excellent implementation rather than a feature inventory alone;
- avoids asserting novelty, demand, or impact without support;
- includes a smallest meaningful exploration;
- links its source Issue and promotion PR in `History and attribution` when available.

## 8. Promotion pull request

A promotion PR should:

- change one primary file under `ideas/`;
- link the source with `Closes #NUMBER`;
- identify the human curator;
- include the promotion rationale;
- include the agent disclosure when materially agent-assisted;
- pass `python scripts/validate_repository.py`;
- avoid unrelated governance or automation changes.

Exceptions should be explained in the PR body.

## 9. Archive schema

The `archive/` directory contains only version-controlled artifacts that were previously curated or otherwise intentionally preserved. Closed and archived Issues remain on GitHub and are not copied into the directory by default.

An archived curated document should preserve its original front matter and add:

```yaml
archived_on: "YYYY-MM-DD"
archive_reason: "superseded"
superseded_by: "ideas/new-slug.md"
```

`superseded_by` is optional unless the reason is `superseded`.

## 10. Repository validation

Run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Validation checks structure and syntax. It cannot determine whether an idea matters, is distinctive, demonstrates taste, or deserves promotion.
