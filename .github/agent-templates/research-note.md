# Agent task: decision-relevant research note

## Goal

Reduce one named uncertainty that could materially change the proposal. Do not produce a general market-research dump.

## Method

1. State the research question before searching.
2. Prefer primary sources, official documentation, original papers, standards, direct observations, or authoritative datasets.
3. Use a small number of strong sources.
4. Record publication dates and relevant constraints.
5. Separate sourced facts from inference.
6. Explain how each finding changes—or does not change—the proposal.

## Output

```markdown
## Contribution: Research

### Decision-relevant question
...

### Findings
1. **Fact:** ... [Source](https://...)
   - **Relevance:** ...

### Assumptions not resolved
- ...

### Implications for the proposal
- Strengthens: ...
- Weakens: ...
- Changes: ...
- No effect: ...

### Recommended next step
...
```

Append the agent disclosure from `contribution-disclosure.md`.

## Guardrails

- Do not cite AI summaries as evidence.
- Do not pad the note with tangential links.
- Do not infer demand from technical feasibility.
- Do not infer validation from a prototype unless the prototype tested the relevant claim.
- Report conflicting evidence rather than selecting only supportive sources.
