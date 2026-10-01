<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# TYPO3 Extension Upgrade Skill

A Claude Code skill for systematically upgrading TYPO3 extensions to newer LTS versions.

**Developed by [Netresearch DTT GmbH](https://www.netresearch.de/)**

## 🔌 Compatibility

This is an **Agent Skill** following the [open standard](https://agentskills.io) originally developed by Anthropic and released for cross-platform use.

**Supported Platforms:**
- ✅ Claude Code (Anthropic)
- ✅ Cursor
- ✅ GitHub Copilot
- ✅ Other skills-compatible AI agents

> Skills are portable packages of procedural knowledge that work across any AI agent supporting the Agent Skills specification.


## Overview

This skill guides extension developers through upgrading TYPO3 extensions (third-party or custom) to newer TYPO3 LTS versions with modern PHP compatibility. It covers:

- **Extension Scanner** - Backend module for diagnosing deprecated/removed APIs
- **Rector** - Automated PHP code migrations
- **Fractor** - Automated non-PHP file migrations (FlexForms, TypoScript, YAML, Fluid)
- **PHPStan** - Static analysis
- **PHPUnit** - Testing framework setup

## Scope

This skill is for **extension developers** upgrading extension code. It does NOT cover:
- Upgrading TYPO3 project installations
- TYPO3 core upgrades
- Site/instance migrations

## Supported Upgrade Paths

| From | To | Status |
|------|-----|--------|
| v7 | v8 | Documented |
| v8 | v9 | Documented |
| v9 | v10 | Documented |
| v10 | v11 | Documented |
| v11 | v12 | Documented |
| v12 | v13 | Documented |
| v13 | v14 | Monitoring |
| v12 | v12+v13 (dual) | Documented |

## Installation

### Marketplace (Recommended)

Add the [Netresearch marketplace](https://github.com/netresearch/claude-code-marketplace) once, then browse and install skills:

```bash
# Claude Code
/plugin marketplace add netresearch/claude-code-marketplace
/plugin install typo3-extension-upgrade@netresearch-claude-code-marketplace
```

### Without a marketplace

Since Claude Code 2.1.157 a plugin directory under your personal skills directory loads on its own, including the commands and agents this repo ships:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/netresearch/typo3-extension-upgrade-skill.git \
  ~/.claude/skills/typo3-extension-upgrade
```

It loads as `typo3-extension-upgrade@skills-dir` on the next session. Update with `git -C ~/.claude/skills/typo3-extension-upgrade pull` and start a new session; remove it by deleting the directory. This route has no `claude plugin update`.

### npx ([skills.sh](https://skills.sh))

Install with any [Agent Skills](https://agentskills.io)-compatible agent:

```bash
npx skills add https://github.com/netresearch/typo3-extension-upgrade-skill --skill typo3-extension-upgrade
```

> **Limitation:** `npx skills` installs `SKILL.md`-based skills only. This repo also ships `agents`, `commands`, which it does not install — use the marketplace or the skills directory for those.

### Download Release

Download the [latest release](https://github.com/netresearch/typo3-extension-upgrade-skill/releases/latest) and extract to your agent's skills directory.

### Git Clone

```bash
git clone https://github.com/netresearch/typo3-extension-upgrade-skill.git
```

### Composer (PHP Projects)

```bash
composer require netresearch/typo3-extension-upgrade-skill
```

Requires [netresearch/composer-agent-skill-plugin](https://github.com/netresearch/composer-agent-skill-plugin).
## Usage

The skill activates automatically when Claude detects:
- TYPO3 extension upgrade requests
- Compatibility issues with newer TYPO3 versions
- Extension modernization tasks

Example prompts:
- "Upgrade this extension to TYPO3 v13"
- "Make this extension compatible with TYPO3 12 and 13"
- "Fix the deprecated API usage in this TYPO3 extension"

## Contents

```
typo3-extension-upgrade-skill/
├── README.md                          # This file
├── agents/upgrade-planner.md          # Upgrade planning agent
├── commands/                          # /assess and /rector slash commands
└── skills/typo3-extension-upgrade/
    ├── SKILL.md                       # Main skill instructions
    ├── checkpoints.yaml               # Assessment checkpoints
    ├── assets/                        # Configuration templates
    │   ├── rector.php                 # Rector configuration
    │   ├── fractor.php                # Fractor configuration
    │   ├── phpstan.neon               # PHPStan configuration
    │   ├── phpunit.xml                # PHPUnit configuration
    │   └── .php-cs-fixer.php          # PHP-CS-Fixer configuration
    ├── references/                    # Detailed documentation (14 files)
    │   ├── api-changes.md             # Version-specific API migrations (v7-v14)
    │   ├── pre-upgrade.md             # Pre-upgrade checklist
    │   └── ...                        # Version guides, dual compatibility, verification, troubleshooting
    └── scripts/
        └── scan-deprecations.sh       # Report-only grep scan for deprecated APIs and traps
```

## Key Resources

### Official TYPO3 Changelogs

- [v14 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-14.html)
- [v13 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-13.html)
- [v12 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-12.html)
- [v11 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-11.html)

### Tools

- [TYPO3 Rector](https://github.com/sabbelasichon/typo3-rector) - PHP migrations
- [TYPO3 Fractor](https://github.com/andreaswolf/fractor) - Non-PHP migrations
- [Extension Scanner](https://docs.typo3.org/m/typo3/reference-coreapi/main/en-us/ExtensionArchitecture/HowTo/UpdateExtensions/ExtensionScanner.html) - API diagnostics

## Contributing

Changes are proposed as pull requests against `main`. New or changed behaviour of a script needs a test in `tests/test_scripts.py` in the same pull request.

### Tests

`tests/test_scripts.py` holds the behaviour tests for the shell scripts. It uses the Python standard library only and needs `python3`, `bash`, GNU `grep` and `git`:

```bash
python3 tests/test_scripts.py
```

What the tests cover:

- `skills/typo3-extension-upgrade/scripts/scan-deprecations.sh`: each of the 45 checks against a fixture only it should match, negative cases, the summaries, a missing path and the default target.
- `Build/Scripts/check-plugin-version.sh` and the `Build/hooks/pre-push` hook that calls it: untagged, matching, mismatching and non-semver tags in a temporary git repository.
- `scripts/verify-harness.sh`: harness layouts from empty to complete, over-long `AGENTS.md`, broken references, undocumented composer scripts, GitHub annotation output and invalid arguments.

`evals/run-ab-test.sh` has no test: it calls the `claude` CLI, which runs paid model requests.

A passing run prints a dot per test and ends with `OK` and exit code 0. A failure prints `FAIL:` with the test name; for the scan checks the `check=` and `label=` fields name the check function and the heading it should have printed, and the exit code is 1. CI runs the same file in the Skill Tests workflow (`.github/workflows/tests.yml`) on every pull request and every push to `main`.

### Dependencies

- **Skill**: the skill itself has no runtime dependency. `scan-deprecations.sh` needs Bash and GNU `grep` (its patterns use `\|` and `\s`).
- **Composer**: `composer.json` requires `netresearch/composer-agent-skill-plugin` for installation through Composer. No `composer.lock` is committed (`.gitignore`).
- **Development and CI tools**: pre-commit hooks are pinned by `rev:` in `.pre-commit-config.yaml`. CI tools come from the shared workflows in `netresearch/.github`, `netresearch/skill-repo-skill` and `netresearch/typo3-ci-workflows`, which pin every action by commit SHA.
- **Updates**: Renovate (`renovate.json`, `config:recommended` with the `pre-commit` manager enabled) opens update pull requests. For pull requests opened by Renovate or Dependabot, `auto-merge-deps.yml` approves them and enables auto-merge through the shared workflow, unless they carry the label `deps-major` or `deps-no-automerge`; the merge waits for the required checks.
- **Checks**: dependency review and Composer Audit (see below) check dependency changes on pull requests. New dependencies follow the licence and vulnerability rules of the organisation's [handling of dependency and code analysis findings](https://github.com/netresearch/.github/blob/main/SECURITY.md#handling-of-dependency-and-code-analysis-findings).

## Governance and policies

This repository follows the Netresearch organisation policies:

- [Governance](https://github.com/netresearch/.github/blob/main/GOVERNANCE.md): ownership, roles, and how decisions are made and disputes resolved.
- [Roadmap](https://github.com/netresearch/.github/blob/main/ROADMAP.md): planned and explicitly excluded work for the coming year.
- [Handling of dependency and code analysis findings](https://github.com/netresearch/.github/blob/main/SECURITY.md#handling-of-dependency-and-code-analysis-findings): thresholds, deadlines and the exception process for dependency (SCA) and static analysis (SAST) findings.
- [Secret management](https://github.com/netresearch/.github/blob/main/SECURITY.md#secret-management): how CI and release credentials are stored, accessed and rotated.
- [Access roster](https://github.com/netresearch/.github/blob/main/docs/access-roster.md): who holds administrative access to this repository and the organisation.

The security assurance case for this skill (threat model, trust boundaries, countermeasures and limits) is in [docs/SECURITY-ASSURANCE.md](docs/SECURITY-ASSURANCE.md); components and data flow are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Checks that run on pull requests in this repository:

- Every pull request: Skill Validation (`lint.yml`: skill structure, manifest sync, markdownlint, yamllint, actionlint, JSON syntax, ShellCheck, Ruff, checkpoint schema), Eval Validation (`eval-validate.yml`), Skill Tests (`tests.yml`: `tests/test_scripts.py`), the Labeler (`labeler.yml`) and Auto-merge dependency PRs (`auto-merge-deps.yml`, which acts only on Renovate and Dependabot pull requests); configured outside the workflows: CodeQL through GitHub's default setup (`Analyze (actions)`), SonarCloud, the DCO sign-off check, the CodeRabbit review and the Copilot code review that the repository ruleset requests.
- Pull requests to `main`: `security.yml` with Betterleaks (secret scanning), zizmor (workflow static analysis), dependency review (fails on vulnerabilities of severity high or above), Composer Audit and Opengrep SAST (which findings fail the check is set by the [organisation rule](https://github.com/netresearch/.github/blob/main/SECURITY.md#static-analysis-sast)); Harness Verification (`harness-verify.yml`) and Template Drift (`check-template-drift.yml`).
- Secret detection: Betterleaks in `security.yml` on pull requests to `main` and pushes to `main`, and GitHub secret scanning with push protection, which is enabled for this repository.

## Author

**Netresearch DTT GmbH**
[https://www.netresearch.de/](https://www.netresearch.de/)

Netresearch is a Leipzig-based technology company specializing in e-commerce, logistics, and TYPO3 solutions. With extensive experience in TYPO3 extension development and maintenance, Netresearch contributes to the TYPO3 ecosystem through open-source extensions and community involvement.

## License

This project uses split licensing:

- **Code** (scripts, workflows, configs): [MIT](LICENSE-MIT)
- **Content** (skill definitions, documentation, references): [CC-BY-SA-4.0](LICENSE-CC-BY-SA-4.0)

See the individual license files for full terms.

## Credits

Developed and maintained by [Netresearch DTT GmbH](https://www.netresearch.de/).
