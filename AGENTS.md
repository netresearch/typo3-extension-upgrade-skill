# TYPO3 Extension Upgrade Skill

Agent harness for the TYPO3 extension upgrade skill repository.

## Repo Structure

```
├── skills/typo3-extension-upgrade/   # Skill definition
│   ├── SKILL.md                      # Main skill instructions
│   ├── assets/                       # Config templates (rector, fractor, phpstan, phpunit)
│   ├── checkpoints.yaml              # Eval checkpoints
│   └── references/                   # Detailed upgrade docs per version
├── agents/                           # Agent definitions
│   └── upgrade-planner.md            # Upgrade planning agent
├── commands/                         # Slash commands
│   ├── assess.md                     # /assess command
│   └── rector.md                     # /rector command
├── evals/                            # Evaluation suite
│   └── evals.json
├── Build/                            # Build tooling
│   ├── Scripts/                      # Utility scripts
│   └── hooks/                        # Git hooks (pre-push)
├── composer.json                     # Composer package (ai-agent-skill type)
├── docs/                             # Architecture and planning docs
│   └── ARCHITECTURE.md
└── scripts/                          # Harness scripts
    └── verify-harness.sh
```

## Commands

No build system scripts defined in `composer.json`. This is a content-only skill repo.

Key skill commands (run in target extension, not this repo):
- `./vendor/bin/rector process --dry-run` -- Rector PHP migrations
- `./vendor/bin/fractor process --dry-run` -- Fractor non-PHP migrations
- `./vendor/bin/phpstan analyse` -- Static analysis
- `./vendor/bin/php-cs-fixer fix` -- Code style fixes

## Rules

- **Scope**: Extension code upgrades only; NOT for TYPO3 project/core upgrades
- **Workflow**: Always complete planning phase before code changes (see `references/pre-upgrade.md`)
- **Caution**: Do NOT blindly apply Rector/Fractor for dual-version compatibility or untested extensions
- **Verification**: Always verify success criteria after upgrade (see `references/verification.md`)
- **Assets**: Config templates in `assets/` are starting points; adapt per extension

## References

- [SKILL.md](skills/typo3-extension-upgrade/SKILL.md) -- Main skill definition
- [Pre-upgrade checklist](skills/typo3-extension-upgrade/references/pre-upgrade.md)
- [API changes by version](skills/typo3-extension-upgrade/references/api-changes.md)
- [v13 to v14 upgrade guide](skills/typo3-extension-upgrade/references/upgrade-v13-to-v14.md)
- [Dual compatibility guide](skills/typo3-extension-upgrade/references/dual-compatibility.md)
- [Verification criteria](skills/typo3-extension-upgrade/references/verification.md)
- [Troubleshooting](skills/typo3-extension-upgrade/references/troubleshooting.md)
- [Upgrade planner agent](agents/upgrade-planner.md)
