# 0002 — Pull requests promote proposals into curated memory

- Status: Accepted
- Date: 2026-07-27

## Context

A working Issue may contain valuable but fragmented reasoning. The repository also needs a compact, version-controlled collection of proposals that have crossed a demanding quality boundary.

## Decision

A proposal enters `ideas/` only through a human-approved pull request. The pull request is the promotion case; the resulting Markdown file is a synthesis, not a transcript.

## Consequences

- Curated ideas have stable links, reviewable diffs, attribution, and history.
- Promotion remains visibly separate from ordinary Issue activity.
- The schema can be validated mechanically while substantive judgment remains human.
- Curated documents require maintenance when evidence or context changes.

## Rejected alternatives

- **Apply `status:promoted` without a file:** insufficient durable synthesis.
- **Automatically export every candidate:** confuses workflow state with curation.
- **Store only final files and close the Issues:** loses working lineage and future collaboration context.

## Review triggers

Revisit if a different versioned format provides materially better portability or if promotion volume makes one-file-per-idea impractical.
