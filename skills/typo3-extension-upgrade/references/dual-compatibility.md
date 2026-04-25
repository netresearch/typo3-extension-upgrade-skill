# TYPO3 Multi-Version Compatibility (v12 + v13 + v14)

When extension must support `^12.4 || ^13.4 || ^14.1`.

## Version Constraints

```json
{
    "require": {
        "php": "^8.2",
        "typo3/cms-core": "^12.4 || ^13.4 || ^14.1"
    }
}
```

```php
// ext_emconf.php
'constraints' => [
    'depends' => [
        'typo3' => '12.4.0-14.99.99',
        'php' => '8.2.0-8.99.99',
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

## Fluid Template Cross-Version Patterns

### f:be.infobox state parameter

The `state` argument type differs across versions:

| Version | `state` type | Accepts |
|---------|-------------|---------|
| v12 | `int` | `InfoboxViewHelper::STATE_*` integer constants |
| v13 | `int` | `InfoboxViewHelper::STATE_*` integer constants |
| v14 | `mixed` | `ContextualFeedbackSeverity` enum OR integer |

**Rule**: Always use `InfoboxViewHelper::STATE_*` constants. Never use
`ContextualFeedbackSeverity` enum for `f:be.infobox` state — it breaks v12/v13.

Verified: `STATE_*` constants exist in v12.4, v13.4, and v14.2.

```html
<!-- CORRECT: works on v12/v13/v14 -->
<f:be.infobox title="Note" state="{f:constant(name: 'TYPO3\CMS\Fluid\ViewHelpers\Be\InfoboxViewHelper::STATE_INFO')}">

<!-- WRONG: breaks v12/v13 (state expects int, gets enum object) -->
<f:be.infobox title="Note" state="{f:constant(name: 'TYPO3\CMS\Core\Type\ContextualFeedbackSeverity::INFO')}">
```

Constants: `STATE_NOTICE` (-2), `STATE_INFO` (-1), `STATE_OK` (0),
`STATE_WARNING` (1), `STATE_ERROR` (2).

### Badge CSS classes

Use `badge-*` classes. TYPO3 core uses `badge badge-success` etc. in its
own backend templates (e.g., MFA overview) across all versions:

```html
<span class="badge badge-success">Active</span>
```

## PHP Cross-Version Patterns

### IconSize enum (v13+)

| Version | `IconFactory::getIcon()` $size | Available |
|---------|-------------------------------|-----------|
| v12 | `string` (untyped) | `Icon::SIZE_SMALL` etc. |
| v13 | `IconSize` enum | Both enum and deprecated constants |
| v14 | `IconSize` enum (strict) | `IconSize::SMALL` only |

**Pattern**: Use `enum_exists()` with argument unpacking for cross-version compat:

```php
use TYPO3\CMS\Core\Imaging\IconSize;

$icon = $this->iconFactory->getIcon(
    'actions-question-circle',
    ...(\enum_exists(IconSize::class) ? [IconSize::SMALL] : ['small']),
);
```

Add PHPStan ignoreErrors for the mixed-type warning:

```neon
# phpstan.neon
parameters:
    ignoreErrors:
        -
            message: '#IconSize#'
            path: %currentWorkingDirectory%/Classes/Controller/MyController.php
            reportUnmatched: false
        -
            message: '#expects string, mixed given#'
            path: %currentWorkingDirectory%/Classes/Controller/MyController.php
            reportUnmatched: false
```

### PHPStan inline ignores

**Never use `@phpstan-ignore` in code** — CI configs may reject inline ignores.
Always use `phpstan.neon` `ignoreErrors` with `reportUnmatched: false`.

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
