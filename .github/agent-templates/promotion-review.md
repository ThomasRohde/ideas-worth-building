# Agent task: promotion-boundary review

## Goal

Assess whether a proposal appears ready for human promotion review. Recommend; do not approve, merge, close, or apply `status:promoted`.

## Review dimensions

### Meaning
- Is it clear who or what is served?
- Is the form of value clear without a manufactured problem narrative?
- Does it explain why the change matters?

### Grounding
- Are current behaviours and alternatives represented honestly?
- Are verifiable claims cited?
- Are facts, assumptions, and speculation distinguishable?

### Distinctiveness
- Is there a non-obvious insight, synthesis, mechanism, or experiential ambition?
- Is it more than a generic capability application or feature bundle?
- Does it preserve a point of view?

### Excellence and learning
- Are qualities of excellent execution articulated?
- Is the strongest uncertainty visible?
- Is there a smallest meaningful exploration?

## Output

```markdown
## Contribution: Promotion review

### Strongest case for promotion
...

### Meaning
Ready / needs work — reasoning

### Grounding
Ready / needs work — reasoning

### Distinctiveness
Ready / needs work — reasoning

### Excellence and learning
Ready / needs work — reasoning

### Strongest remaining counterargument
...

### Recommendation
- [ ] Recommend human candidate review
- [ ] Recommend human promotion review
- [ ] Continue exploration or grounding
- [ ] Run a named experiment first
- [ ] Consider dormancy or archival

### Specific next contribution wanted
...
```

Append the agent disclosure from `contribution-disclosure.md`.

## Guardrails

- Do not calculate or invent a promotion score.
- Do not equate popularity, polish, or text length with quality.
- Do not treat lack of market evidence as fatal for non-commercial proposals.
- Do not make the final curatorial judgment.
