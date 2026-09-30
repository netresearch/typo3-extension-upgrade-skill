<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# Architecture

## Purpose

This repository is an AI agent skill that provides procedural knowledge for upgrading TYPO3 extensions to newer LTS versions. It consists mostly of structured documentation, configuration templates, and evaluation criteria. The skill ships one executable helper, `scripts/scan-deprecations.sh`; the other scripts in the repository serve its maintenance (see [Scripts and tests](#scripts-and-tests)).

## Component Overview

### Skill Definition (`skills/typo3-extension-upgrade/`)

The core skill package following the Agent Skills specification:

- **SKILL.md**: Entry point loaded by AI agents. Contains the upgrade workflow, tool descriptions, and decision logic.
- **assets/**: Configuration file templates (Rector, Fractor, PHPStan, PHPUnit) that agents copy into target extensions.
- **references/**: Detailed documentation covering version-specific API changes, pre-upgrade checklists, dual-compatibility patterns, and verification criteria.
- **scripts/scan-deprecations.sh**: Report-only grep scan of an extension directory for the deprecated and removed APIs and traps documented in `references/api-changes.md` and `references/api-traps.md`. It reads files and prints matches; it changes nothing and always exits 0 unless the path does not exist.
- **checkpoints.yaml**: Evaluation checkpoint definitions for skill quality scoring.

### Agents (`agents/`)

Specialized agent definitions for sub-tasks (e.g., upgrade-planner for assessment and planning).

### Commands (`commands/`)

Slash command definitions (e.g., `/assess`, `/rector`) that provide shortcut entry points into specific skill workflows.

### Evaluations (`evals/`)

Test cases for validating skill quality and correctness against known upgrade scenarios.

### Build (`Build/`)

Git hooks and utility scripts for repository maintenance (not for target extensions). `Build/hooks/pre-push` runs `Build/Scripts/check-plugin-version.sh`, which fails when a semver tag at `HEAD` differs from the version in `.claude-plugin/plugin.json`.

### Scripts and tests

- `scripts/verify-harness.sh`: local check of the agent harness (AGENTS.md, docs, workflows, hooks). CI runs its own inline checks through `harness-verify.yml`, not this script.
- `evals/run-ab-test.sh`: compares answers of the `claude` CLI with and without the skill for the prompts in `evals/evals.json`. It runs paid model requests and is started by hand only.
- `tests/test_scripts.py`: behaviour tests for `scan-deprecations.sh`, `check-plugin-version.sh` with the pre-push hook, and `verify-harness.sh`. The `Skill Tests` workflow (`.github/workflows/tests.yml`) runs them.

## Data Flow

1. Agent loads `SKILL.md` when upgrade intent is detected
2. Skill references `references/` docs for version-specific migration details
3. Agent applies `assets/` templates to the target extension
4. Agent follows the workflow steps, running tools in the target extension context

## Key Design Decisions

- **No runtime dependencies**: the skill is documentation consumed by AI agents, plus one scan script that needs only Bash and grep.
- **Version-specific references**: Each TYPO3 version pair has dedicated migration docs to keep instructions precise.
- **Template-based configs**: Assets are starting points, not rigid configs -- agents adapt them per extension.
