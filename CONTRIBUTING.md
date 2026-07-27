# Contributing

This repository welcomes unfinished thoughts and demands honest development of them.

Read [`README.md`](README.md), [`principles/README.md`](principles/README.md), and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) before contributing. AI agents and agent-assisted contributors must also follow [`AGENTS.md`](AGENTS.md).

## The basic rule

> You may start with a problem, an idea, a capability, an observation, a desired experience, a prototype, or something whose purpose is not yet understood. You do not need to manufacture a problem statement. However, before a proposal is promoted, it must demonstrate who or what it serves, why that matters, and why this is a good response.

Only the spark and proposition need to be clear at entry. Other fields may say “unknown,” “untested,” or “not yet understood.”

## Before opening a proposal

Search open and closed Issues. Use more than the final title:

- synonyms and alternate phrasings;
- the underlying capability;
- the desired experience or outcome;
- likely beneficiaries;
- present alternatives;
- related prototypes or products.

If an existing proposal has substantially the same core, improve it. Add a new Issue only when the distinctive delta deserves its own working record.

A useful duplicate note is:

```markdown
### Duplicate search
- Searches: `...`, `...`, `...`
- Closest Issues: #12, #37
- Distinctive delta: ...
- Remaining uncertainty: ...
```

## Opening a proposal

Use the Proposal Issue form. It applies:

- `type:proposal`
- `status:spark`

Optional `origin:*` labels describe where the idea began, not what it must become:

- `origin:problem`
- `origin:capability`
- `origin:experience`
- `origin:observation`
- `origin:prototype`
- `origin:combination`
- `origin:unknown`

More than one origin may apply. `origin:unknown` is valid.

Keep one main proposition per Issue. A combination may be one proposition when the value lies in the synthesis itself.

### Agent and CLI path

Agents should use the JSON contract in [`schemas/proposal-input.schema.json`](schemas/proposal-input.schema.json) and the two-step flow described in [`AGENTS.md`](AGENTS.md). The first command validates the input, repeats searches over open and closed Issues, and previews the body; the second requires explicit confirmation that those results were reviewed.

This path does not waive any contribution rule. It makes omissions explicit and deterministic instead of encouraging agents to fill a human form with synthetic narrative.

## Opening a standalone problem

Use `type:problem` for a problem, frustration, tension, or recurring observation that is worth understanding even when no response is proposed.

A proposal does not need to link to a problem Issue. A problem Issue does not need to produce a proposal.

Problems remain working memory. If a problem reveals a durable cross-proposal pattern, that pattern may later be captured under `patterns/` through a pull request.

## Improving an existing proposal

The best contribution may be a comment rather than a new Issue. Useful contribution modes are described in [`patterns/contribution-modes.md`](patterns/contribution-modes.md).

When commenting:

- add a concrete delta;
- cite externally verifiable claims;
- distinguish facts, assumptions, and speculation;
- disclose material agent assistance;
- critique the proposal rather than the contributor;
- preserve unusual or ambitious qualities unless you can explain why they are harmful;
- avoid generic praise or dismissal.

Strong comments often include one of the following:

- a comparable project and the precise lesson it provides;
- a current workaround and why it persists;
- a contradiction or counterexample;
- an overlooked beneficiary or affected system;
- an implementation quality that changes the idea's character;
- a smaller experiment that could invalidate a key assumption;
- a proposed synthesis of the Issue body.

## Facts, assumptions, and speculation

Use these terms deliberately:

- **Fact** — externally verifiable or directly observed, with a source or described observation.
- **Assumption** — treated as provisionally true to reason or design, but not established.
- **Speculation** — a possibility worth considering without sufficient support yet.

Evidence may be qualitative, technical, experiential, scientific, operational, or market-based. Do not force every proposal into a market-demand frame. Beauty, insight, public value, delight, safety, autonomy, and reduction of complexity may matter without a conventional customer pain narrative.

## Lifecycle changes

A proposal has one `status:*` label. Statuses describe the present mode of work; they are not merit scores.

Contributors may recommend a status change. Human curators decide `status:candidate`, `status:promoted`, and `status:archived` and resolve contested transitions. A human steward, maintainer, or curator may decide dormancy; agents may recommend it but do not apply it autonomously.

Use `status:dormant` rather than forcing activity when no one is currently prepared to develop a proposal. Dormancy is not rejection.

Use `status:archived` with a written reason, such as:

- duplicate;
- superseded;
- invalidated by evidence;
- no longer distinctive;
- outside repository scope;
- withdrawn by the proposer;
- unable to be pursued responsibly.

Archival decisions may be revisited when material new information appears.

## Promotion pull requests

A proposal is promoted by adding one synthesized Markdown file under `ideas/` through a pull request.

Promotion PRs should normally:

1. be invited or endorsed by a human curator, normally through `status:candidate`;
2. link the source Issue with `Closes #NUMBER`;
3. add one `ideas/<slug>.md` file based on `ideas/_template.md`;
4. comply with `SCHEMA.md`;
5. explain the promotion case;
6. preserve important uncertainty and the strongest counterargument;
7. attribute material contributors;
8. pass repository validation;
9. receive an explicit human decision rationale before merge.

A promoted idea is not a commitment to implement it, a certification of novelty, or an investment recommendation. It is a curated judgment that the idea deserves preservation and serious consideration.

After merge, the source Issue is closed with `status:promoted`. The curator can record the final transition mechanically:

```bash
python scripts/iwb.py transition ISSUE_NUMBER status:promoted \
  --human-approved \
  --reason "Promotion PR #NUMBER merged"
```

The helper refuses to apply `status:promoted` while the source Issue is still open. Further evolution can occur through a new Issue or a pull request that links back to the source.

## Prototypes and implementation code

A prototype can be valuable evidence, especially when it reveals an experience or reduces a named uncertainty. Link it from the Issue and explain what it established and what it did not test.

Do not turn this repository into the implementation repository for a proposed product. Substantial build code should normally live separately. Link that project back to the source Issue and return material experiment results, failed assumptions, or design learning to the working proposal.

## Repository changes

Changes to principles, governance, schema, lifecycle, licensing, or decision rights require a pull request and usually a decision record under `decisions/`.

Do not hide a governance change inside an unrelated promotion PR.

## Contribution credit

Material contributions should be credited in the promoted document. Credit may include:

- the original spark;
- substantial research;
- a decisive critique;
- experiment design or results;
- synthesis or editorial work;
- distinctive design insight.

Credit is not allocated by text volume. Agents and models may be acknowledged, but only humans can serve as curators or approving reviewers.

## Licensing and public disclosure

By submitting an Issue, comment, pull request, or repository change, you agree that your contribution is licensed under the repository's applicable license:

- prose and idea content: CC BY 4.0;
- scripts, code, and automation: MIT.

Do not contribute confidential, proprietary, personal, security-sensitive, export-controlled, or patent-sensitive material. Public disclosure may affect intellectual-property options. The repository does not provide legal advice or guarantee freedom to operate.
