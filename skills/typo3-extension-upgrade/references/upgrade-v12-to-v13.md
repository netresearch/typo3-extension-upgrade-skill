# TYPO3 v12 to v13 Upgrade Guide

## Version Constraints

```json
{
    "require": {
        "php": "^8.2",
        "typo3/cms-core": "^13.4"
    }
}
```

```php
// ext_emconf.php
'constraints' => [
    'depends' => [
        'typo3' => '13.4.0-13.4.99',
        'php' => '8.2.0-8.4.99',
    ],
],
```

## Rector Configuration

```php
$rectorConfig->sets([
    LevelSetList::UP_TO_PHP_82,
    Typo3LevelSetList::UP_TO_TYPO3_13,
    Typo3SetList::CODE_QUALITY,
    Typo3SetList::GENERAL,
]);
```

## Key Breaking Changes

| Change | v12 API | v13 API |
|--------|---------|---------|
| Frontend user | `$TSFE->fe_user` | `$request->getAttribute('frontend.user')` |
| Page info | `$data['pObj']->rootLine` | `$request->getAttribute('frontend.page.information')` |

## Dual v12 + v13 Gotchas

### `#[AsEventListener]` Attribute Is v13+ Only

The PHP attribute `#[AsEventListener]` was introduced in TYPO3 v13 (Symfony EventDispatcher attribute). If your extension supports `^12.4 || ^13.4 || ^14.0`, the attribute alone is **not enough** — on v12, the listener is never registered (silent: no error, the event simply never fires).

**Fix**: keep BOTH the attribute AND the `Services.yaml` tag. v13+ ignores the tag when the attribute is present, so there is no double-registration.

```php
use TYPO3\CMS\Core\Attribute\AsEventListener;

#[AsEventListener(identifier: 'vendor-myext/login-listener')]
final class LoginListener
{
    public function __invoke(BeforeUserLogoutEvent $event): void { /* ... */ }
}
```

```yaml
# Configuration/Services.yaml — required for v12 compat
services:
  Vendor\MyExt\EventListener\LoginListener:
    tags:
      - name: event.listener
        identifier: 'vendor-myext/login-listener'
        event: TYPO3\CMS\Core\Authentication\Event\BeforeUserLogoutEvent
```

**Drop the `Services.yaml` tag** only when bumping the floor to `^13.4`.

See also: `api-changes.md` for detailed patterns.
