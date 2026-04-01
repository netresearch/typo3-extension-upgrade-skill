# TYPO3 v13 to v14 Upgrade Guide

## Version Constraints

```json
{
    "require": {
        "php": "^8.4",
        "typo3/cms-core": "^14.0"
    }
}
```

```php
// ext_emconf.php
'constraints' => [
    'depends' => [
        'typo3' => '14.0.0-14.4.99',
        'php' => '8.4.0-8.4.99',
    ],
],
```

## Rector Configuration

```php
$rectorConfig->sets([
    LevelSetList::UP_TO_PHP_84,
    Typo3LevelSetList::UP_TO_TYPO3_14,
    Typo3SetList::CODE_QUALITY,
    Typo3SetList::GENERAL,
]);
```

## Key Breaking Changes

| Change | Search | Fix |
|--------|--------|-----|
| TypoScript callables | `grep -rn "userFunc" Configuration/TypoScript/` | Add `#[AsAllowedCallable]` attribute |
| `ExtensionConfiguration::getAll()` | `grep -rn "getAll()" Classes/` | Use `$GLOBALS['TYPO3_CONF_VARS']['EXTENSIONS']` |
| `Icon::SIZE_*` constants | `grep -rn "Icon::SIZE_" Classes/` | Use `IconSize` enum |
| DBAL `Type::getName()` | `grep -rn "->getName()" Classes/` | Use `instanceof` checks |
| `f:uri.resource` in non-Extbase | `grep -rn "f:uri.resource" Resources/` | Use `EXT:` syntax |
| Bootstrap 4 CSS classes | `grep -rn "btn-default\|badge-primary" Resources/` | Use Bootstrap 5 classes |
| Scheduler interface signatures | `grep -rn "AdditionalFieldProviderInterface" Classes/` | Match exact interface signature |

## Dual v13/v14 Compatibility

When supporting `^13.4 || ^14.0`:

- Minimum `^13.4.21` required (for `#[AsAllowedCallable]` backport)
- Use `class_exists(IconSize::class)` guard for IconSize enum
- Or use string size values: `$iconFactory->getIcon('name', 'small')`

## Composer Dependencies

```json
{
    "require-dev": {
        "a9f/typo3-fractor": "^0.4",
        "friendsofphp/php-cs-fixer": "^3.64",
        "phpstan/phpstan": "^2.0",
        "phpstan/phpstan-deprecation-rules": "^2.0",
        "phpstan/phpstan-phpunit": "^2.0",
        "phpunit/phpunit": "^12.0",
        "rector/rector": "^2.0",
        "ssch/typo3-rector": "^3.0",
        "typo3/testing-framework": "^9.0"
    }
}
```

See also: `api-changes.md` for detailed patterns (v13 -> v14 section).
