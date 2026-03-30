# TYPO3 v12 + v13 Dual Compatibility

When extension must support BOTH `^12.4 || ^13.4`.

## Version Constraints

```json
{
    "require": {
        "php": "^8.2",
        "typo3/cms-core": "^12.4 || ^13.4"
    }
}
```

```php
// ext_emconf.php
'constraints' => [
    'depends' => [
        'typo3' => '12.4.0-13.4.99',
        'php' => '8.2.0-8.4.99',
    ],
],
```

## Critical: Rector Configuration

**Do NOT use `UP_TO_TYPO3_13`** - it introduces v13-only APIs that break v12.

```php
$rectorConfig->sets([
    LevelSetList::UP_TO_PHP_82,
    // ONLY v12 rules for dual compatibility
    Typo3LevelSetList::UP_TO_TYPO3_12,
    Typo3SetList::CODE_QUALITY,
    Typo3SetList::GENERAL,
]);
```

## API Compatibility Matrix

| Purpose | v12 Compatible (use this) | v13 Only (avoid) |
|---------|---------------------------|------------------|
| Session access | `$TSFE->fe_user->getKey()` | `$request->getAttribute('frontend.user')` |
| Page info | `$data['pObj']->rootLine` | `$request->getAttribute('frontend.page.information')` |

**Rule**: Always use v12-compatible APIs when supporting both versions.

## Third-Party Dependency Dual Compatibility

The same principles apply to non-TYPO3 dependencies when supporting multiple major
versions (e.g., `"intervention/image": "^3.0 || ^4.0"`):

- **Use only APIs that exist in ALL supported versions** of the dependency
- **Check interface definitions**, not just concrete class methods
- **Use adapter pattern** when APIs differ between major versions
- **Run PHPStan and tests against each major version separately**
- **Never use `@phpstan-ignore`** to suppress version-conditional method errors

See `third-party-dependency-upgrades.md` for detailed patterns and examples.

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Rector v13 breaks v12 | v13-only APIs | Only use `UP_TO_TYPO3_12` for dual compat |
| `$TSFE` undefined | Not always set | Use `$GLOBALS['TSFE'] ?? null` |
| Method not found on interface | Method exists on concrete class but not interface | Use adapter pattern or version-safe API |
| `@phpstan-ignore` masks runtime error | Suppresses analysis but code still fails at runtime | Refactor to adapter pattern |
| Mock `->method()` fails | Mocked method removed in new version | Mock your own adapter interface instead |
| PHPStan passes but tests fail | PHPStan only checks one installed version | Run against each major version in CI |
