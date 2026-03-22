# Architecture

## Purpose

This repository is an AI agent skill that provides procedural knowledge for upgrading TYPO3 extensions to newer LTS versions. It contains no executable code -- only structured documentation, configuration templates, and evaluation criteria.

## Component Overview

### Skill Definition (`skills/typo3-extension-upgrade/`)

The core skill package following the Agent Skills specification:

- **SKILL.md**: Entry point loaded by AI agents. Contains the upgrade workflow, tool descriptions, and decision logic.
- **assets/**: Configuration file templates (Rector, Fractor, PHPStan, PHPUnit) that agents copy into target extensions.
- **references/**: Detailed documentation covering version-specific API changes, pre-upgrade checklists, dual-compatibility patterns, and verification criteria.
- **checkpoints.yaml**: Evaluation checkpoint definitions for skill quality scoring.

### Agents (`agents/`)

Specialized agent definitions for sub-tasks (e.g., upgrade-planner for assessment and planning).

### Commands (`commands/`)

Slash command definitions (e.g., `/assess`, `/rector`) that provide shortcut entry points into specific skill workflows.

### Evaluations (`evals/`)

Test cases for validating skill quality and correctness against known upgrade scenarios.

### Build (`Build/`)

Git hooks and utility scripts for repository maintenance (not for target extensions).

## Data Flow

1. Agent loads `SKILL.md` when upgrade intent is detected
2. Skill references `references/` docs for version-specific migration details
3. Agent applies `assets/` templates to the target extension
4. Agent follows the workflow steps, running tools in the target extension context

## Key Design Decisions

- **Content-only repo**: No runtime dependencies; the skill is pure documentation consumed by AI agents.
- **Version-specific references**: Each TYPO3 version pair has dedicated migration docs to keep instructions precise.
- **Template-based configs**: Assets are starting points, not rigid configs -- agents adapt them per extension.
