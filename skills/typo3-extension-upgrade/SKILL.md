---
name: typo3-extension-upgrade
description: "Use when an extension has to work with a newer or the current TYPO3 LTS, when a version bump breaks compatibility or leaves deprecated APIs behind, when upgrading v11->v12, v12->v13 or v13->v14 (v14.3 LTS is the current target), when one codebase must stay compatible with two versions, when running Extension Scanner, Rector, Fractor or PHPStan against a target version, or when a specific v14 breaker bites - Fluid 5 strict ViewHelpers, HashService removal, the ext_tables.php split."
---

# TYPO3 Extension Upgrade Skill

Framework for upgrading TYPO3 extensions to newer LTS versions.
Extension code only, not project/core upgrades.

**Done is `exit=0` from the step 10 command, run last on every line the
constraint names that installs, and pasted into the report.** Not a summary.
Not green on one line with another left red. Not green because tests were
skipped or deleted. Not a commit with `--no-verify`. Anything short of that is
reported as not done, with the lines that show why.

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

   **Adding a version is not replacing one.** Writing `^14.3` alone drops
   support for every line the extension had before, which is a breaking change
   for everyone installing it — and it is the cheap way to make the new line
   resolve, so it happens by accident. "Make it work with the current LTS"
   asks for the new line, not for the loss of the old ones.
   **Read the existing constraint and keep every line in it**, then add the
   target: `^12.4 || ^13.4` becomes `^12.4 || ^13.4 || ^14.3`, and only an
   extension that already supported v13 alone ends up at `^13.4 || ^14.3`.
   Drop a line only where that was asked for, and say so where a maintainer
   will see it. Whether one codebase *can* serve them all is a separate
   question, answered in `references/dual-compatibility.md`.
4. **Audit third-party dependencies** for major version changes (consult `references/third-party-dependency-upgrades.md`)
5. Run `rector process --dry-run` then review and apply
6. Run `fractor process --dry-run` then review and apply
7. Run `php-cs-fixer fix`
8. Run `phpstan analyse` **against each supported dependency version** and fix errors
9. Run `phpunit` and fix tests. **`Tests/` is part of the upgrade, not a
   consequence of it.** A class v14 removed, referenced from a test, is fatal
   rather than failing: in an import, a parent, a property or a signature it
   stops PHPUnit while it loads the suite, so nothing runs at all. Search for
   the removed types across both trees before running anything:
   `grep -rnE 'TypoScriptFrontendController|StandaloneView|TemplateView|HashService|LocalPreviewHelper|LocalCropScaleMaskHelper|FreezableBackendInterface' Classes/ Tests/`
   Every hit is a fix. `createMock` on one of them cannot be repaired by
   swapping the name — see `references/upgrade-v13-to-v14.md`
10. **Install the target version and run the suite against it.** A green suite
    on the version already installed proves nothing about the target — that is
    the old code passing old tests. Install first, in two passes, then test:
    ```bash
    composer update "typo3/*" --with typo3/cms-core:^14.3 -W --no-install \
      && rm -rf vendor && composer install \
      && composer show typo3/cms-core | grep '^versions' \
      && vendor/bin/phpunit -c Build/phpunit/UnitTests.xml; echo "exit=$?"
    ```
    Chained, so a failed install stops before PHPUnit runs against the old tree;
    the `versions` line says what was actually installed, and `exit=` is the
    status of whichever step ran last.
    One pass fails on the way from v13 to v14: Composer upgrades
    `typo3/class-alias-loader` and then runs the old plugin against the new
    files, which dies with `Class "…\CaseSensitiveToken" not found` after the
    lock file is written. `composer install` on top of the old `vendor/` dies the
    same way, so `vendor/` goes first.
    The package argument matters: without it `composer update` moves every
    dependency, and the test result then depends on upgrades that have nothing
    to do with TYPO3. `-W` lets the TYPO3 packages' own dependencies follow.
    **If the target will not install, the upgrade is untested.** Say so in the
    report, with the error, and do not report the suite as passing: a green run
    on the version that was already there is that version's result.
11. **Run the same command for every older line the constraint keeps** —
    `--with typo3/cms-core:^13.4` for `^13.4`, and so on. A migration that
    turns the target green can break the line below it: measured, an agent got
    v14 green, left v13's suite failing, and reported all three lines
    compatible. Fix, then run every line again. A line that cannot be
    installed here at all — Composer cannot resolve or download it — is
    untested, not failed: report it with Composer's error, and never drop it
    from the constraint for that reason (step 3).
12. **Write the report, ending with the output of the last run on each line,
    pasted as it printed** — the `versions` line, PHPUnit's final summary line
    and the `exit=` line. Where there is no summary, paste what stands in its
    place: PHPUnit's `Message:` line when the suite would not load, Composer's
    error when the install failed. On a line that installed, any `exit=` other
    than `0` means the work is not done: go back to step 9. A line whose install
    failed is the untested case from step 11. Committing past a red suite, or
    with `--no-verify`, is not done either.
13. Verify success criteria (consult `references/verification.md`)

**Done means the suite passes on every line the constraint names, with that
line installed** — every line that can be installed; the rest are reported as
untested. Not that the constraint was widened, and not that the suite
is green where it was already green.

The pasted lines are the point of step 12. Measured: agents asked to *prove*
the result wrote "✅ 719 tests pass" instead, and among those who summarised,
one had never installed the target, one had seen the suite fail to load three
times, and one had seen three errors and thirteen failures and committed with
`--no-verify`. A
summary can say anything; a pasted `exit=1` cannot. Only where you cannot make
the suite pass, report that, with those same lines.

Where a removed class is referenced decides when it bites. In an `import`, a
parent class, a property or a signature it is resolved while PHPUnit *loads*
the suite, so nothing runs at all and the failure looks nothing like a test
failure. Referenced only inside a method body, it fails when that one test
executes, and the rest of the suite still passes — which is the more
comfortable failure and the easier one to miss in a summary line.

## When the migration breaks the tests

It will. A suite that was green before Rector routinely comes back with dozens
of errors, and working through them is the job.

**Never revert the migration to get back to green.** Measured: an agent ran
Rector, saw `Tests: 719, Errors: 34`, discarded every migrated file under
`Classes/`, got `OK (719 tests, 1176 assertions)`, and committed
`composer.json`, `ext_emconf.php` and two build files — no code at all. That
commit claims support for a version the code does not have, and it is the worst
of the three possible outcomes: a failing upgrade is visible, an unattempted one
is honest, and this one is neither.

Green after a revert is the state you started in. The only green that counts is
the one from step 10, with the target version installed and the migration in
place.

**Skipping or deleting a test to get green is the same revert,** one test at a
time. A test that exercises an API the new version removed is migrated with the
code it tests, not marked skipped: `markTestSkipped`, a version check that
returns early, or a removed test method all turn a failure into silence. The
same goes for `--no-verify` on the commit — it silences the checks that would
report it.

**Nor stop to ask whether to proceed.** Measured: an agent installed the
target, counted the uses of a class the new version removed, ran
`git reset --hard`, and asked whether it should do the refactoring. A request
to make the extension work with the new version is that permission. Replacing
what the new version removed *is* the upgrade, however many places use it — it
is the work, not a finding to report back. Ask only about what the request
leaves open, such as dropping a supported line (step 3).

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
