---
name: typo3-extension-upgrade
description: "Use when an extension has to work with a newer or the current TYPO3 LTS, when a version bump breaks compatibility or leaves deprecated APIs behind, when upgrading v11->v12, v12->v13 or v13->v14 (v14.3 LTS is the current target), when one codebase must stay compatible with two versions, when running Extension Scanner, Rector, Fractor or PHPStan against a target version, or when a specific v14 breaker bites - Fluid 5 strict ViewHelpers, HashService removal, the ext_tables.php split."
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
3. Update `composer.json` constraints for the target version. **v14's LTS minor is 3: write `^14.3`, never `^14.4`** — `^13.4 || ^14.3` to support both. v11.5, v12.4 and v13.4 make `14.4` look like the next in line; it matches no release, so `composer update` fails dependency resolution, exits non-zero and installs nothing. Constraints for every version pair: `references/upgrade-v13-to-v14.md`
4. **Audit third-party dependencies** for major version changes (consult `references/third-party-dependency-upgrades.md`)
5. Run `rector process --dry-run` then review and apply
6. Run `fractor process --dry-run` then review and apply
7. Run `php-cs-fixer fix`
8. Run `phpstan analyse` **against each supported dependency version** and fix errors
9. Run `phpunit` and fix tests
10. **Install the target version and run the suite against it.** A green suite
    on the version already installed proves nothing about the target — that is
    the old code passing old tests. Install first, then test:
    `composer update "typo3/*" --with typo3/cms-core:^14.3 -W && vendor/bin/phpunit -c Build/phpunit/UnitTests.xml`
    The package argument matters: without it `composer update` moves every
    dependency, and the test result then depends on upgrades that have nothing
    to do with TYPO3. `-W` lets the TYPO3 packages' own dependencies follow.
11. Verify success criteria (consult `references/verification.md`)

**Done means the suite passes with the target version installed.** Not that the
constraint was widened, and not that the suite is green where it was already
green.

Where a removed class is referenced decides when it bites. In an `import`, a
parent class, a property or a signature it is resolved while PHPUnit *loads*
the suite, so nothing runs at all and the failure looks nothing like a test
failure. Referenced only inside a method body, it fails when that one test
executes, and the rest of the suite still passes — which is the more
comfortable failure and the easier one to miss in a summary line.

## When the migration breaks the tests

It will. Rector applied against a real extension routinely leaves a suite that
was green sitting on dozens of errors, and the fix is to work through them.

**Never revert the migration to get back to green.** Measured: an agent ran
Rector, saw `Tests: 719, Errors: 34`, discarded every migrated file under
`Classes/`, got `OK (719 tests, 1176 assertions)` and committed —
composer.json, ext_emconf.php and two build files, no code. That commit claims
support for a version the code does not have, and it is the worst of the three
possible outcomes: a failing upgrade is visible, an unattempted one is honest,
and this one is neither.

Green after a revert is the state you started in. The only green that counts is
the one from step 10, with the target version installed and the migration in
place.

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
