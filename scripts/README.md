# Repository helpers

The scripts automate deterministic mechanics. They do not evaluate whether an idea is meaningful, distinctive, tasteful, or worthy of promotion.

## Requirements

- Python 3.11 or newer
- GitHub CLI (`gh`) authenticated for commands that operate on GitHub
- no third-party Python packages

## `iwb.py`

```bash
# Validate agent input, repeat open-and-closed searches, and preview
python scripts/iwb.py create-proposal --input proposal.json --check-only

# Create one proposal only after reviewing those results
python scripts/iwb.py create-proposal --input proposal.json \
  --confirm-reviewed-search-results

# Search open and closed proposal memory
python scripts/iwb.py search "quiet coordination"

# Create or update every canonical label
python scripts/iwb.py bootstrap-labels --repo OWNER/ideas-worth-building

# Replace the current lifecycle label
python scripts/iwb.py transition 42 status:grounding

# Protected transitions require a recorded human decision
python scripts/iwb.py transition 42 status:candidate \
  --human-approved \
  --reason "Curator review invited; the remaining question is clearly recorded"

# Draft a curated document after a human has applied status:candidate
python scripts/iwb.py prepare-promotion 42 \
  --slug quiet-coordination \
  --curator @OWNER

# Run local validation
python scripts/iwb.py validate
```

Use `--repo OWNER/REPO` outside a local clone. Add `--dry-run` to mutating commands to inspect the `gh` commands without executing them.

`prepare-promotion` normally requires `type:proposal` and `status:candidate`. The exceptional `--allow-unlabelled` and `--allow-non-candidate` overrides require manual verification; they do not grant an agent decision authority.

## `validate_repository.py`

Checks:

- required repository files, directories, and machine-input contract;
- canonical labels and uniqueness;
- Issue-form classification and integrity wording;
- safe baseline workflow permissions and immutable external Action references;
- restricted front matter and required sections for curated ideas;
- absence of obvious placeholders in promoted documents.

It intentionally does not assign a quality score.
