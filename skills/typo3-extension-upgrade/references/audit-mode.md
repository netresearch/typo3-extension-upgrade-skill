# Audit mode: report vs. auto-fix

Use this when the goal is to **assess/report** — produce an upgrade estimate or file issues — rather than to apply the upgrade. The aim is to ticket only the work that is genuinely manual, so the backlog does not fill with noise that the toolchain fixes on its own.

## Pin the tool targets to the upgrade target first

A dry-run only reveals what its configured target covers. A config left on a previous version passes the "tool exists" checkpoints but silently skips the relevant migrations.

- **Rector** — set `Typo3LevelSetList::UP_TO_TYPO3_<target>` for the TYPO3 migrations, and keep `LevelSetList::UP_TO_PHP_<floor>` at the **minimum** supported PHP. Targeting a higher PHP would rewrite code with newer-version syntax (e.g. typed class constants) and break the floor (checkpoints TU-56 / TU-57). When auditing without changing the repo, write a separate audit config and run with `--dry-run`.
- **PHPStan** — set `phpVersion: { min: <floor>, max: <ceiling> }` (e.g. `80200`–`80500`; range form supported since PHPStan 1.10) to verify the whole supported PHP range. This is where the PHP **ceiling** (e.g. 8.5) is checked — not in Rector.

## Cross-reference, then ticket only the remainder

1. Run `rector process --dry-run` and `fractor process --dry-run`; collect the **applied rules**.
2. Run `phpstan analyse` with `phpstan-deprecation-rules`; collect the **deprecation findings**.
3. For each deprecation, check whether an applied Rector/Fractor rule covers it:
   - **Has a matching rule** → auto-fixed when the upgrade runs → **do not ticket**.
   - **No matching rule** → manual work → **ticket it**.

Also ticket (the tools do not handle these):

- Logic/behaviour bugs surfaced during the audit.
- Design gaps (e.g. an extension that should ship a v14 Site Set instead of static TypoScript).
- Config the tools skip — notably `ext_emconf.php` version constraints, `ext_tables.sql` system columns, and FlexForm fields with semantically wrong values (a wrong value is a bug, not a migration).

## Ignore pure code-style rules

Style-only Rector rules (e.g. `ClassPropertyAssignToConstructorPromotionRector`) are not upgrade-relevant. Exclude them when deciding what counts as an upgrade finding — many extensions even skip them in their own `rector.php`.
