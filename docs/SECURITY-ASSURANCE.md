<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# Security Assurance Case

This document states what users of the typo3-extension-upgrade skill can and cannot expect in terms of security, and argues why the expectations hold. Every claim names the file that implements it. Vulnerabilities are reported privately as described in the [organisation security policy](https://github.com/netresearch/.github/blob/main/SECURITY.md).

## What the project ships

| Part | Files | Runs code? |
|------|-------|------------|
| Skill instructions and references | `skills/typo3-extension-upgrade/SKILL.md`, `skills/typo3-extension-upgrade/references/*.md`, `agents/upgrade-planner.md`, `commands/assess.md`, `commands/rector.md` | No. Text an AI agent loads. The text tells the agent which commands to run in the user's extension (see [Actors and trust boundaries](#actors-and-trust-boundaries)). |
| Checkpoints | `skills/typo3-extension-upgrade/checkpoints.yaml` | No. Data read by an assessment runner. |
| Scan script | `skills/typo3-extension-upgrade/scripts/scan-deprecations.sh` | Yes. Bash, run by the user or the agent against an extension directory. |
| Configuration templates | `skills/typo3-extension-upgrade/assets/` | Not in this repository. Rector, Fractor, PHPStan, PHPUnit and PHP-CS-Fixer configuration a user copies into an extension; `rector.php`, `fractor.php` and `.php-cs-fixer.php` are PHP that those tools execute with the user's permissions once copied. |
| Repository tooling | `Build/Scripts/check-plugin-version.sh`, `Build/hooks/pre-push`, `scripts/verify-harness.sh`, `evals/run-ab-test.sh`, `tests/test_scripts.py` | Yes, for maintainers and CI only. |

## Security requirements

1. The scan script only reads the extension it analyses. It does not execute the extension's code, install dependencies, write files or contact the network.
2. The skill and its releases are delivered unmodified from this repository.
3. Changes to `main` are proposed as pull requests, on which the checks listed in [README.md](../README.md#governance-and-policies) run.

## Actors and trust boundaries

- **User**: asks for an upgrade of an extension they chose, or runs the scan script. Trusted: they choose the target directory and approve the agent's actions.
- **AI agent**: loads `SKILL.md`, the references, the agent and command definitions, and follows them. It acts with the user's permissions and the tools the user's agent platform grants.
- **Extension under upgrade**: untrusted input for the scan script, which reads its files with `grep`. For the upgrade workflow it is the user's own code base: `SKILL.md` (Core Workflow, steps 3 to 10) and `commands/rector.md` direct the agent to run `composer update`, `composer install`, `composer require --dev`, Rector, Fractor, PHP-CS-Fixer, PHPStan and PHPUnit inside it. These tools execute code from the extension and its dependencies (Composer plugins and scripts, test code, Rector and Fractor configuration).
- **Maintainers and CI**: change and release this repository.

Boundary 1 lies between the scan script and the analysed extension: file content is data for `grep`, never code. Boundary 2 lies between this repository and the user's machine: releases are built and signed in CI. The upgrade workflow itself does not cross a boundary the user has not already crossed by working on the extension; the skill adds no isolation to it.

## Argument per requirement

### 1. The scan script only reads

- `scan-deprecations.sh` checks that its single argument is a directory (`[[ ! -d "$target" ]]`, exit 1 otherwise) and then runs 45 checks, each made of one or two `grep -r` searches below it (a few filter their result through a second `grep`). Each search is a fixed pattern; the target path is passed quoted as a file argument and is never part of a pattern or a command string.
- It does not call `eval`, `source`, `php`, `composer`, `curl`, `wget` or another network client, and it writes no file: matches go to standard output, `grep` errors to `/dev/null`.
- It is report-only: it exits 0 whether or not a pattern matches.
- `tests/test_scripts.py` runs every one of the 45 checks against its own fixture, the empty and missing-path cases and the default target `.`.

### 2. Delivered content is the reviewed content

- Releases are built by `.github/workflows/release.yml`, which calls the `netresearch/skill-repo-skill` release workflow with `id-token: write` and `attestations: write`. That workflow signs `SHA256SUMS.txt` keyless with `cosign sign-blob` and attests the release archives and checksums with `actions/attest-build-provenance`.
- `Build/hooks/pre-push` (enabled by `.envrc` through `core.hooksPath`) runs `Build/Scripts/check-plugin-version.sh`, which refuses a push where a semver tag at `HEAD` disagrees with the version in `.claude-plugin/plugin.json`. The shared Skill Validation job checks that `plugin.json` and `.claude-plugin/plugin.json` agree.
- `.github/workflows/scorecard.yml` runs OpenSSF Scorecard on `main` and weekly.

### 3. Changes pass automated checks

Every workflow declares `permissions: {}` at the top and grants each job only what its reusable workflow needs. The two workflows that run on `pull_request_target` (`auto-merge-deps.yml`, `labeler.yml`) call shared workflows in `netresearch/.github` that contain no checkout step and run no pull request code; `auto-merge-deps.yml` says so in its header comment and passes only the two merge-app secrets, not `secrets: inherit`. The checks themselves are listed in [README.md](../README.md#governance-and-policies).

## Common weaknesses

| Weakness | Where it could arise | Countermeasure |
|----------|---------------------|----------------|
| CWE-78 OS command injection | File names and contents of the analysed extension | `scan-deprecations.sh` passes the target only as a quoted path argument to `grep`; no command string is built from it or from file content. |
| CWE-829 inclusion from an untrusted source | Scripts in the analysed extension | `scan-deprecations.sh` runs no file from the target. |
| CWE-1104 unmaintained third-party components | Development and CI tools | Pre-commit hooks are pinned by `rev:` in `.pre-commit-config.yaml` and updated by Renovate (`renovate.json`, `pre-commit` manager enabled); the shared workflows pin actions by commit SHA. |
| CWE-798 secret exposure | Commits | Betterleaks scans every pull request to `main` and every push to `main` (`security.yml`); GitHub secret scanning with push protection is enabled for the repository. No script reads or stores credentials. |

## What the skill does not protect against

- **Code run by the upgrade toolchain.** Following the skill, the agent runs Composer, Rector, Fractor, PHP-CS-Fixer, PHPStan and PHPUnit in the extension. These execute the extension's code, its configuration files and its dependencies with the user's permissions. Upgrade only extensions whose code and dependencies you would run yourself, and review what the agent proposes to run.
- **Content of the extension reaching the agent.** The agent reads the extension's code and documentation, and `scan-deprecations.sh` prints matching source lines. Instructions hidden in those files are text like any other; the skill does not filter them.
- **`allowed-tools`.** `SKILL.md` declares none. Where a skill declares `allowed-tools`, it only pre-approves tools; it does not remove tools the agent already has.
- **Symbolic links in the target.** `grep` follows a symbolic link named on its command line, so when a path the script searches (for example `Classes/` or `ext_tables.php`) is a link, the scan reads the link's target and prints matches from it.
- **Arguments.** The scan script trusts its argument; it is meant to be the path of the user's own extension.
- **Completeness of the scan.** The checks are `grep` patterns. A scan without matches is not proof that an extension is free of deprecated APIs, and some patterns (for example implicit nullable parameters) report false positives. The script says so in its summary.
- **Configuration templates.** The files under `assets/` configure tools in the user's extension. Review them before copying; they are not security controls.
- **Maintainer tooling.** `scripts/verify-harness.sh` queries the GitHub API with the local `gh` login when the repository has no local pull request template, and `evals/run-ab-test.sh` sends the eval prompts and the skill text to a model through the `claude` CLI. Both are run by maintainers only.
