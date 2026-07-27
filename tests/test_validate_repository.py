from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import iwb  # noqa: E402
import validate_repository as validator  # noqa: E402


VALID_IDEA = '''---
schema_version: 1
title: "Context-preserving work handoff"
source_issue: 42
status: "promoted"
promoted_on: "2026-07-27"
origins: ["observation", "experience"]
themes: ["knowledge-work", "handoff"]
contributors: ["@author", "@researcher"]
promoted_by: ["@curator"]
---

# Context-preserving work handoff

## The spark

Important working context repeatedly disappears when responsibility moves between people and agents.

## The proposition

Create a compact handoff artifact that preserves decisions, uncertainty, intent, and executable next steps.

## Who or what it serves

It serves teams and technical systems that must continue work without reconstructing every prior conversation.

## Why it matters

A better handoff reduces repeated discovery while making unresolved assumptions and human responsibility visible.

## Current behaviours and alternatives

Teams currently use tickets, chat transcripts, documents, commits, and meetings, each preserving only part of the state.

## The non-obvious insight

The valuable unit is not a summary of content but a transfer of decision state, uncertainty, and authority.

## What would make an implementation excellent

It should be concise, inspectable, source-linked, reversible, and explicit about what an agent may decide next.

## Evidence, assumptions, and speculation

The observed fragmentation is first-hand evidence; cross-team prevalence and measurable benefit remain assumptions to test.

## Known uncertainties and strongest counterargument

The format may become another document nobody maintains; existing issue trackers may already be sufficient with discipline.

## Risk of solutionism

The proposal may overvalue a new artifact when better stewardship of existing tools could solve the same failure.

## Smallest meaningful exploration

Use the format for three real handoffs and compare reconstruction questions with three ordinary handoffs.

## Promotion case

The proposal preserves a distinctive focus on decision-state transfer, has a bounded experiment, and merits continued exploration.

## History and attribution

- Source Issue: #42
- Promotion pull request: #51
- Material contributors: @author, @researcher
'''


class FrontMatterTests(unittest.TestCase):
    def test_parses_restricted_front_matter(self) -> None:
        metadata, body, line = validator.parse_front_matter(VALID_IDEA)
        self.assertEqual(metadata["source_issue"], 42)
        self.assertEqual(metadata["origins"], ["observation", "experience"])
        self.assertIn("## The spark", body)
        self.assertGreater(line, 1)

    def test_rejects_unquoted_plain_yaml(self) -> None:
        text = "---\ntitle: unquoted title\n---\nbody\n"
        with self.assertRaises(validator.FrontMatterError):
            validator.parse_front_matter(text)


class IdeaValidationTests(unittest.TestCase):
    def _validate(self, content: str, *, archived: bool = False) -> list[validator.ValidationIssue]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "idea.md"
            path.write_text(content, encoding="utf-8")
            return validator.validate_idea_document(path, archived=archived)

    def test_valid_promoted_idea(self) -> None:
        self.assertEqual(self._validate(VALID_IDEA), [])

    def test_rejects_placeholder_and_bad_origin(self) -> None:
        content = VALID_IDEA.replace(
            'origins: ["observation", "experience"]',
            'origins: ["unknown", "experience"]',
        ).replace(
            "The proposal preserves a distinctive focus on decision-state transfer, has a bounded experiment, and merits continued exploration.",
            "[HUMAN CURATOR REQUIRED] TODO: replace this.",
        )
        messages = [issue.message for issue in self._validate(content)]
        self.assertTrue(any("unknown" in message for message in messages))
        self.assertTrue(any("placeholder" in message for message in messages))

    def test_rejects_out_of_order_heading(self) -> None:
        first = "## Who or what it serves"
        second = "## Why it matters"
        content = VALID_IDEA.replace(first, "## TEMP", 1).replace(second, first, 1).replace(
            "## TEMP", second, 1
        )
        messages = [issue.message for issue in self._validate(content)]
        self.assertTrue(any("out of order" in message for message in messages))

    def test_archived_idea_requires_archive_metadata(self) -> None:
        messages = [issue.message for issue in self._validate(VALID_IDEA, archived=True)]
        self.assertTrue(any("archived_on" in message for message in messages))
        self.assertTrue(any("archive_reason" in message for message in messages))


