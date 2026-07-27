# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Operating rules

@AGENTS.md

`AGENTS.md` is authoritative for how to contribute here: mandatory preflight, duplicate search, epistemic rules, disclosure, decision rights, and stop conditions. Follow it over any general instinct about "being helpful."

## Commands

Run both before opening a pull request — they are the two checks CI runs:

```bash
uv run python -m unittest discover -s tests -v
uv run python scripts/validate_repository.py
```

Tests use `unittest`, not pytest. Python is managed by `uv` (`.python-version` pins 3.13); prefix commands with `uv run`.

Repository mechanics go through the deterministic helper rather than improvised `gh` calls:

```bash
uv run python scripts/iwb.py search "keywords"
uv run python scripts/iwb.py create-proposal --input proposal.json --check-only
uv run python scripts/iwb.py transition 42 status:grounding
uv run python scripts/iwb.py prepare-promotion 42 --slug some-slug --curator @ThomasRohde
```

Add `--dry-run` to mutating commands to inspect the `gh` invocation without executing it. `/proposal.json` is gitignored and is the expected scratch path for machine input.

## Constraints

- **`scripts/` must stay dependency-free.** `pyproject.toml` declares `dependencies = []`. Use the standard library only; never add a third-party import or suggest `pip install`.
- Curated documents under `ideas/` must use `ideas/_template.md` and comply with `SCHEMA.md`. `validate_repository.py` enforces required front matter, required sections, and the absence of placeholders.
- This repository curates proposals; it is not the implementation repository for promoted ideas. Do not add substantial product code here.

## Style

- Python: run `uvx ruff check .` and `uvx ruff format .` on Python changes before a PR. The lint ruleset is pinned in `pyproject.toml` (`E4, E7, E9, F, I, UP`) because ruff's defaults shift between releases — do not widen it casually, and do not delete a `# noqa` without checking that the rule is actually unselected.
- `E501` is not linted; `line-length = 100` applies through `ruff format`. There are pre-existing long lines.
- `.editorconfig` governs the rest: LF endings, UTF-8, final newline, 4-space Python indent, 2-space YAML/JSON.

## Branches and pull requests

- `promote/<slug>` for promotion PRs, `docs/<topic>` for governance or documentation edits.
- A promotion PR adds exactly one `ideas/<slug>.md`, links the source Issue with `Closes #NUMBER`, and opens as a draft until a human curator has reviewed the promotion case.
- Do not bundle a governance change into an unrelated promotion PR.
- Paths listed in `.github/CODEOWNERS` (`ideas/`, `principles/`, `patterns/`, `decisions/`, `GOVERNANCE.md`, `SCHEMA.md`, `AGENTS.md`, `schemas/`, `.github/workflows/`) are human-curation boundaries — propose changes, do not assume approval.
