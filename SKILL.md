---
name: typo3-extension-upgrade
description: "Agent Skill: Systematic TYPO3 extension upgrades to newer LTS versions. Covers Extension Scanner, Rector, Fractor, PHPStan, and testing. Use when upgrading extensions to newer TYPO3 versions or fixing compatibility issues. By Netresearch."
---

# TYPO3 Extension Upgrade

Systematic framework for upgrading TYPO3 extensions to newer LTS versions.

> **Scope**: Extension code upgrades only. NOT for TYPO3 project/core upgrades.

## Upgrade Toolkit

| Tool | Purpose | Files |
|------|---------|-------|
| Extension Scanner | Diagnose deprecated APIs | TYPO3 Backend |
| Rector | Automated PHP migrations | `.php` |
| Fractor | Non-PHP migrations | FlexForms, TypoScript, YAML, Fluid |
| PHPStan | Static analysis | `.php` |

## Generic Upgrade Workflow

1. Create feature branch (verify git clean)
2. Update `composer.json` constraints for target version
3. Run `rector process --dry-run` → review → apply
4. Run `fractor process --dry-run` → review → apply
5. Run `php-cs-fixer fix`
6. Run `phpstan analyse` → fix errors
7. Run `phpunit` → fix tests
8. Test in target TYPO3 version(s)

## Quick Commands

```bash
./vendor/bin/rector process --dry-run && ./vendor/bin/rector process
./vendor/bin/fractor process --dry-run && ./vendor/bin/fractor process
./vendor/bin/php-cs-fixer fix && ./vendor/bin/phpstan analyse && ./vendor/bin/phpunit
```

## Configuration Templates

Copy from `assets/` and adjust for target version:
- `rector.php`, `fractor.php`, `phpstan.neon`, `phpunit.xml`, `.php-cs-fixer.php`

## References

| Topic | File |
|-------|------|
| Pre-upgrade checklist | `references/pre-upgrade.md` |
| API changes by version | `references/api-changes.md` |
| Real-world patterns | `references/real-world-patterns.md` |

## TYPO3 Changelogs

| Version | Changelog |
|---------|-----------|
| v14 | [Changelog-14](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-14.html) |
| v13 | [Changelog-13](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-13.html) |
| v12 | [Changelog-12](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-12.html) |

## Success Criteria

- `rector/fractor --dry-run` show no changes
- `phpstan analyse` passes
- All tests pass
- Extension works in target TYPO3 version

---

> **Contributing:** https://github.com/netresearch/typo3-extension-upgrade-skill