class LabelValidationTests(unittest.TestCase):
    def test_actual_label_registry_is_valid(self) -> None:
        self.assertEqual(validator.validate_labels(ROOT / ".github/labels.json"), [])

    def test_duplicate_label_is_rejected(self) -> None:
        labels = json.loads((ROOT / ".github/labels.json").read_text(encoding="utf-8"))
        labels.append(dict(labels[0]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.json"
            path.write_text(json.dumps(labels), encoding="utf-8")
            messages = [issue.message for issue in validator.validate_labels(path)]
        self.assertTrue(any("duplicate label" in message for message in messages))


class HelperTests(unittest.TestCase):
    def test_issue_form_parser(self) -> None:
        body = """### The spark\nAn observation\n\n### The proposition\nBuild the smallest useful thing\n"""
        self.assertEqual(
            iwb._parse_issue_form_body(body),
            {"spark": "An observation", "proposition": "Build the smallest useful thing"},
        )

    def test_origin_parser(self) -> None:
        self.assertEqual(
            iwb._origins_from_form("New capability\nObservation or emerging pattern"),
            ["capability", "observation"],
        )

    def test_protected_transition_requires_human_approval(self) -> None:
        namespace = type(
            "Args",
            (),
            {
                "status": "status:promoted",
                "human_approved": False,
                "reason": None,
                "issue": 42,
                "repo": None,
                "dry_run": False,
            },
        )()
        with self.assertRaises(iwb.CliError):
            iwb.cmd_transition(namespace)

    def test_agent_proposal_example_is_valid(self) -> None:
        payload = iwb.load_proposal_input(
            ROOT / ".github/agent-templates/proposal-input.example.json"
        )
        self.assertEqual(payload["origins"], ["observation"])
        self.assertTrue(payload["duplicate_search"]["reviewed_open_and_closed"])
        rendered = iwb.render_proposal_body(payload)
        self.assertIn("### Duplicate and adjacency review", rendered)
        self.assertIn("Unknown at entry.", rendered)
        self.assertIn("### AI or agent assistance", rendered)
        self.assertIn("- **Remaining uncertainties:**\n  - ", rendered)

    def test_agent_input_rejects_short_title(self) -> None:
        payload = json.loads(
            (ROOT / ".github/agent-templates/proposal-input.example.json").read_text(
                encoding="utf-8"
            )
        )
        payload["title"] = "Idea"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(iwb.CliError):
                iwb.load_proposal_input(path)

    def test_agent_input_requires_delta_for_close_match(self) -> None:
        payload = json.loads(
            (ROOT / ".github/agent-templates/proposal-input.example.json").read_text(
                encoding="utf-8"
            )
        )
        payload["duplicate_search"]["closest_issues"] = [7]
        payload["duplicate_search"]["distinctive_delta"] = None
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(iwb.CliError):
                iwb.load_proposal_input(path)

    def test_candidate_status_is_reserved_for_proposals(self) -> None:
        namespace = type(
            "Args",
            (),
            {
                "status": "status:candidate",
                "human_approved": True,
                "reason": "A human curator explicitly invited focused review.",
                "issue": 7,
                "repo": None,
                "dry_run": False,
            },
        )()
        issue = {
            "number": 7,
            "title": "A standalone problem",
            "url": "https://example.invalid/issues/7",
            "state": "OPEN",
            "labels": [
                {"name": "type:problem"},
                {"name": "status:grounding"},
            ],
        }
        with mock.patch.object(iwb, "_gh_json", return_value=issue):
            with self.assertRaises(iwb.CliError):
                iwb.cmd_transition(namespace)

    def test_promoted_status_requires_closed_source_issue(self) -> None:
        namespace = type(
            "Args",
            (),
            {
                "status": "status:promoted",
                "human_approved": True,
                "reason": "Promotion pull request #19 was approved by a human curator.",
                "issue": 8,
                "repo": None,
                "dry_run": False,
            },
        )()
        issue = {
            "number": 8,
            "title": "A proposal",
            "url": "https://example.invalid/issues/8",
            "state": "OPEN",
            "labels": [
                {"name": "type:proposal"},
                {"name": "status:candidate"},
            ],
        }
        with mock.patch.object(iwb, "_gh_json", return_value=issue):
            with self.assertRaises(iwb.CliError):
                iwb.cmd_transition(namespace)

    def test_promotion_draft_remains_explicitly_unapproved(self) -> None:
        issue = {
            "number": 42,
            "title": "A careful idea",
            "url": "https://github.com/example/repo/issues/42",
            "author": {"login": "author"},
        }
        sections = {
            "spark": "A real observation.",
            "proposition": "Create a bounded response.",
            "beneficiaries": "A technical practice may benefit because state is otherwise lost.",
            "alternatives": "People use documents and memory today.",
            "insight": "Transfer decision state rather than raw content.",
            "excellence": "It must be source-linked and reversible.",
            "uncertainties": "Whether the artifact will be maintained.",
            "solutionism": "A new format may be unnecessary.",
            "experiment": "Try it in three real handoffs.",
            "sources": "No external claims yet.",
        }
        result = iwb._promotion_document(
            issue,
            sections,
            curator="@curator",
            themes=["handoff"],
            extra_contributors=[],
            promoted_on="2026-07-27",
        )
        self.assertIn("[HUMAN CURATOR REQUIRED]", result)
        self.assertIn("Source Issue: [#42]", result)
        self.assertIn('promoted_by: ["@curator"]', result)

    def test_promotion_preparation_normally_requires_candidate(self) -> None:
        namespace = type(
            "Args",
            (),
            {
                "slug": "careful-idea",
                "theme": [],
                "issue": 42,
                "repo": None,
                "allow_unlabelled": False,
                "allow_non_candidate": False,
            },
        )()
        issue = {
            "number": 42,
            "title": "A careful idea",
            "body": "### The spark\nObserved.\n\n### The proposition\nExplore it.",
            "url": "https://example.invalid/issues/42",
            "author": {"login": "author"},
            "state": "OPEN",
            "labels": [{"name": "type:proposal"}, {"name": "status:grounding"}],
        }
        with mock.patch.object(iwb, "_gh_json", return_value=issue):
            with self.assertRaises(iwb.CliError):
                iwb.cmd_prepare_promotion(namespace)


class WorkflowValidationTests(unittest.TestCase):
    def _validate(self, workflow: str) -> list[validator.ValidationIssue]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow_dir = root / ".github/workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "test.yml").write_text(workflow, encoding="utf-8")
            return validator.validate_workflows(root)

    def test_rejects_external_action_tag(self) -> None:
        workflow = """name: test
permissions:
  contents: read
jobs:
  test:
    steps:
      - uses: actions/checkout@v7
"""
        messages = [issue.message for issue in self._validate(workflow)]
        self.assertTrue(any("full commit SHA" in message for message in messages))

    def test_accepts_full_action_sha_and_local_action(self) -> None:
        workflow = """name: test
permissions:
  contents: read
jobs:
  test:
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
      - uses: ./local-action
"""
        self.assertEqual(self._validate(workflow), [])


class RepositoryIntegrationTests(unittest.TestCase):
    def test_scaffold_validates(self) -> None:
        issues = validator.validate_repository(ROOT)
        self.assertEqual([issue.format(ROOT) for issue in issues], [])


if __name__ == "__main__":
    unittest.main()
