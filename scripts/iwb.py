#!/usr/bin/env python3
"""Deterministic GitHub mechanics for the Ideas Worth Building repository.

The helper delegates remote operations to the authenticated GitHub CLI. It does not
rank proposals or make curation decisions.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import validate_repository

ROOT = Path(__file__).resolve().parents[1]
LABELS_PATH = ROOT / ".github/labels.json"
STATUS_LABELS = tuple(sorted(validate_repository.REQUIRED_STATUS_LABELS))
PROTECTED_STATUSES = {
    "status:candidate",
    "status:promoted",
    "status:dormant",
    "status:archived",
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
THEME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

ORIGIN_TEXT_MAP = {
    "problem or frustration": "problem",
    "new capability": "capability",
    "desired experience": "experience",
    "observation or emerging pattern": "observation",
    "prototype or experiment": "prototype",
    "combination of existing concepts": "combination",
    "unknown or not useful to classify yet": "unknown",
}
ORIGIN_DISPLAY = {
    "problem": "Problem or frustration",
    "capability": "New capability",
    "experience": "Desired experience",
    "observation": "Observation or emerging pattern",
    "prototype": "Prototype or experiment",
    "combination": "Combination of existing concepts",
    "unknown": "Unknown or not useful to classify yet",
}
CONTRIBUTION_LABELS = {
    "duplicate-review": "needs:duplicate-review",
    "research": "needs:research",
    "critique": "needs:critique",
    "experiment": "needs:experiment",
    "design-judgment": "needs:design-judgment",
    "synthesis": "needs:synthesis",
    "domain-knowledge": "needs:domain-knowledge",
}
CONTRIBUTION_DISPLAY = {
    "duplicate-review": "Duplicate and adjacency review",
    "research": "Research and source verification",
    "critique": "Strong critique or counterexample",
    "experiment": "Experiment design or results",
    "design-judgment": "Design judgment and quality bar",
    "synthesis": "Synthesis and editing",
    "domain-knowledge": "Domain knowledge",
}
RELATIONSHIP_DISPLAY = {
    "related-to": "Related to",
    "builds-on": "Builds on",
    "contrasts-with": "Contrasts with",
    "possible-duplicate-of": "Possible duplicate of",
    "supersedes": "Supersedes",
    "experiment-for": "Experiment for",
}
PROPOSAL_INPUT_KEYS = {
    "title",
    "spark",
    "proposition",
    "origins",
    "beneficiaries",
    "alternatives",
    "insight",
    "excellence",
    "uncertainties",
    "solutionism_risk",
    "experiment",
    "facts",
    "assumptions",
    "speculation",
    "sources",
    "contributions_wanted",
    "duplicate_search",
    "related_issues",
    "agent_disclosure",
}

SECTION_MAP = {
    "The spark": "spark",
    "The proposition": "proposition",
    "Origin": "origin",
    "Duplicate and adjacency review": "duplicate_review",
    "Who or what might benefit, and why": "beneficiaries",
    "Current behaviours and alternatives": "alternatives",
    "The non-obvious insight": "insight",
    "What would make an implementation excellent": "excellence",
    "Known uncertainties": "uncertainties",
    "Risk that this is a solution looking for a problem": "solutionism",
    "Smallest meaningful exploration or experiment": "experiment",
    "Contributions currently wanted": "contributions",
    "Sources and supporting material": "sources",
    "AI or agent assistance": "agent_assistance",
}


class CliError(RuntimeError):
    """An expected command-line error with a concise user-facing message."""


def _repo_args(repo: str | None) -> list[str]:
    return ["--repo", repo] if repo else []


def _render_command(command: Sequence[str]) -> str:
    return shlex.join(str(part) for part in command)


def _ensure_gh() -> None:
    if shutil.which("gh") is None:
        raise CliError(
            "GitHub CLI 'gh' was not found. Install it and run 'gh auth login' before remote commands."
        )


def _run(
    command: Sequence[str],
    *,
    capture: bool = False,
    dry_run: bool = False,
) -> str:
    if dry_run:
        print(f"DRY RUN: {_render_command(command)}")
        return ""

    _ensure_gh()
    result = subprocess.run(
        list(command),
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = (result.stderr or "").strip()
        raise CliError(f"command failed: {_render_command(command)}\n{detail}")
    return result.stdout if capture else ""


def _gh_json(command: Sequence[str]) -> Any:
    output = _run(command, capture=True)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise CliError(f"GitHub CLI returned invalid JSON for {_render_command(command)}") from exc


def _load_labels() -> list[dict[str, str]]:
    try:
        labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot read canonical labels from {LABELS_PATH}: {exc}") from exc
    if not isinstance(labels, list):
        raise CliError(f"{LABELS_PATH} must contain a JSON array")
    return labels


def _normalise_handle(handle: str) -> str:
    handle = handle.strip()
    return handle if handle.startswith("@") else f"@{handle}"


def _markdown_quote(value: str) -> str:
    return value.strip() if value.strip() else "Not yet recorded in the source Issue."


def _parse_issue_form_body(body: str) -> dict[str, str]:
    """Parse the level-three headings emitted by GitHub Issue Forms."""

    heading_re = re.compile(r"(?m)^###\s+(.+?)\s*$")
    matches = list(heading_re.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[match.end() : end].strip()
        key = SECTION_MAP.get(heading)
        if key:
            sections[key] = content
    return sections


def _origins_from_form(value: str) -> list[str]:
    lowered = value.casefold()
    origins = [origin for text, origin in ORIGIN_TEXT_MAP.items() if text in lowered]
    origins = list(dict.fromkeys(origins))
    if "unknown" in origins and len(origins) > 1:
        origins.remove("unknown")
    return origins


def _json_inline(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _require_string(value: Any, name: str, *, allow_null: bool = False) -> str | None:
    if value is None and allow_null:
        return None
    if not isinstance(value, str) or not value.strip():
        suffix = " or null" if allow_null else ""
        raise CliError(f"proposal input field {name!r} must be a non-empty string{suffix}")
    return value.strip()


def _string_list(value: Any, name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise CliError(f"proposal input field {name!r} must be an array of non-empty strings")
    cleaned = [item.strip() for item in value]
    if len(cleaned) != len(set(cleaned)):
        raise CliError(f"proposal input field {name!r} contains duplicate values")
    return cleaned


def load_proposal_input(path: Path) -> dict[str, Any]:
    """Load and validate the dependency-free subset of the agent proposal contract."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot parse proposal input {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CliError("proposal input must be a JSON object")

    unknown = sorted(set(payload) - PROPOSAL_INPUT_KEYS)
    if unknown:
        raise CliError(f"proposal input contains unsupported fields: {', '.join(unknown)}")

    required = {
        "title",
        "spark",
        "proposition",
        "origins",
        "duplicate_search",
        "agent_disclosure",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise CliError(f"proposal input is missing required fields: {', '.join(missing)}")

    result: dict[str, Any] = {
        "title": _require_string(payload["title"], "title"),
        "spark": _require_string(payload["spark"], "spark"),
        "proposition": _require_string(payload["proposition"], "proposition"),
    }
    if len(result["title"]) < 5:
        raise CliError("proposal input title must contain at least 5 characters")
    if len(result["title"]) > 180:
        raise CliError("proposal input title may not exceed 180 characters")

    origins = _string_list(payload["origins"], "origins")
    invalid_origins = sorted(set(origins) - set(ORIGIN_DISPLAY))
    if invalid_origins:
        raise CliError(f"proposal input contains unsupported origins: {', '.join(invalid_origins)}")
    if "unknown" in origins and len(origins) > 1:
        raise CliError("proposal origin 'unknown' may not be combined with other origins")
    result["origins"] = origins

    for key in (
        "beneficiaries",
        "alternatives",
        "insight",
        "excellence",
        "uncertainties",
        "solutionism_risk",
        "experiment",
    ):
        result[key] = _require_string(payload.get(key), key, allow_null=True)

    for key in ("facts", "assumptions", "speculation"):
        result[key] = _string_list(payload.get(key, []), key)

    contributions = _string_list(
        payload.get("contributions_wanted", []), "contributions_wanted"
    )
    invalid_contributions = sorted(set(contributions) - set(CONTRIBUTION_LABELS))
    if invalid_contributions:
        raise CliError(
            "proposal input contains unsupported contribution requests: "
            + ", ".join(invalid_contributions)
        )
    result["contributions_wanted"] = contributions

    sources = payload.get("sources", [])
    if not isinstance(sources, list):
        raise CliError("proposal input field 'sources' must be an array")
    clean_sources: list[dict[str, str | None]] = []
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict) or set(source) - {"title", "url", "supports"}:
            raise CliError(f"source {index} must contain only title, url, and supports")
        url = _require_string(source.get("url"), f"sources[{index}].url")
        assert isinstance(url, str)
        if not url.startswith(("https://", "http://")):
            raise CliError(f"sources[{index}].url must be an HTTP or HTTPS URL")
        supports = _require_string(source.get("supports"), f"sources[{index}].supports")
        title = _require_string(
            source.get("title"), f"sources[{index}].title", allow_null=True
        )
        clean_sources.append({"title": title, "url": url, "supports": supports})
    result["sources"] = clean_sources

    duplicate = payload["duplicate_search"]
    if not isinstance(duplicate, dict):
        raise CliError("duplicate_search must be an object")
    expected_duplicate = {
        "queries",
        "reviewed_open_and_closed",
        "closest_issues",
        "distinctive_delta",
    }
    if set(duplicate) != expected_duplicate:
        missing_duplicate = sorted(expected_duplicate - set(duplicate))
        unknown_duplicate = sorted(set(duplicate) - expected_duplicate)
        detail = []
        if missing_duplicate:
            detail.append("missing " + ", ".join(missing_duplicate))
        if unknown_duplicate:
            detail.append("unsupported " + ", ".join(unknown_duplicate))
        raise CliError("duplicate_search fields are invalid: " + "; ".join(detail))
    queries = _string_list(duplicate["queries"], "duplicate_search.queries")
    if not queries:
        raise CliError("duplicate_search.queries must contain at least one search")
    if duplicate["reviewed_open_and_closed"] is not True:
        raise CliError("duplicate_search.reviewed_open_and_closed must be true")
    closest = duplicate["closest_issues"]
    if not isinstance(closest, list) or not all(
        isinstance(number, int) and not isinstance(number, bool) and number > 0
        for number in closest
    ):
        raise CliError(
            "duplicate_search.closest_issues must be an array of positive Issue numbers"
        )
    if len(closest) != len(set(closest)):
        raise CliError("duplicate_search.closest_issues contains duplicates")
    delta = _require_string(
        duplicate["distinctive_delta"],
        "duplicate_search.distinctive_delta",
        allow_null=True,
    )
    if closest and delta is None:
        raise CliError("a distinctive_delta is required when closest_issues is not empty")
    result["duplicate_search"] = {
        "queries": queries,
        "reviewed_open_and_closed": True,
        "closest_issues": closest,
        "distinctive_delta": delta,
    }

    related = payload.get("related_issues", [])
    if not isinstance(related, list):
        raise CliError("related_issues must be an array")
    clean_related: list[dict[str, Any]] = []
    for index, relationship in enumerate(related, start=1):
        expected = {"number", "relationship", "note"}
        if not isinstance(relationship, dict) or set(relationship) != expected:
            raise CliError(
                f"related_issues[{index}] must contain exactly number, relationship, and note"
            )
        number = relationship["number"]
        if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
            raise CliError(f"related_issues[{index}].number must be a positive integer")
        relation = relationship["relationship"]
        if relation not in RELATIONSHIP_DISPLAY:
            raise CliError(f"related_issues[{index}].relationship is unsupported")
        note = _require_string(relationship["note"], f"related_issues[{index}].note")
        clean_related.append({"number": number, "relationship": relation, "note": note})
    result["related_issues"] = clean_related

    disclosure = payload["agent_disclosure"]
    if not isinstance(disclosure, dict):
        raise CliError("agent_disclosure must be an object")
    expected_disclosure = {
        "agent_tool",
        "model",
        "external_research_performed",
        "human_reviewed",
        "remaining_uncertainties",
    }
    if set(disclosure) != expected_disclosure:
        raise CliError(
            "agent_disclosure must contain exactly the fields defined by the schema"
        )
    if not isinstance(disclosure["external_research_performed"], bool):
        raise CliError("agent_disclosure.external_research_performed must be true or false")
    if not isinstance(disclosure["human_reviewed"], bool):
        raise CliError("agent_disclosure.human_reviewed must be true or false")
    result["agent_disclosure"] = {
        "agent_tool": _require_string(
            disclosure["agent_tool"], "agent_disclosure.agent_tool"
        ),
        "model": _require_string(disclosure["model"], "agent_disclosure.model"),
        "external_research_performed": disclosure["external_research_performed"],
        "human_reviewed": disclosure["human_reviewed"],
        "remaining_uncertainties": _string_list(
            disclosure["remaining_uncertainties"],
            "agent_disclosure.remaining_uncertainties",
        ),
    }
    return result


