#!/usr/bin/env python3
"""Validate the mechanical invariants of the Ideas Worth Building repository.

This validator is intentionally dependency-free. It checks document shape, metadata,
labels, forms, links, and workflow safety baselines. It does not score proposal quality
or make curatorial decisions.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote

REQUIRED_ROOT_FILES = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "SCHEMA.md",
    "SETUP.md",
    "SECURITY.md",
    "LICENSE",
    "CODE_OF_CONDUCT.md",
)

REQUIRED_DIRECTORIES = (
    "principles",
    "ideas",
    "patterns",
    "decisions",
    "archive",
    ".github/ISSUE_TEMPLATE",
    ".github/agent-templates",
    ".github/workflows",
    "scripts",
    "tests",
    "schemas",
    "LICENSES",
)

REQUIRED_TYPE_LABELS = {
    "type:proposal",
    "type:problem",
    "type:governance",
}

REQUIRED_STATUS_LABELS = {
    "status:spark",
    "status:exploring",
    "status:grounding",
    "status:candidate",
    "status:experimenting",
    "status:promoted",
    "status:dormant",
    "status:archived",
}

REQUIRED_ORIGIN_LABELS = {
    "origin:problem",
    "origin:capability",
    "origin:experience",
    "origin:observation",
    "origin:prototype",
    "origin:combination",
    "origin:unknown",
}

ALLOWED_ORIGINS = {label.removeprefix("origin:") for label in REQUIRED_ORIGIN_LABELS}

REQUIRED_IDEA_METADATA = (
    "schema_version",
    "title",
    "source_issue",
    "status",
    "promoted_on",
    "origins",
    "themes",
    "contributors",
    "promoted_by",
)

REQUIRED_IDEA_HEADINGS = (
    "## The spark",
    "## The proposition",
    "## Who or what it serves",
    "## Why it matters",
    "## Current behaviours and alternatives",
    "## The non-obvious insight",
    "## What would make an implementation excellent",
    "## Evidence, assumptions, and speculation",
    "## Known uncertainties and strongest counterargument",
    "## Risk of solutionism",
    "## Smallest meaningful exploration",
    "## Promotion case",
    "## History and attribution",
)

REQUIRED_AGENT_TEMPLATES = (
    "contribution-disclosure.md",
    "critique.md",
    "duplicate-review.md",
    "experiment-design.md",
    "promotion-review.md",
    "proposal-intake.md",
    "research-note.md",
    "synthesis.md",
)

SKIP_LINK_DIRECTORIES = {".git", ".venv", "venv", "__pycache__"}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", flags=re.DOTALL)
HEADING_RE = re.compile(r"^##\s+.+$", flags=re.MULTILINE)
THEME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_COLOR_RE = re.compile(r"^[0-9A-Fa-f]{6}$")
HANDLE_RE = re.compile(r"^@[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PLACEHOLDER_MARKERS = (
    "[human curator required]",
    "<human curator",
    "@todo",
    "@owner",
    "@human-curator",
    "replace this",
    "tbd",
    "todo:",
)


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str
    line: int | None = None

    def format(self, root: Path) -> str:
        try:
            relative = self.path.relative_to(root)
        except ValueError:
            relative = self.path
        location = f"{relative}:{self.line}" if self.line else str(relative)
        return f"{location}: {self.message}"


class FrontMatterError(ValueError):
    """Raised when restricted front matter is malformed."""


def _parse_scalar(value: str, *, line_number: int) -> Any:
    """Parse the intentionally small JSON-compatible YAML value subset."""

    value = value.strip()
    if not value:
        raise FrontMatterError(f"line {line_number}: metadata values may not be empty")

    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise FrontMatterError(
            f"line {line_number}: use JSON-compatible values, quoted strings, and arrays: {exc.msg}"
        ) from exc


def parse_front_matter(text: str) -> tuple[dict[str, Any], str, int]:
    """Return metadata, Markdown body, and the first body line number.

    Front matter must use one key per line and JSON-compatible values. This is a
    deliberate restricted subset that avoids a runtime YAML dependency.
    """

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontMatterError("document must start with '---' front matter")

    closing_index: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise FrontMatterError("front matter is missing its closing '---'")

    metadata: dict[str, Any] = {}
    for index, raw_line in enumerate(lines[1:closing_index], start=2):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise FrontMatterError(f"line {index}: expected 'key: value'")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise FrontMatterError(f"line {index}: invalid metadata key {key!r}")
        if key in metadata:
            raise FrontMatterError(f"line {index}: duplicate metadata key {key!r}")
        metadata[key] = _parse_scalar(raw_value, line_number=index)

    body = "\n".join(lines[closing_index + 1 :])
    return metadata, body, closing_index + 2


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _line_number(text: str, character_offset: int, body_start_line: int = 1) -> int:
    return body_start_line + text.count("\n", 0, character_offset)


def _substantive_text(section: str) -> str:
    without_comments = HTML_COMMENT_RE.sub("", section)
    without_markdown_noise = re.sub(r"[`*_>#\-\[\]()]", " ", without_comments)
    return " ".join(without_markdown_noise.split())


def _contains_placeholder(text: str) -> str | None:
    lowered = text.casefold()
    for marker in PLACEHOLDER_MARKERS:
        if marker in lowered:
            return marker
    return None


def _validate_handle_list(
    path: Path,
    key: str,
    value: Any,
    *,
    require_nonempty: bool,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return [ValidationIssue(path, f"{key} must be a JSON-style array of GitHub handles")]
    if require_nonempty and not value:
        issues.append(ValidationIssue(path, f"{key} must contain at least one GitHub handle"))
    for handle in value:
        if not HANDLE_RE.fullmatch(handle):
            issues.append(ValidationIssue(path, f"{key} contains invalid GitHub handle {handle!r}"))
        placeholder = _contains_placeholder(handle)
        if placeholder:
            issues.append(ValidationIssue(path, f"{key} contains placeholder {handle!r}"))
    if len(value) != len(set(value)):
        issues.append(ValidationIssue(path, f"{key} contains duplicate handles"))
    return issues


def validate_idea_document(path: Path, *, archived: bool = False) -> list[ValidationIssue]:
    """Validate one promoted or archived idea document."""

    issues: list[ValidationIssue] = []
    text = path.read_text(encoding="utf-8")

    try:
        metadata, body, body_start_line = parse_front_matter(text)
    except FrontMatterError as exc:
        return [ValidationIssue(path, str(exc))]

    for key in REQUIRED_IDEA_METADATA:
        if key not in metadata:
            issues.append(ValidationIssue(path, f"missing required metadata key {key!r}"))

    if issues:
        return issues

    if metadata["schema_version"] != 1:
        issues.append(ValidationIssue(path, "schema_version must be the integer 1"))

    title = metadata["title"]
    if not isinstance(title, str) or not title.strip():
        issues.append(ValidationIssue(path, "title must be a non-empty quoted string"))

    source_issue = metadata["source_issue"]
    if isinstance(source_issue, bool) or not isinstance(source_issue, int) or source_issue <= 0:
        issues.append(ValidationIssue(path, "source_issue must be a positive integer"))

    if metadata["status"] != "promoted":
        issues.append(ValidationIssue(path, 'status must remain "promoted" in curated documents'))

    if not _valid_date(metadata["promoted_on"]):
        issues.append(ValidationIssue(path, "promoted_on must be a valid quoted YYYY-MM-DD date"))

    origins = metadata["origins"]
    if not isinstance(origins, list) or not all(isinstance(item, str) for item in origins):
        issues.append(ValidationIssue(path, "origins must be a JSON-style array of strings"))
    else:
        invalid_origins = sorted(set(origins) - ALLOWED_ORIGINS)
        if invalid_origins:
            issues.append(
                ValidationIssue(path, f"origins contains unsupported values: {', '.join(invalid_origins)}")
            )
        if len(origins) != len(set(origins)):
            issues.append(ValidationIssue(path, "origins contains duplicate values"))
        if "unknown" in origins and len(origins) > 1:
            issues.append(ValidationIssue(path, "origin 'unknown' may not be combined with other origins"))

    themes = metadata["themes"]
    if not isinstance(themes, list) or not all(isinstance(item, str) for item in themes):
        issues.append(ValidationIssue(path, "themes must be a JSON-style array of strings"))
    else:
        for theme in themes:
            if not THEME_RE.fullmatch(theme):
                issues.append(
                    ValidationIssue(path, f"theme {theme!r} must use lowercase kebab-case")
                )
        if len(themes) != len(set(themes)):
            issues.append(ValidationIssue(path, "themes contains duplicate values"))

    issues.extend(
        _validate_handle_list(path, "contributors", metadata["contributors"], require_nonempty=True)
    )
    issues.extend(
        _validate_handle_list(path, "promoted_by", metadata["promoted_by"], require_nonempty=True)
    )

    if archived:
        if not _valid_date(metadata.get("archived_on")):
            issues.append(ValidationIssue(path, "archived_on must be a valid quoted YYYY-MM-DD date"))
        archive_reason = metadata.get("archive_reason")
        if not isinstance(archive_reason, str) or not archive_reason.strip():
            issues.append(ValidationIssue(path, "archive_reason must be a non-empty quoted string"))
        if archive_reason == "superseded":
            superseded_by = metadata.get("superseded_by")
            if not isinstance(superseded_by, str) or not superseded_by.startswith("ideas/"):
                issues.append(
                    ValidationIssue(
                        path,
                        "superseded archives must provide superseded_by as an ideas/... path",
                    )
                )

    heading_matches = list(HEADING_RE.finditer(body))
    heading_names = [match.group(0).strip() for match in heading_matches]

    previous_position = -1
    for required_heading in REQUIRED_IDEA_HEADINGS:
        occurrences = [i for i, name in enumerate(heading_names) if name == required_heading]
        if not occurrences:
            issues.append(ValidationIssue(path, f"missing required heading {required_heading!r}"))
            continue
        if len(occurrences) > 1:
            issues.append(ValidationIssue(path, f"heading appears more than once: {required_heading!r}"))
            continue
        position = occurrences[0]
        if position <= previous_position:
            issues.append(ValidationIssue(path, f"heading is out of order: {required_heading!r}"))
        previous_position = position

    if not any(line.startswith("# ") for line in body.splitlines()):
        issues.append(ValidationIssue(path, "document must contain one level-one title heading"))

    for index, required_heading in enumerate(REQUIRED_IDEA_HEADINGS):
        matching = [match for match in heading_matches if match.group(0).strip() == required_heading]
        if len(matching) != 1:
            continue
        start = matching[0].end()
        later_headings = [match for match in heading_matches if match.start() > matching[0].start()]
        end = later_headings[0].start() if later_headings else len(body)
        section = body[start:end]
        substantive = _substantive_text(section)
        if len(substantive) < 20:
            issues.append(
                ValidationIssue(
                    path,
                    f"section {required_heading!r} needs substantive text",
                    _line_number(body, matching[0].start(), body_start_line),
                )
            )
        placeholder = _contains_placeholder(section)
        if placeholder:
            issues.append(
                ValidationIssue(
                    path,
                    f"section {required_heading!r} contains unresolved placeholder {placeholder!r}",
                    _line_number(body, matching[0].start(), body_start_line),
                )
            )

    history_match = next(
        (match for match in heading_matches if match.group(0).strip() == "## History and attribution"),
        None,
    )
    if history_match and isinstance(source_issue, int):
        history = body[history_match.end() :]
        if f"#{source_issue}" not in history and f"/issues/{source_issue}" not in history:
            issues.append(
                ValidationIssue(
                    path,
                    f"History and attribution must link or name source Issue #{source_issue}",
                    _line_number(body, history_match.start(), body_start_line),
                )
            )

    return issues


def validate_labels(path: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [ValidationIssue(path, f"cannot parse label registry: {exc}")]

    if not isinstance(data, list):
        return [ValidationIssue(path, "label registry must be a JSON array")]

    names: list[str] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            issues.append(ValidationIssue(path, f"label entry {index} must be an object"))
            continue
        name = item.get("name")
        color = item.get("color")
        description = item.get("description")
        if not isinstance(name, str) or not name.strip():
            issues.append(ValidationIssue(path, f"label entry {index} has no valid name"))
            continue
        names.append(name)
        if not isinstance(color, str) or not HEX_COLOR_RE.fullmatch(color):
            issues.append(ValidationIssue(path, f"label {name!r} must use a six-digit hex color"))
        if not isinstance(description, str) or not description.strip():
            issues.append(ValidationIssue(path, f"label {name!r} must have a description"))
        elif len(description) > 100:
            issues.append(ValidationIssue(path, f"label {name!r} description exceeds 100 characters"))
        unknown_keys = sorted(set(item) - {"name", "color", "description"})
        if unknown_keys:
            issues.append(
                ValidationIssue(path, f"label {name!r} has unsupported keys: {', '.join(unknown_keys)}")
            )

    duplicates = sorted(name for name in set(names) if names.count(name) > 1)
    for duplicate in duplicates:
        issues.append(ValidationIssue(path, f"duplicate label name {duplicate!r}"))

    present = set(names)
    for required in sorted(REQUIRED_TYPE_LABELS | REQUIRED_STATUS_LABELS | REQUIRED_ORIGIN_LABELS):
        if required not in present:
            issues.append(ValidationIssue(path, f"missing canonical label {required!r}"))

    return issues


def validate_issue_forms(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    forms = {
        root / ".github/ISSUE_TEMPLATE/proposal.yml": ("type:proposal", "status:spark"),
        root / ".github/ISSUE_TEMPLATE/problem.yml": ("type:problem", "status:spark"),
        root / ".github/ISSUE_TEMPLATE/governance.yml": ("type:governance", "status:spark"),
    }

    for path, expected_labels in forms.items():
        if not path.exists():
            issues.append(ValidationIssue(path, "required Issue form is missing"))
            continue
        text = path.read_text(encoding="utf-8")
        for label in expected_labels:
            if label not in text:
                issues.append(ValidationIssue(path, f"Issue form must apply {label!r}"))
        if "validations:" not in text or "required: true" not in text:
            issues.append(ValidationIssue(path, "Issue form must contain explicit required fields"))

    proposal_path = root / ".github/ISSUE_TEMPLATE/proposal.yml"
    if proposal_path.exists():
        text = proposal_path.read_text(encoding="utf-8")
        required_phrases = (
            "Duplicate and adjacency review",
            "The spark",
            "The proposition",
            "Who or what might benefit, and why",
            "Current behaviours and alternatives",
            "The non-obvious insight",
            "What would make an implementation excellent",
            "Known uncertainties",
            "solution looking for a problem",
            "Smallest meaningful exploration or experiment",
            "Contributions currently wanted",
            "I have not invented users",
            "AI or agent assistance",
        )
        for phrase in required_phrases:
            if phrase not in text:
                issues.append(ValidationIssue(proposal_path, f"proposal form is missing {phrase!r}"))

        # The proposal is intentionally open at entry. These two text areas are the only
        # substantive proposal fields that should be mandatory.
        for field_id in (
            "duplicate-review",
            "beneficiaries",
            "alternatives",
            "insight",
            "excellence",
            "uncertainties",
        ):
            block_match = re.search(
                rf"(?ms)^\s*- type: textarea\s+id: {re.escape(field_id)}\b(.*?)(?=^\s*- type:|\Z)",
                text,
            )
            if block_match and "required: true" in block_match.group(1):
                issues.append(
                    ValidationIssue(
                        proposal_path,
                        f"optional proposal field {field_id!r} must not be required at entry",
                    )
                )

    config_path = root / ".github/ISSUE_TEMPLATE/config.yml"
    if not config_path.exists():
        issues.append(ValidationIssue(config_path, "Issue template configuration is missing"))
    elif "blank_issues_enabled: false" not in config_path.read_text(encoding="utf-8"):
        issues.append(ValidationIssue(config_path, "blank Issues should be disabled"))

    return issues



def validate_agent_contract(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    schema_path = root / "schemas/proposal-input.schema.json"
    example_path = root / ".github/agent-templates/proposal-input.example.json"

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(ValidationIssue(schema_path, f"cannot parse proposal input schema: {exc}"))
        schema = None

    try:
        example = json.loads(example_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(ValidationIssue(example_path, f"cannot parse proposal input example: {exc}"))
        example = None

    if isinstance(schema, dict):
        required = set(schema.get("required", []))
        for key in (
            "title",
            "spark",
            "proposition",
            "origins",
            "duplicate_search",
            "agent_disclosure",
        ):
            if key not in required:
                issues.append(ValidationIssue(schema_path, f"schema must require {key!r}"))
        if schema.get("additionalProperties") is not False:
            issues.append(
                ValidationIssue(schema_path, "proposal input schema must reject unknown top-level fields")
            )

    if isinstance(schema, dict) and isinstance(example, dict):
        schema_properties = set((schema.get("properties") or {}).keys())
        unknown_example = sorted(set(example) - schema_properties)
        if unknown_example:
            issues.append(
                ValidationIssue(
                    example_path,
                    f"example contains fields absent from schema: {', '.join(unknown_example)}",
                )
            )
        missing_example = sorted(set(schema.get("required", [])) - set(example))
        if missing_example:
            issues.append(
                ValidationIssue(
                    example_path,
                    f"example is missing required fields: {', '.join(missing_example)}",
                )
            )
        duplicate_search = example.get("duplicate_search")
        if not isinstance(duplicate_search, dict) or duplicate_search.get(
            "reviewed_open_and_closed"
        ) is not True:
            issues.append(
                ValidationIssue(
                    example_path,
                    "example must explicitly record review of open and closed Issues",
                )
            )

    return issues

def validate_workflows(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    workflow_dir = root / ".github/workflows"
    for path in sorted(workflow_dir.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if "pull_request_target:" in text:
            issues.append(
                ValidationIssue(path, "pull_request_target is prohibited without a documented security decision")
            )
        if re.search(r"(?m)^permissions:\s*write-all\s*$", text):
            issues.append(ValidationIssue(path, "workflow may not request write-all permissions"))
        if "permissions:" not in text:
            issues.append(ValidationIssue(path, "workflow must declare explicit permissions"))
        uses_refs = re.findall(r"(?m)^\s*(?:-\s*)?uses:\s*([^\s#]+)", text)
        for ref in uses_refs:
            if ref.startswith(("./", "docker://")):
                continue
            if ref.endswith("@main") or ref.endswith("@master"):
                issues.append(ValidationIssue(path, f"action reference must not track a mutable branch: {ref}"))
                continue
            if not re.fullmatch(r"[^@]+@[0-9a-fA-F]{40}", ref):
                issues.append(
                    ValidationIssue(
                        path,
                        f"external action reference must be pinned to a full commit SHA: {ref}",
                    )
                )
    return issues


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if any(part in SKIP_LINK_DIRECTORIES for part in path.parts):
            continue
        yield path


def validate_relative_links(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in _iter_markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw_target = match.group(1).strip()
            # Optional Markdown titles follow a path separated by whitespace. Repository
            # links here do not use spaces in filenames, so splitting is safe and useful.
            target = raw_target.split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if target.startswith(("gh:", "git:")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                issues.append(
                    ValidationIssue(
                        path,
                        f"relative link escapes repository root: {raw_target!r}",
                        _line_number(text, match.start()),
                    )
                )
                continue
            if not candidate.exists():
                issues.append(
                    ValidationIssue(
                        path,
                        f"broken relative link: {raw_target!r}",
                        _line_number(text, match.start()),
                    )
                )
    return issues


def validate_repository(root: Path) -> list[ValidationIssue]:
    root = root.resolve()
    issues: list[ValidationIssue] = []

    for relative in REQUIRED_ROOT_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(ValidationIssue(path, "required repository file is missing"))

    for relative in REQUIRED_DIRECTORIES:
        path = root / relative
        if not path.is_dir():
            issues.append(ValidationIssue(path, "required repository directory is missing"))

    labels_path = root / ".github/labels.json"
    if labels_path.exists():
        issues.extend(validate_labels(labels_path))
    else:
        issues.append(ValidationIssue(labels_path, "canonical label registry is missing"))

    issues.extend(validate_issue_forms(root))
    issues.extend(validate_agent_contract(root))
    issues.extend(validate_workflows(root))

    for template in REQUIRED_AGENT_TEMPLATES:
        path = root / ".github/agent-templates" / template
        if not path.is_file():
            issues.append(ValidationIssue(path, "required agent contribution template is missing"))

    ideas_dir = root / "ideas"
    if ideas_dir.exists():
        for path in sorted(ideas_dir.glob("*.md")):
            if path.name in {"README.md", "_template.md"}:
                continue
            issues.extend(validate_idea_document(path))

    archive_dir = root / "archive"
    if archive_dir.exists():
        for path in sorted(archive_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            issues.extend(validate_idea_document(path, archived=True))

    issues.extend(validate_relative_links(root))
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: parent of scripts/)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable findings")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    issues = validate_repository(root)

    if args.json:
        payload = [
            {
                "path": str(issue.path.relative_to(root)) if issue.path.is_relative_to(root) else str(issue.path),
                "line": issue.line,
                "message": issue.message,
            }
            for issue in issues
        ]
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif issues:
        print(f"Repository validation failed with {len(issues)} finding(s):", file=sys.stderr)
        for issue in issues:
            print(f"- {issue.format(root)}", file=sys.stderr)
    else:
        idea_count = len(
            [
                path
                for path in (root / "ideas").glob("*.md")
                if path.name not in {"README.md", "_template.md"}
            ]
        )
        print(
            "Repository validation passed: "
            f"structure, labels, forms, workflows, links, and {idea_count} curated idea(s)."
        )

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
