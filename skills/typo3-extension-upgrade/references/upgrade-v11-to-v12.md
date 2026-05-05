# TYPO3 v11 to v12 Upgrade Guide

## Version Constraints

```json
{
    "require": {
        "php": "^8.1",
        "typo3/cms-core": "^12.4"
    }
}
```

```php
// ext_emconf.php
'constraints' => [
    'depends' => [
        'typo3' => '12.4.0-12.4.99',
        'php' => '8.1.0-8.4.99',
    ],
],
```

## Rector Configuration

```php
$rectorConfig->sets([
    LevelSetList::UP_TO_PHP_81,
    Typo3LevelSetList::UP_TO_TYPO3_12,
    Typo3SetList::CODE_QUALITY,
    Typo3SetList::GENERAL,
]);
```

## Key Breaking Changes

| Change | Search | Fix |
|--------|--------|-----|
| Doctrine DBAL 4.x | `grep -rn "PDO::PARAM_"` | Use `Connection::PARAM_*` |
| GeneralUtility::_GET/POST | `grep -rn "GeneralUtility::_GET"` | Use `$_GET['param'] ?? null` |
| TCA required flag | `grep -rn "'eval'.*'required'"` | Use `'required' => true` |
| itemFormElID removed | `grep -rn "itemFormElID"` | Generate from `itemFormElName` |
| FlexForm structure | Run Fractor | Fractor auto-fixes |
| TypoScript [end] | Run Fractor | Changed to `[global]` |

## Composer Dependencies

```json
{
    "require-dev": {
        "a9f/typo3-fractor": "^0.4",
        "friendsofphp/php-cs-fixer": "^3.64",
        "phpstan/phpstan": "^2.0",
        "phpstan/phpstan-deprecation-rules": "^2.0",
        "phpstan/phpstan-phpunit": "^2.0",
        "phpunit/phpunit": "^11.0",
        "rector/rector": "^2.0",
        "ssch/typo3-rector": "^3.0",
        "typo3/testing-framework": "^9.0"
    }
}
```

## v12-Specific Gotchas

### FormEngine DI Nodes Need Their Own `setData()`

> **Source**: [Deprecation #100670 — DI-aware FormEngine nodes](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/12.4/Deprecation-100670-DIAwareFormEngineNodes.html)

In v12, `AbstractNode::setData()` is **commented out** and the constructor-based `NodeFactory` invocation is the deprecated path. If your custom FormEngine element (`AbstractFormElement` subclass) uses constructor injection, `NodeFactory` falls back to the legacy `__construct(NodeFactory $nodeFactory, array $data)` path and you get:

```
TypeError: Argument #1 ($nodeFactory) of MyFormElement::__construct() must be of type NodeFactory, …
```

**Fix** (works on v12, v13, v14):

```php
final class MyFormElement extends AbstractFormElement
{
    public function __construct(
        private readonly LanguageService $languageService,
    ) {}

    // REQUIRED on v12 — restored signature without NodeFactory
    public function setData(array $data): void
    {
        $this->data = $data;
    }

    public function render(): array { /* ... */ }
}
```

```yaml
# Configuration/Services.yaml — MUST be public for makeInstance lookup
services:
  Vendor\MyExt\FormEngine\MyFormElement:
    public: true
```

`#[Autoconfigure(public: true)]` on the class works too. Without `public: true`, the DI container won't resolve the class for `NodeFactory`'s lazy lookup and you fall back to the broken legacy path.

See also: `api-changes.md` for detailed patterns.