def _markdown_list(items: list[str], *, empty: str) -> str:
    return "\n".join(f"- {item}" for item in items) if items else empty


def render_proposal_body(payload: dict[str, Any]) -> str:
    """Render the same semantic shape used by the human Proposal Issue Form."""

    duplicate = payload["duplicate_search"]
    closest = (
        ", ".join(f"#{number}" for number in duplicate["closest_issues"])
        if duplicate["closest_issues"]
        else "No close match was identified in the reviewed results."
    )
    related = [
        f"{RELATIONSHIP_DISPLAY[item['relationship']]} #{item['number']} — {item['note']}"
        for item in payload["related_issues"]
    ]
    origin_text = _markdown_list(
        [ORIGIN_DISPLAY[origin] for origin in payload["origins"]],
        empty="Not classified at entry.",
    )
    contribution_text = _markdown_list(
        [CONTRIBUTION_DISPLAY[item] for item in payload["contributions_wanted"]],
        empty="No specific contribution mode selected yet.",
    )
    sources = [
        f"[{item['title'] or item['url']}]({item['url']}) — supports: {item['supports']}"
        for item in payload["sources"]
    ]
    disclosure = payload["agent_disclosure"]
    remaining_items = disclosure["remaining_uncertainties"] or [
        "None identified beyond the uncertainties in the proposal body."
    ]
    remaining = "\n".join(f"  - {item}" for item in remaining_items)

    def optional(key: str) -> str:
        return payload[key] or "Unknown at entry."

    return f'''### Search first

Open and closed Issues were searched before creation.

### Duplicate and adjacency review

**Searches performed**
{_markdown_list([f'`{query}`' for query in duplicate['queries']], empty='- None recorded.')}

**Closest reviewed Issues**
{closest}

**Distinctive delta**
{duplicate['distinctive_delta'] or 'No close match was identified; distinctiveness still requires further critique.'}

**Other explicit relationships**
{_markdown_list(related, empty='- None recorded.')}

### The spark

{payload['spark']}

### The proposition

{payload['proposition']}

### Origin

{origin_text}

### Who or what might benefit, and why

{optional('beneficiaries')}

### Current behaviours and alternatives

{optional('alternatives')}

### The non-obvious insight

{optional('insight')}

### What would make an implementation excellent

{optional('excellence')}

### Known uncertainties

{optional('uncertainties')}

### Risk that this is a solution looking for a problem

{optional('solutionism_risk')}

### Smallest meaningful exploration or experiment

{optional('experiment')}

### Contributions currently wanted

{contribution_text}

### Sources and supporting material

#### Facts and evidence
{_markdown_list(payload['facts'], empty='- No externally verifiable factual claim is asserted yet.')}

#### Assumptions
{_markdown_list(payload['assumptions'], empty='- None recorded beyond the visible uncertainties.')}

#### Speculation
{_markdown_list(payload['speculation'], empty='- None recorded.')}

#### Sources
{_markdown_list(sources, empty='- No external sources used.')}

### AI or agent assistance

- **Agent/tool:** {disclosure['agent_tool']}
- **Model:** {disclosure['model']}
- **External research performed:** {'yes' if disclosure['external_research_performed'] else 'no'}
- **Human reviewed before submission:** {'yes' if disclosure['human_reviewed'] else 'no'}
- **Remaining uncertainties:**
{remaining}

### Contribution integrity

This Issue was created through the repository's machine-oriented proposal contract. Unknown fields were left unknown rather than filled with invented users, pain points, evidence, quotations, or market narratives.
'''


