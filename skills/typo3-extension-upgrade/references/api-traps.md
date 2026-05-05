# TYPO3 API Traps (Cross-Version)

Architectural rules and silent footguns that bite across TYPO3 v12, v13, and v14. Each one looks innocuous at the call site but produces wrong-but-not-fatal behavior — soft-deleted records vanish, registrations get silently dropped, paths double, DI breaks at runtime.

---

## `Connection::select()` Applies TCA Restrictions Silently

`TYPO3\CMS\Core\Database\Connection::select()` (the convenience wrapper, not the QueryBuilder fluent API) applies the **default `RestrictionContainer`**, which includes `DeletedRestriction`, `HiddenRestriction`, and `StartTimeRestriction` per TCA. Code reaching for "I just want to read the row" misses every soft-deleted / hidden / time-restricted record.

This bites hardest in admin tooling, cleanup scripts, and audit features that explicitly want to see deleted records.

**Search Pattern**

```bash
grep -rn "->select(\|Connection::select" Classes/
```

**Fix** — drop down to `QueryBuilder` and remove restrictions explicitly:

```php
// ❌ Silently filters deleted/hidden/time-restricted rows
$rows = $connection->select(['*'], 'be_users', ['uid' => $uid])->fetchAllAssociative();

// ✅ See every row, including deleted
$queryBuilder = GeneralUtility::makeInstance(ConnectionPool::class)
    ->getQueryBuilderForTable('be_users');
$queryBuilder->getRestrictions()->removeAll();
$rows = $queryBuilder
    ->select('*')
    ->from('be_users')
    ->where($queryBuilder->expr()->eq('uid', $queryBuilder->createNamedParameter($uid, Connection::PARAM_INT)))
    ->executeQuery()
    ->fetchAllAssociative();
```

To keep some restrictions but drop others, use `removeByType(DeletedRestriction::class)` instead of `removeAll()`.

---

## `TYPO3_USER_SETTINGS` Registration MUST Live in `ext_tables.php`

`cms-setup`'s own `ext_tables.php` rebuilds `$GLOBALS['TYPO3_USER_SETTINGS']` from scratch. Any field your extension registers in `ext_localconf.php` is wiped out before the setup module gets to read it — and the failure mode is silent: no error, the field just doesn't appear.

**Affected**: any custom user-settings panel, e.g. an "Enable passkey login" toggle.

**Symptom**: field renders during local dev (when caches are warm with stale data) but is missing on a fresh install / after `Flush all caches`.

**Fix** — move the registration:

```php
// ❌ ext_localconf.php — silently overwritten
ExtensionManagementUtility::addUserTSConfig(...);
$GLOBALS['TYPO3_USER_SETTINGS']['columns']['tx_myext_setting'] = [...];

// ✅ ext_tables.php — runs AFTER cms-setup/ext_tables.php
$GLOBALS['TYPO3_USER_SETTINGS']['columns']['tx_myext_setting'] = [...];
ExtensionManagementUtility::addFieldsToUserSettings('tx_myext_setting', 'after:lang');
```

See also: [TYPO3 boot order](#typo3-boot-order) below.

---

## TYPO3 Boot Order

The reason for the rule above. Boot order is:

1. `ext_localconf.php` of every active extension (in extension dependency order)
2. TCA loaded
3. `ext_tables.php` of every active extension (in extension dependency order)

Anything that depends on **another extension's `ext_tables.php` having already executed** must itself live in `ext_tables.php`. The two most common cases:

- **User Settings fields** — `cms-setup/ext_tables.php` overwrites `$GLOBALS['TYPO3_USER_SETTINGS']`
- **Backend module overrides** — depend on `cms-backend` having registered the module first

Mental model: `ext_localconf.php` is for "configure the framework" (DI, caches, hooks, event listeners). `ext_tables.php` is for "extend things the framework already built."

---

## `callUserFunction()` Bypasses Dependency Injection

`GeneralUtility::callUserFunction()` instantiates the target class via `makeInstance()` **without DI**, calling the constructor with no arguments. Any class used as a userFunc target (TypoScript `userFunc`, TCA `displayCond`, custom hooks routed through callUserFunction, user-settings panels, etc.) **cannot use constructor injection** — you'll get a `TypeError: too few arguments`.

**Search Pattern**

```bash
grep -rn "callUserFunction\|userFunc\s*=" Classes/ Configuration/
```

**Fix options** (in order of preference):

```php
// ❌ Constructor DI breaks under callUserFunction
final class MyPanel
{
    public function __construct(private readonly LanguageService $lang) {}
    public function render(array $params): string { ... }
}
```

```php
// ✅ Option 1 — pull deps via makeInstance() inside the method
final class MyPanel
{
    public function render(array $params): string
    {
        $lang = GeneralUtility::makeInstance(LanguageServiceFactory::class)->createFromUserPreferences(...);
        // ...
    }
}
```

```php
// ✅ Option 2 — refactor away from callUserFunction
//    For TCA displayCond: use the array-form `displayCond` instead of userFunc
//    For TypoScript: use a USER content object pointing at a properly DI'd controller action
//    For PSR-14 events: just write an event listener
```

PHPStan won't catch this — the class constructor is valid PHP. The error appears only when TYPO3 actually invokes the userFunc.

---

## `TemplatePaths::ensureAbsolutePath()` Resolves `EXT:` Paths Itself

Fluid's `TYPO3Fluid\Fluid\View\TemplatePaths::ensureAbsolutePath()` (and the layers above it — `setTemplateRootPaths`, `setLayoutRootPaths`, `setPartialRootPaths`) accept `EXT:my_ext/Resources/Private/Templates/` directly and resolve it through `GeneralUtility::getFileAbsFileName()` internally.

If you pre-resolve the path yourself with `GeneralUtility::getFileAbsFileName('EXT:my_ext/...')` and then pass the absolute result, **most setups still work** — but on Composer-mode installs where the EXT path resolves to a symlinked vendor directory, you can hit path-doubling (`/var/www/html/vendor/.../EXT:my_ext/...`) or stale resolution after a `composer dump-autoload`.

**Fix** — pass `EXT:` paths verbatim:

```php
// ❌ Pre-resolved
$view->setTemplateRootPaths([
    GeneralUtility::getFileAbsFileName('EXT:my_ext/Resources/Private/Templates/'),
]);

// ✅ Let TemplatePaths resolve it
$view->setTemplateRootPaths([
    'EXT:my_ext/Resources/Private/Templates/',
]);
```

Same applies to `LayoutRootPaths` and `PartialRootPaths`.

---

## See Also

- `upgrade-v11-to-v12.md` — v12 FormEngine DI nodes (`setData()` workaround for [#100670](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/12.4/Deprecation-100670-DIAwareFormEngineNodes.html))
- `upgrade-v12-to-v13.md` — `#[AsEventListener]` v13+ vs `Services.yaml` tag for v12 compat
- `upgrade-v13-to-v14.md` — `LoginProviderInterface::modifyView()`, `StandaloneView` removal, `ModifyPageLayoutOnLoginProviderSelectionEvent` signature drift
- `api-changes.md` — full deprecated/removed API tables per version
