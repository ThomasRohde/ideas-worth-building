# 0001 — Issues are working memory

- Status: Accepted
- Date: 2026-07-27

## Context

Proposals need a low-friction place where incomplete thinking, questions, evidence, critique, experiments, and revisions can accumulate. Storing every early proposal directly as a Markdown file would impose pull-request ceremony too early and would encourage snapshots rather than conversation.

## Decision

GitHub Issues are the canonical working representation of active proposals and standalone problems.

The Issue body contains the current synthesis. Comments preserve contributions, debate, evidence, and history. Open and closed Issues are searched before new proposals are created.

## Consequences

- Entry remains accessible to contributors and agents using the web UI, `gh`, or the API.
- Working records can evolve without a pull request for every edit.
- Maintainers must steward Issue bodies rather than treating them as immutable submissions.
- Closed Issues remain part of working memory and duplicate detection.
- Git history alone does not capture every intermediate revision of an Issue body.

## Rejected alternatives

- **Markdown proposal for every submission:** too much ceremony at entry and poor conversational ergonomics.
- **GitHub Discussions as the core:** useful for broad conversation, but less structured for lifecycle labels, forms, and promotion linkage.
- **External database:** unnecessary infrastructure and a weaker public contribution path.

## Review triggers

Revisit if GitHub Issues no longer provide adequate exportability, search, attribution, moderation, or API access.