def _search_queries(
    queries: list[str], *, repo: str | None, limit: int
) -> dict[str, list[dict[str, Any]]]:
    results: dict[str, list[dict[str, Any]]] = {}
    for query in queries:
        command = [
            "gh",
            "issue",
            "list",
            "--state",
            "all",
            "--search",
            query,
            "--limit",
            str(limit),
            "--json",
            "number,title,state,url,labels",
            *_repo_args(repo),
        ]
        results[query] = _gh_json(command)
    return results


def _print_search_snapshot(results: dict[str, list[dict[str, Any]]]) -> None:
    print("Open-and-closed Issue search snapshot:")
    for query, matches in results.items():
        print(f"\n  Query: {query!r}")
        if not matches:
            print("    No matches.")
            continue
        for item in matches:
            print(f"    #{item['number']} [{item['state']}] {item['title']} — {item['url']}")


def cmd_create_proposal(args: argparse.Namespace) -> int:
    payload = load_proposal_input(args.input)
    search_results = _search_queries(
        payload["duplicate_search"]["queries"],
        repo=args.repo,
        limit=args.search_limit,
    )
    _print_search_snapshot(search_results)
    body = render_proposal_body(payload)

    if args.check_only:
        print("\n--- Proposed Issue body ---\n")
        print(body)
        print("\nCheck only: no Issue was created.")
        return 0

    if not args.confirm_reviewed_search_results:
        raise CliError(
            "creation requires --confirm-reviewed-search-results after inspecting the open-and-closed search snapshot"
        )

    labels = ["type:proposal", "status:spark"]
    labels.extend(f"origin:{origin}" for origin in payload["origins"])
    labels.extend(CONTRIBUTION_LABELS[item] for item in payload["contributions_wanted"])
    labels = list(dict.fromkeys(labels))

    with tempfile.TemporaryDirectory(prefix="iwb-") as directory:
        body_file = Path(directory) / "proposal.md"
        body_file.write_text(body, encoding="utf-8")
        command = [
            "gh",
            "issue",
            "create",
            "--title",
            payload["title"],
            "--body-file",
            str(body_file),
        ]
        for label in labels:
            command.extend(["--label", label])
        command.extend(_repo_args(args.repo))
        if args.dry_run:
            print(f"\nDRY RUN: {_render_command(command)}")
            print("\n--- Proposed Issue body ---\n")
            print(body)
            return 0
        url = _run(command, capture=True).strip()

    print(url or "Proposal Issue created.")
    return 0


