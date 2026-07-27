# Repository Setup

This scaffold is ready to publish as `ThomasRohde/ideas-worth-building`.

## Prerequisites

- Git
- GitHub CLI (`gh`) authenticated to the intended account
- Python 3.11 or newer

Verify:

```bash
gh auth status
python --version
```

## 1. Validate locally

From the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

The tools have no third-party Python dependencies.

## 2. Initialize and publish

```bash
git init -b main
git add .
git commit -m "Initial Ideas Worth Building repository"

gh repo create ThomasRohde/ideas-worth-building \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description="A curated public workshop for discovering and refining project ideas worth building"
```

On PowerShell, place the command on one line or replace `\` with the PowerShell continuation character.

## 3. Configure repository features

Issues are core. Discussions, Projects, and the wiki are not required.

```bash
gh repo edit ThomasRohde/ideas-worth-building \
  --enable-issues=true \
  --enable-discussions=false \
  --enable-projects=false \
  --enable-wiki=false \
  --enable-squash-merge=true \
  --enable-merge-commit=false \
  --enable-rebase-merge=false \
  --delete-branch-on-merge=true \
  --allow-update-branch=true \
  --add-topic=ideas \
  --add-topic=collaboration \
  --add-topic=agentic-coding \
  --add-topic=product-thinking \
  --add-topic=design
```

Discussions can be enabled later if the community develops a need for broad conversation that does not belong to a proposal, problem, governance Issue, or pull request.

## 4. Enable private vulnerability reporting

The repository includes `SECURITY.md`. Enable GitHub's private reporting channel so contributors do not have to disclose sensitive details in public Issues:

```bash
gh api --method PUT \
  repos/ThomasRohde/ideas-worth-building/private-vulnerability-reporting
```

Alternatively, enable **Private vulnerability reporting** under repository Settings → Security → Advanced Security.

## 5. Create canonical labels

Issue forms only auto-apply labels that already exist. Bootstrap them immediately after creating the repository:

```bash
python scripts/iwb.py bootstrap-labels \
  --repo ThomasRohde/ideas-worth-building
```

The command is idempotent: it creates missing labels and updates descriptions and colours for existing labels.

Review:

```bash
gh label list --repo ThomasRohde/ideas-worth-building --limit 100
```

You may delete unrelated GitHub default labels after confirming they are not useful. Keep `duplicate`, `good first issue`, and `help wanted` only if they support actual contribution work.

## 6. Repository rules

Create a branch ruleset for `main` in GitHub Settings → Rules → Rulesets.

Recommended initial rules:

- require a pull request before merging;
- require the `validate` check produced by the `Validate repository` workflow;
- require conversation resolution;
- block force pushes;
- block branch deletion;
- allow repository administrators to bypass only for emergencies;
- do not require an approving review while there is only one human curator.

Once a second active curator exists, require one Code Owner approval for changes under `ideas/`, `principles/`, `GOVERNANCE.md`, and `SCHEMA.md`.

Rulesets are available for public repositories on GitHub Free. Keep workflow token permissions read-only unless a future workflow has a narrowly justified need to write.

## 7. Repository About text

Suggested description:

> A curated public workshop for discovering and refining project ideas worth building.

Suggested website: leave blank initially.

Suggested topics:

```text
ideas, collaboration, agentic-coding, product-thinking, design, open-innovation
```

## 8. Pin orientation Issues

After labels exist, consider opening and pinning two `type:governance` Issues:

1. **How to contribute without generating noise** — links to the principles, proposal form, and agent rules.
2. **What should the first curation cycle teach us?** — collects observed process failures before adding more automation.

Do not seed the repository with a large generated list of proposals. A small number of genuinely held ideas is a better opening corpus.

## 9. First promotion dry run

Before inviting broad contribution:

1. open one real proposal through the Issue form or the two-step `create-proposal` machine path;
2. add one research or critique contribution;
3. revise the Issue body;
4. move it through exploration and apply `status:candidate` with a recorded human rationale when it is ready for focused review;
5. run `python scripts/iwb.py prepare-promotion ISSUE --slug SLUG --curator @ThomasRohde` on a branch;
6. review the resulting document against the promotion boundary;
7. open a draft PR;
8. merge only if the idea genuinely clears the bar.

This dry run tests the process without lowering the curation standard merely to populate `ideas/`.

## 10. Optional native issue types

GitHub custom issue types are defined at the organization level. If the repository later moves into an organization, native `Proposal`, `Problem`, and `Governance` types may be added.

Keep `type:*` labels canonical even then because:

- they work in personal repositories;
- they are visible through all Issue APIs and older clients;
- they make forks and migrations portable;
- they avoid coupling the repository schema to organization administration.

## 11. Security notes

The validation workflow uses the `pull_request` event, read-only contents permission, and no secrets. It intentionally does not use `pull_request_target` or execute downloaded Issue attachments.

GitHub Actions are pinned to verified full commit SHAs, with release versions recorded in comments. Dependabot checks monthly for action updates; review the referenced release and resulting SHA before merging.
