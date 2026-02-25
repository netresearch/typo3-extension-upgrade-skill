---
name: typo3-extension-upgrade
description: "Use when upgrading TYPO3 extensions to newer LTS versions (v11->v12, v12->v13, v13->v14), using Extension Scanner, Rector, Fractor, PHPStan, testing, or fixing compatibility issues."
---

# TYPO3 Extension Upgrade Skill

Systematic framework for upgrading TYPO3 extensions to newer LTS versions.

> **Scope**: Extension code upgrades only. NOT for TYPO3 project/core upgrades.

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
4. Run `rector process --dry-run` then review and apply
5. Run `fractor process --dry-run` then review and apply
6. Run `php-cs-fixer fix`
7. Run `phpstan analyse` and fix errors
8. Run `phpunit` and fix tests
9. Test in target TYPO3 version(s)
10. Verify success criteria (consult `references/verification.md`)

## When NOT to Apply Automatically

Do NOT blindly apply Rector/Fractor if:
- You need dual-version compatibility (v12 + v13)
- The extension has no tests to verify changes
- The diff shows changes you don't understand
- The rule affects complex APIs (DBAL, Extbase internals)

Instead: apply specific rules manually, test between each change.

## Quick Commands

```bash
# Rector: automated PHP migrations
./vendor/bin/rector process --dry-run && ./vendor/bin/rector process

# Fractor: non-PHP migrations
./vendor/bin/fractor process --dry-run && ./vendor/bin/fractor process

# Quality checks
./vendor/bin/php-cs-fixer fix && ./vendor/bin/phpstan analyse && ./vendor/bin/phpunit
```

## TYPO3 Changelogs

| Version | Changelog |
|---------|-----------|
| v14 | [Changelog-14](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-14.html) |
| v13 | [Changelog-13](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-13.html) |
| v12 | [Changelog-12](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-12.html) |

## Asset Templates

Configure tooling by copying and adjusting these templates:
- `assets/rector.php` - Rector configuration for PHP migrations
- `assets/fractor.php` - Fractor configuration for non-PHP migrations
- `assets/phpstan.neon` - PHPStan static analysis configuration
- `assets/phpunit.xml` - PHPUnit test configuration
- `assets/.php-cs-fixer.php` - PHP-CS-Fixer code style configuration

## References

| Reference | Use when... |
|-----------|-------------|
| `references/pre-upgrade.md` | Starting an upgrade: planning checklist, version audit, risk assessment |
| `references/api-changes.md` | Checking deprecated/removed APIs by TYPO3 version |
| `references/upgrade-v11-to-v12.md` | Upgrading from TYPO3 v11 to v12 |
| `references/upgrade-v12-to-v13.md` | Upgrading from TYPO3 v12 to v13 |
| `references/dual-compatibility.md` | Maintaining dual compatibility (v12 + v13) |
| `references/real-world-patterns.md` | Looking for real-world migration examples |
| `references/toolchain-output.md` | Understanding Rector/Fractor dry-run output |
| `references/troubleshooting.md` | Rector broke code, PHPStan errors, test failures |
| `references/verification.md` | Checking success criteria and real-world testing |

## External Resources

- [TYPO3 Rector Documentation](https://github.com/sabbelasichon/typo3-rector)
- [Fractor Documentation](https://github.com/andreaswolf/fractor)
- [TYPO3 Core Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/)

---

> **Contributing:** https://github.com/netresearch/typo3-extension-upgrade-skill