def cmd_bootstrap_labels(args: argparse.Namespace) -> int:
    labels = _load_labels()
    for label in labels:
        command = [
            "gh",
            "label",
            "create",
            label["name"],
            "--color",
            label["color"],
            "--description",
            label["description"],
            "--force",
            *_repo_args(args.repo),
        ]
        _run(command, dry_run=args.dry_run)
    action = "Would create or update" if args.dry_run else "Created or updated"
    print(f"{action} {len(labels)} canonical labels.")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    command = [
        "gh",
        "issue",
        "list",
        "--state",
        "all",
        "--search",
        args.query,
        "--limit",
        str(args.limit),
        "--json",
        "number,title,state,labels,url,updatedAt,author",
        *_repo_args(args.repo),
    ]
    items = _gh_json(command)
    if args.json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return 0
    if not items:
        print("No matching open or closed Issues found.")
        return 0
    for item in items:
        label_names = [label["name"] for label in item.get("labels", [])]
        status = next(
            (label for label in label_names if label.startswith("status:")), "no-status"
        )
        issue_type = next(
            (label for label in label_names if label.startswith("type:")), "no-type"
        )
        author = (item.get("author") or {}).get("login", "unknown")
        print(
            f"#{item['number']} [{item['state']}] {item['title']}\n"
            f"  {issue_type} · {status} · @{author} · {item['url']}"
        )
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    target = args.status
    if target in PROTECTED_STATUSES:
        if not args.human_approved:
            raise CliError(
                f"{target} requires --human-approved. Agents may recommend this transition but may not decide it."
            )
        if not args.reason or len(args.reason.strip()) < 12:
            raise CliError(
                f"{target} requires --reason with the human decision rationale or promotion PR reference."
            )

    view_command = [
        "gh",
        "issue",
        "view",
        str(args.issue),
        "--json",
        "number,title,url,labels,state",
        *_repo_args(args.repo),
    ]
    issue = _gh_json(view_command)
    current_statuses = [
        label["name"]
        for label in issue.get("labels", [])
        if label.get("name", "").startswith("status:")
    ]
    type_labels = {
        label["name"]
        for label in issue.get("labels", [])
        if label.get("name", "").startswith("type:")
    }
    if target in {"status:candidate", "status:promoted"} and "type:proposal" not in type_labels:
        raise CliError(f"{target} is reserved for type:proposal Issues")
    if target == "status:promoted" and issue.get("state") != "CLOSED":
        raise CliError(
            "status:promoted may be applied only after the promotion PR has merged and closed the source Issue"
        )

    if current_statuses == [target]:
        print(f"Issue #{args.issue} already has {target}.")
        return 0

    edit_command = ["gh", "issue", "edit", str(args.issue)]
    for status in current_statuses:
        edit_command.extend(["--remove-label", status])
    edit_command.extend(["--add-label", target, *_repo_args(args.repo)])
    _run(edit_command, dry_run=args.dry_run)

    if args.reason:
        decision_kind = "Human lifecycle decision" if args.human_approved else "Lifecycle update"
        body = (
            f"### {decision_kind}\n\n"
            f"Transitioned from {', '.join(f'`{s}`' for s in current_statuses) or 'no status label'} "
            f"to `{target}`.\n\n"
            f"**Reason:** {args.reason.strip()}"
        )
        comment_command = [
            "gh",
            "issue",
            "comment",
            str(args.issue),
            "--body",
            body,
            *_repo_args(args.repo),
        ]
        _run(comment_command, dry_run=args.dry_run)

    verb = "Would transition" if args.dry_run else "Transitioned"
    print(f"{verb} Issue #{args.issue} to {target}.")
    return 0


