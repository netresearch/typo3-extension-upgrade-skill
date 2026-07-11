---
name: typo3-extension-upgrade
description: "Use when upgrading TYPO3 extensions to newer LTS versions (v11->v12, v12->v13, v13->v14 - v14.3 LTS is the current target), running Extension Scanner, Rector, Fractor, PHPStan, fixing deprecated APIs, or resolving compatibility issues. Also triggers on: migration, version upgrade, deprecated API, dual-version compatibility, Fluid 5 strict VHs, HashService removal, ext_tables.php split."
---

# TYPO3 Extension Upgrade Skill

Framework for upgrading TYPO3 extensions to newer LTS versions.
Extension code only, not project/core upgrades.

## Upgrade Toolkit

| Tool | Purpose | Files |
|------|---------|-------|
| Extension Scanner | Diagnose deprecated APIs | TYPO3 Backend |
| Rector | Automated PHP migrations | `.php` |
| Fractor | Non-PHP migrations | FlexForms, TypoScript, YAML, Fluid |
| PHPStan | Static analysis | `.php` |

## Core Workflow

1. Complete planning phase (consult `references/pre-upgrade.md`)
2. Create feature branch (verify git is clean)
3. Update `composer.json` constraints for target version
4. **Audit third-party dependencies** for major version changes (consult `references/third-party-dependency-upgrades.md`)
5. Run `rector process --dry-run` then review and apply
6. Run `fractor process --dry-run` then review and apply
7. Run `php-cs-fixer fix`
8. Run `phpstan analyse` **against each supported dependency version** and fix errors
9. Run `phpunit` and fix tests
10. Test in target TYPO3 version(s)
11. Verify success criteria (consult `references/verification.md`)

## When NOT to Apply Automatically

Do NOT blindly apply Rector/Fractor when dual-version compatibility, missing
tests, unclear changes, or complex APIs (DBAL, Extbase) are involved. Instead
apply rules manually, testing between changes.

## Third-Party Dependency Upgrades

When `composer.json` widens a dependency to a new major version: enumerate API usages, cross-reference the new API, verify mocks, use adapter pattern for signature differences, run PHPStan per major version. See `references/third-party-dependency-upgrades.md`.

## Quick Commands

```bash
rector process --dry-run && rector process        # PHP migrations
fractor process --dry-run && fractor process       # Non-PHP migrations
php-cs-fixer fix && phpstan analyse && phpunit     # Quality checks
```

## Asset Templates

Config templates in `assets/`: `rector.php`, `fractor.php`, `phpstan.neon`, `phpunit.xml`, `.php-cs-fixer.php`

## References

| Reference | Use when... |
|-----------|-------------|
| `references/pre-upgrade.md` | Planning checklist, version audit, risk assessment |
| `references/api-changes.md` | Checking deprecated/removed APIs by TYPO3 version |
| `references/api-traps.md` | Cross-version footguns: TCA restrictions, boot order, DI bypass |
| `references/upgrade-v11-to-v12.md` | Upgrading from TYPO3 v11 to v12 |
| `references/upgrade-v12-to-v13.md` | Upgrading from TYPO3 v12 to v13 |
| `references/upgrade-v13-to-v14.md` | Upgrading from TYPO3 v13 to v14 |
| `references/dual-compatibility.md` | Dual compatibility (v12 + v13) |
| `references/real-world-patterns.md` | Real-world migration examples |
| `references/toolchain-output.md` | Rector/Fractor dry-run output |
| `references/troubleshooting.md` | Rector broke code, PHPStan errors, test failures |
| `references/third-party-dependency-upgrades.md` | Non-TYPO3 dependencies (major version bumps, adapter patterns) |
| `references/verification.md` | Success criteria and real-world testing |
| `references/multi-version-worktrees.md` | Per-LTS worktree layout, backport workflow, cross-version CI matrix |
| `references/audit-mode.md` | Assessing/estimating: ticket only non-automatable findings |
| `scripts/scan-deprecations.sh <path>` | Deterministic grep scan for deprecated/removed APIs and traps |

## External Resources

- [TYPO3 Rector](https://github.com/sabbelasichon/typo3-rector)
- [Fractor](https://github.com/andreaswolf/fractor)
- [TYPO3 Core Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/)
