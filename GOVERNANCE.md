# Governance

## Purpose of governance

Governance protects two things that are in tension:

1. an open entrance for incomplete, unconventional, and uncertain ideas;
2. a demanding promotion boundary that keeps the curated collection useful.

The repository is not governed by submission volume, reactions, or automatic scoring. Community participation informs decisions; accountable human judgment makes them.

## Roles

### Contributors

Anyone who opens an Issue, comments, researches, critiques, designs an experiment, prepares a pull request, or improves repository documentation.

### Proposal stewards

A contributor who takes responsibility for keeping an Issue's working representation coherent. The original proposer is the initial steward unless they decline or another steward is agreed.

Stewardship does not confer ownership of the idea or authority to promote it. Stewards may synthesize comments, invite needed contributions, and recommend lifecycle changes.

### Curators

Humans with repository authority who are accountable for candidate, promotion, archival, governance, and moderation decisions.

The founding curator is `@ThomasRohde`. Additional curators may be appointed through a governance pull request that records the rationale and scope of authority.

AI agents, bots, and models cannot be curators, approving reviewers, or final decision-makers.

### Maintainers

Humans who administer labels, permissions, Actions, templates, security settings, and repository mechanics. A maintainer may also be a curator, but mechanical authority and curatorial judgment are conceptually distinct.

## Decision principles

### Open entrance

Incomplete proposals are accepted when they contain a genuine spark and proposition and comply with the Code of Conduct. Lack of a conventional problem statement is not grounds for rejection.

### Demanding promotion

Promotion is a positive curation decision. It requires a written rationale that addresses meaning, grounding, distinctiveness, excellence, and learning.

### No mechanical popularity rule

Reactions, stars, forks, and comment volume may indicate attention. They do not establish value, truth, distinctiveness, or promotion readiness.

### No mechanical model score

Automated analysis, embeddings, novelty estimates, rubrics, and model reviews may support a decision. None can approve promotion or archival.

### Reasons over authority

Curators should explain consequential decisions. “Maintainer preference” alone is insufficient when a proposal has substantial community involvement.

### Reversibility

Dormancy and archival are reversible when material new evidence, capability, insight, or stewardship appears. Promotion can also be superseded or retired through a transparent pull request.

## Lifecycle authority

| Action | Who may perform it |
|---|---|
| Open `type:proposal` or `type:problem` | Any contributor |
| Recommend or apply `status:spark`, `exploring`, `grounding`, or `experimenting` | Steward or maintainer; agents only when explicitly authorized |
| Recommend `status:candidate`, `promoted`, `dormant`, or `archived` | Any contributor or agent with reasoning |
| Decide `status:candidate` | Human curator |
| Decide `status:promoted` | Human curator through merged PR |
| Decide `status:dormant` | Human steward, maintainer, or curator; never an unattended stale bot |
| Decide contested dormancy or archival | Human curator |
| Merge a promotion PR | Human curator or maintainer acting on explicit curator approval |
| Change principles, schema, or governance | Human-approved PR; decision record normally required |

## Candidate decision

A curator may apply `status:candidate` when the proposal appears close enough to the promotion boundary that focused review is more useful than broad exploration.

The curator should comment with:

- why the proposal may be worth promoting;
- the strongest remaining concern;
- the specific contribution now wanted;
- whether an experiment is required before promotion.

Candidate is not a promise of promotion.

## Promotion decision

A promotion PR should contain a concise curator decision record in its body:

- **Who or what is served?**
- **Why does that matter?**
- **What is distinctive here?**
- **What qualities make the proposed response worth preserving?**
- **What remains uncertain?**
- **Why promote now rather than continue only in the Issue?**

At least one named human curator must approve the promotion. While the repository has only one curator, the founding curator may approve their own promotion PR but must disclose that no independent curator review occurred. Once two or more active curators exist, promotion should normally receive approval from a curator who did not author the promotion synthesis.

Promotion is not determined by a majority vote. For difficult cases, curators should seek a reasoned rough consensus; if disagreement remains, the final decision and dissent should both be recorded.

## Archival decision

Archival closes an active line of inquiry; it does not declare the contributor foolish or the idea permanently worthless.

A curator must record at least one reason:

- duplicate and merged into another Issue;
- superseded by a stronger formulation;
- contradicted or invalidated by material evidence;
- insufficiently distinctive after exploration;
- outside repository scope;
- withdrawn;
- unsafe or irresponsible to pursue;
- no credible path to meaningful learning;
- other reason explained in the comment.

When contributions can be preserved, link the destination Issue, pattern, decision, or archived file.

## Dormancy

Dormancy is appropriate when a proposal remains plausible but lacks active stewardship, timely capability, necessary evidence, or a feasible next exploration.

Dormant Issues are normally closed to keep the active queue legible. They may be reopened without stigma when someone brings a concrete contribution or renewed stewardship.

No stale bot automatically marks proposals dormant or archived. Time without comments is not itself a judgment of value.

## Duplicate handling

A duplicate decision should compare the propositions, not only titles.

When closing a duplicate:

1. identify the canonical Issue;
2. state the overlap;
3. preserve any distinctive contribution by copying or linking it with attribution;
4. state whether any meaningful delta remains;
5. invite reopening if the delta was misunderstood.

Agents may perform duplicate analysis but may not close a contested duplicate autonomously.

## Conflicts of interest

Contributors and curators should disclose a material interest when relevant, including ownership, employment, investment, paid research, or a plan to commercialize the proposal.

A conflict does not automatically disqualify participation. It does require transparency and, when possible, independent review.

## Moderation

Maintainers may edit or remove content, close or lock threads, restrict participation, or ban contributors to enforce the Code of Conduct, protect privacy, prevent spam, or preserve repository quality.

Idea flooding, repetitive model-generated comments, fabricated evidence, covert promotion, harassment, and deliberate attribution removal are moderation issues rather than ordinary disagreement.

## Governance changes

Material changes to the repository's purpose, promotion criteria, decision rights, licensing, or agent authority require:

1. a focused pull request;
2. a linked `type:governance` Issue when debate is needed;
3. a decision record under `decisions/`;
4. explicit human curator approval.

Governance should remain lightweight. Add process only when it addresses an observed failure mode.