def _promotion_document(
    issue: dict[str, Any],
    sections: dict[str, str],
    *,
    curator: str,
    themes: list[str],
    extra_contributors: list[str],
    promoted_on: str,
) -> str:
    author_login = (issue.get("author") or {}).get("login")
    contributors = []
    if author_login:
        contributors.append(_normalise_handle(author_login))
    contributors.extend(_normalise_handle(item) for item in extra_contributors)
    contributors = list(dict.fromkeys(contributors))

    origins = _origins_from_form(sections.get("origin", ""))
    title = issue["title"].strip()
    source_issue = int(issue["number"])
    source_url = issue["url"]

    beneficiaries = _markdown_quote(sections.get("beneficiaries", ""))
    uncertainties = _markdown_quote(sections.get("uncertainties", ""))
    solutionism = _markdown_quote(sections.get("solutionism", ""))
    sources = _markdown_quote(sections.get("sources", ""))
    agent_assistance = sections.get("agent_assistance", "").strip()
    duplicate_review = sections.get("duplicate_review", "").strip()

    return f'''---
schema_version: 1
title: {_json_inline(title)}
source_issue: {source_issue}
status: "promoted"
promoted_on: {_json_inline(promoted_on)}
origins: {_json_inline(origins)}
themes: {_json_inline(themes)}
contributors: {_json_inline(contributors)}
promoted_by: {_json_inline([_normalise_handle(curator)])}
---

# {title}

> {_markdown_quote(sections.get("proposition", "")).splitlines()[0]}

## The spark

{_markdown_quote(sections.get("spark", ""))}

## The proposition

{_markdown_quote(sections.get("proposition", ""))}

## Who or what it serves

{beneficiaries}

## Why it matters

{beneficiaries}

This section is derived from the source Issue's combined account of beneficiary and significance. Promotion review should sharpen the distinction without inventing evidence.

## Current behaviours and alternatives

{_markdown_quote(sections.get("alternatives", ""))}

## The non-obvious insight

{_markdown_quote(sections.get("insight", ""))}

## What would make an implementation excellent

{_markdown_quote(sections.get("excellence", ""))}

## Evidence, assumptions, and speculation

### Sources and externally checkable material

{sources}

### Assumptions and speculation still visible in the working proposal

{uncertainties}

## Known uncertainties and strongest counterargument

{uncertainties}

The strongest recorded solutionism challenge is:

{solutionism}

## Risk of solutionism

{solutionism}

## Smallest meaningful exploration

{_markdown_quote(sections.get("experiment", ""))}

## Promotion case

[HUMAN CURATOR REQUIRED] Replace this marker with the qualitative promotion rationale. Address who or what is served, why it matters, what is distinctive, what excellent execution requires, what remains uncertain, and why the proposal should enter curated memory now.

## History and attribution

- Source Issue: [#{source_issue}]({source_url})
- Promotion pull request: To be linked before merge.
- Original Issue author: {_normalise_handle(author_login) if author_login else 'Not exposed by GitHub CLI.'}
- Material human contributors: {', '.join(contributors) if contributors else 'To be confirmed during review.'}
- Duplicate and adjacency review from the Issue: {duplicate_review or 'None recorded in the source Issue.'}
- Material agent assistance recorded in the Issue: {agent_assistance or 'None recorded in the source Issue.'}
- Draft preparation: `scripts/iwb.py prepare-promotion` mechanically synthesized the Issue form; it did not approve promotion.
- Important dissent or changes in direction: Preserve these from the Issue during human review.
'''


