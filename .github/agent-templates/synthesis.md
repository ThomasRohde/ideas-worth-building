# Agent task: synthesize the working proposal

## Goal

Prepare a revised Issue body that reflects the strongest current understanding while preserving the original spark, material uncertainty, dissent, sources, and attribution.

## Method

1. Read the complete Issue and linked material.
2. Identify contributions that materially changed the proposal.
3. Resolve only disagreements that the evidence or explicit human decision actually resolved.
4. Keep unresolved disagreements visible.
5. Remove repetition and rhetorical inflation.
6. Preserve “unknown” rather than filling gaps with plausible invention.
7. Keep the proposition distinctive; do not average it into generic consensus.

## Output

Provide:

```markdown
## Contribution: Proposed synthesis

### Summary of substantive changes
- ...

### Proposed replacement Issue body
<complete body using the proposal headings from SCHEMA.md>

### Unresolved points intentionally preserved
- ...

### Attribution notes
- @handle — material contribution
```

Append the agent disclosure from `contribution-disclosure.md`.

## Guardrails

- Do not edit the Issue directly without explicit authorization.
- Do not silently drop contrary evidence.
- Do not list every commenter as a material contributor.
- Do not convert comments into facts merely because they were repeated.
