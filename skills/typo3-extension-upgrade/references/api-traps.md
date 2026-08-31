# TYPO3 API Traps (Cross-Version)

Architectural rules and silent footguns that bite across TYPO3 v12, v13, and v14. Each one looks innocuous at the call site but produces wrong-but-not-fatal behavior — soft-deleted records vanish, registrations get silently dropped, paths double, DI breaks at runtime.

---

## `Connection::select()` Applies TCA Restrictions Silently

`TYPO3\CMS\Core\Database\Connection::select()` (the convenience wrapper, not the QueryBuilder fluent API) applies the **default `RestrictionContainer`**, which includes `DeletedRestriction`, `HiddenRestriction`, and `StartTimeRestriction` per TCA. Code reaching for "I just want to read the row" misses every soft-deleted / hidden / time-restricted record.

This bites hardest in admin tooling, cleanup scripts, and audit features that explicitly want to see deleted records.

### Search Pattern

```bash
grep -rne "->select(\|Connection::select" Classes/ Tests/
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

### Search Pattern

```bash
grep -rn "callUserFunction\|userFunc\s*=" Classes/ Tests/ Configuration/
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

## v13 Backend CSS Reuses Generic Extension Class Names

TYPO3 v13's backend stylesheet introduced new core UI components under short, generic class names — `.settings` in particular is now the Settings-module component (`background`, `border`, `box-shadow`, `display: grid; grid-template-columns: 1fr`). An extension's own Fluid markup from the v12 era that happens to use the same generic class name — often as a harmless, purely semantic marker with no CSS meaning at the time — silently inherits the new component's styling: a `<form class="... settings">` gets boxed with a border and every direct child (including buttons) gets stretched to full width by CSS Grid's default `stretch` alignment.

This is invisible in a code diff: the port itself may not touch the affected template at all, since nothing in the markup or the extension's own code changed. It only shows up as a rendering regression against the real running v13 instance. `form-inline` / `form-inline-spaced` (Bootstrap 4-era utility classes many v12 extensions carry) are similarly dead weight in v13 — `form-inline` is reduced to `display: inline`, `form-inline-spaced` doesn't exist in the v13 core CSS at all — so leaving them in place is harmless on its own, but doesn't provide the layout it used to either.

**Search Pattern** — grep every class actually used in the extension's Fluid templates against the installed core CSS, not just the ones that look obviously TYPO3-specific:

```bash
# Extract classes used in the extension's own templates
grep -rhoP 'class="\K[^"]+' Resources/Private/**/*.html | tr ' ' '\n' | sort -u > /tmp/ext-classes.txt

# Check which ones the v13 core backend CSS now defines
while read -r cls; do
    grep -q "^\.${cls}{" vendor/typo3/cms-backend/Resources/Public/Css/backend.css \
        && echo "COLLISION: .$cls"
done < /tmp/ext-classes.txt
```

**Fix** — drop classes that no longer serve a real purpose (checked against the current core CSS) rather than assuming old markup is inert:

```html
<!-- ❌ v12-era Bootstrap 4 classes, "settings" collides with the v13 core component -->
<f:form class="form-inline form-inline-spaced settings" ...>

<!-- ✅ let the surrounding Bootstrap defaults (or an explicit, non-colliding class) handle layout -->
<f:form ...>
```

**How to verify**: this class of bug will not surface from a code review or a green test suite, load the actual backend module in a real running v13 instance and visually compare against v12. See `verification.md`.

---

## v14 `AjaxRequest.withQueryArguments()` Dropped Its Decode-Neutralization Step — Undocumented, Version-Specific

`@typo3/core/ajax/ajax-request.js`'s `withQueryArguments()` builds the query string differently per major version, and the difference is invisible from an extension's own unchanged JS.

- **v12/v13**: routes the value through `InputTransformer.toSearchParams()`, which builds a `URLSearchParams`, serializes it, and then calls `decodeURI()` on the result. That `decodeURI()` step neutralizes exactly one prior layer of manual `encodeURIComponent()`/percent-encoding on the value (it leaves URI-reserved characters like `%3A`/`%2F` alone, but un-escapes a stray `%25` back to `%`). A caller that manually pre-encodes a value before passing it to `withQueryArguments()` still gets the correct, single-encoded value on the wire.
- **v14**: `withQueryArguments()` was rewired to use the new `@typo3/core/factory/url-factory.js` module (`UrlFactory.createSearchParams()`) instead, appending the value onto the request URL's own `URLSearchParams` via `.append()` — with **no decode step at all**. The exact same manually-pre-encoded value now gets percent-encoded a second time (`%` → `%25`), producing a broken double-encoded value server-side (e.g. `1%3A%2Fcamino%2Ffile.pdf` → `1%253A%252Fcamino%252Ffile.pdf`).

This is a real, reproducible behavior change (verified live: a v14 backend AJAX call using this pattern throws `InvalidFileException`/HTTP 500 when resolving the resulting identifier server-side; the identical code on v12/v13 resolves correctly), **not documented as a Breaking change** in TYPO3's official `Documentation/Changelog/14.0/` — the only related entry is `Feature-107104-IntroduceUrlFactoryJavaScriptModule.rst`, which describes `UrlFactory` as a new standalone utility and says nothing about `AjaxRequest`'s own internal implementation switching to it.

**Symptom**: any extension JS that does `new AjaxRequest(url).withQueryArguments({ key: encodeURIComponent(someIdentifier) })` (a common pattern for passing a FAL combined identifier, `storage:/path`, which contains `:`/`/`) breaks silently on v14 with no visible in-page error unless the calling code explicitly renders an error state — the request still completes, the content container still refreshes, only the server-side resolution fails.

**Search Pattern**:

```bash
grep -rn "encodeURIComponent" Resources/Public/JavaScript/
# For each hit, check whether it feeds a .withQueryArguments()/.get() call, not a .post()/.put() body
```

**Fix** — do not pre-encode; let `withQueryArguments()` do it once (this is the shape that works correctly on v12, v13, AND v14):

```js
// ❌ Correct-looking on v12/v13, silently broken on v14
new AjaxRequest(actionUrl).withQueryArguments({ target: encodeURIComponent(identifier) }).get();

// ✅ Works on all three
new AjaxRequest(actionUrl).withQueryArguments({ target: identifier }).get();
```

**Verification caveat**: do not assume a version-spanning "pre-existing bug" claim from extension-code similarity alone. The extension's own JS file can be byte-identical across v12/v13/v14 checkouts while TYPO3 core's own `ajax-request.js`/`input-transformer.js`/`url-factory.js` differ per version — read the actual vendored core JS for **each** version under test (`vendor/typo3/cms-core/Resources/Public/JavaScript/ajax/*.js`) rather than diffing only the extension's own file, and reproduce the exact call path in Node (or a real browser) per version before generalizing a fix across a v12/v13/v14 maintenance-branch set. See `verification.md`.

---

## See Also

- `upgrade-v11-to-v12.md` — v12 FormEngine DI nodes (`setData()` workaround for [#100670](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/12.4/Deprecation-100670-DIAwareFormEngineNodes.html))
- `upgrade-v12-to-v13.md` — `#[AsEventListener]` v13+ vs `Services.yaml` tag for v12 compat
- `upgrade-v13-to-v14.md` — `LoginProviderInterface::modifyView()`, `StandaloneView` removal, `ModifyPageLayoutOnLoginProviderSelectionEvent` signature drift
- `api-changes.md` — full deprecated/removed API tables per version