def cmd_prepare_promotion(args: argparse.Namespace) -> int:
    if not SLUG_RE.fullmatch(args.slug):
        raise CliError("--slug must use lowercase kebab-case")
    invalid_themes = [theme for theme in args.theme if not THEME_RE.fullmatch(theme)]
    if invalid_themes:
        raise CliError(f"themes must use lowercase kebab-case: {', '.join(invalid_themes)}")

    issue_command = [
        "gh",
        "issue",
        "view",
        str(args.issue),
        "--json",
        "number,title,body,url,author,labels,state",
        *_repo_args(args.repo),
    ]
    issue = _gh_json(issue_command)
    label_names = {label["name"] for label in issue.get("labels", [])}
    if "type:proposal" not in label_names and not args.allow_unlabelled:
        raise CliError(
            f"Issue #{args.issue} is not labelled type:proposal. Use --allow-unlabelled only after manual verification."
        )
    if "status:candidate" not in label_names and not args.allow_non_candidate:
        raise CliError(
            f"Issue #{args.issue} is not labelled status:candidate. Promotion preparation normally follows an explicit human candidate decision; use --allow-non-candidate only when that invitation is recorded elsewhere."
        )

    sections = _parse_issue_form_body(issue.get("body") or "")
    missing_core = [key for key in ("spark", "proposition") if not sections.get(key, "").strip()]
    if missing_core:
        raise CliError(
            "Issue body does not contain the expected Proposal form sections: "
            + ", ".join(missing_core)
        )

    output = args.output or (ROOT / "ideas" / f"{args.slug}.md")
    output = output.resolve()
    try:
        output.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise CliError("promotion drafts must be written inside the repository") from exc

    if output.exists() and not args.force:
        raise CliError(f"refusing to overwrite {output}; use --force after reviewing the existing file")

    promoted_on = args.promoted_on or dt.date.today().isoformat()
    try:
        dt.date.fromisoformat(promoted_on)
    except ValueError as exc:
        raise CliError("--promoted-on must be a valid YYYY-MM-DD date") from exc

    document = _promotion_document(
        issue,
        sections,
        curator=args.curator,
        themes=list(dict.fromkeys(args.theme)),
        extra_contributors=args.contributor,
        promoted_on=promoted_on,
    )

    if args.dry_run:
        print(f"DRY RUN: would write {output.relative_to(ROOT)}")
        print(document)
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(f"Prepared {output.relative_to(ROOT)} from Issue #{args.issue}.")
    print(
        "Human curator action remains required: replace the promotion marker, verify attribution and the promoted_on date, and review every claim before opening the PR."
    )
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    argv = ["--root", str(ROOT)]
    if args.json:
        argv.append("--json")
    return validate_repository.main(argv)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser(
        "create-proposal",
        help="validate, search, preview, and create one agent-prepared Proposal Issue",
    )
    create.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON input following schemas/proposal-input.schema.json",
    )
    create.add_argument("--repo", help="OWNER/REPO; defaults to the current repository")
    create.add_argument("--search-limit", type=int, default=20)
    create.add_argument(
        "--check-only",
        action="store_true",
        help="run searches and print the body without creating an Issue",
    )
    create.add_argument(
        "--confirm-reviewed-search-results",
        action="store_true",
        help="explicitly confirm that open-and-closed search results were reviewed",
    )
    create.add_argument("--dry-run", action="store_true")
    create.set_defaults(func=cmd_create_proposal)

    bootstrap = subparsers.add_parser(
        "bootstrap-labels", help="create or update canonical labels"
    )
    bootstrap.add_argument("--repo", required=True, help="OWNER/REPO")
    bootstrap.add_argument("--dry-run", action="store_true")
    bootstrap.set_defaults(func=cmd_bootstrap_labels)

    search = subparsers.add_parser("search", help="search open and closed Issues")
    search.add_argument("query", help="GitHub Issue search expression or natural query")
    search.add_argument("--repo", help="OWNER/REPO; defaults to the current repository")
    search.add_argument("--limit", type=int, default=100)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    transition = subparsers.add_parser(
        "transition", help="replace the lifecycle status label"
    )
    transition.add_argument("issue", type=int)
    transition.add_argument("status", choices=STATUS_LABELS)
    transition.add_argument("--repo", help="OWNER/REPO; defaults to the current repository")
    transition.add_argument(
        "--human-approved",
        action="store_true",
        help="assert that an identifiable human made a protected lifecycle decision",
    )
    transition.add_argument(
        "--reason",
        help="decision rationale; required for candidate, promoted, dormant, and archived",
    )
    transition.add_argument("--dry-run", action="store_true")
    transition.set_defaults(func=cmd_transition)

    promotion = subparsers.add_parser(
        "prepare-promotion",
        help="draft, but do not approve, a curated idea document from a Proposal Issue",
    )
    promotion.add_argument("issue", type=int)
    promotion.add_argument("--slug", required=True)
    promotion.add_argument("--curator", required=True, help="human curator GitHub handle")
    promotion.add_argument("--repo", help="OWNER/REPO; defaults to the current repository")
    promotion.add_argument(
        "--theme", action="append", default=[], help="repeatable kebab-case theme"
    )
    promotion.add_argument(
        "--contributor",
        action="append",
        default=[],
        help="additional material human contributor; repeat as needed",
    )
    promotion.add_argument("--promoted-on", help="YYYY-MM-DD; defaults to today's local date")
    promotion.add_argument("--output", type=Path)
    promotion.add_argument("--force", action="store_true")
    promotion.add_argument("--allow-unlabelled", action="store_true")
    promotion.add_argument(
        "--allow-non-candidate",
        action="store_true",
        help="prepare despite missing status:candidate only when a human invitation is recorded elsewhere",
    )
    promotion.add_argument("--dry-run", action="store_true")
    promotion.set_defaults(func=cmd_prepare_promotion)

    validate = subparsers.add_parser("validate", help="run repository validation")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=cmd_validate)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "limit") and args.limit < 1:
        parser.error("--limit must be at least 1")
    if hasattr(args, "search_limit") and args.search_limit < 1:
        parser.error("--search-limit must be at least 1")
    try:
        return int(args.func(args))
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
