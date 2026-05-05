# TYPO3 v13 → v14 Upgrade Guide

**Context:** TYPO3 v14.3 LTS released 2026-04-21. v14 introduces the largest breaking-change sweep in several cycles: 98 breaking + 31 deprecations + 105 features + 16 important entries, **all landed in v14.0**. v14.1/14.2/14.3 added zero breaking changes — the LTS stability promise.

**Free support window:** bugfix until 2027-12-31, security until 2029-06-30.

---

## Version constraints

### composer.json (v14-only)

```json
{
    "require": {
        "php": "^8.2",
        "typo3/cms-core": "^14.3"
    }
}
```

- **PHP floor:** `8.2` (unchanged from v12/v13). Ceiling: `8.5.99`.
- Composer ≥ 2.1 required by core ([get.typo3.org/version/14](https://get.typo3.org/version/14)).

### ext_emconf.php (v14-only)

```php
'constraints' => [
    'depends' => [
        'typo3' => '14.0.0-14.3.99',
        'php' => '8.2.0-8.5.99',
    ],
],
```

> ⚠️ `ext_emconf.php` itself is **deprecated** in v14.2 (#108345) for v15 removal. Maintain during the transition but mirror all metadata in `composer.json`. **Classic mode now requires `composer.json`** (Breaking #108310).

### Dual v13 + v14

See companion file `dual-compatibility.md` and also the typo3-conformance-skill's `references/v13-v14-dual-compatibility.md` for the full matrix. Short form (inside the `require` block of `composer.json`):

```json
{
    "require": {
        "typo3/cms-core": "^13.4 || ^14.3"
    }
}
```

---

## Rector v14 configuration

```php
// rector.php
$rectorConfig->sets([
    LevelSetList::UP_TO_PHP_82,
    Typo3LevelSetList::UP_TO_TYPO3_14,
    Typo3SetList::CODE_QUALITY,
    Typo3SetList::GENERAL,
]);
```

**New in v14 Rector CLI:**
- `--only=<RuleClass>` — run a single rule (47 v14 rules available)
- `--no-progress-bar` — cleaner CI output

**47 v14-specific Rector rules** ship in `rules/TYPO314/v0/` (46) and `rules/TYPO314/v2/` (1). Highlights (full list in [`ssch/typo3-rector`](https://github.com/sabbelasichon/typo3-rector/tree/main/rules/TYPO314)):

- `RequireComposerJsonInClassicModeRector` (#108310)
- `UseStrictTypesInFluidViewHelpersRector` (#108148)
- `UseStrictTypesInExtbaseArgumentRector` (#107777)
- `MigratePassingAnArrayOfConfigurationValuesToExtbaseAttributesRector`
- `UsageOfValidationAttributesAtMethodLevelRector` (#108227)
- `RemovePageRendererMethodsRector` (#108055)
- `MigrateRemovedMailMessageSendRector` (#108097)
- `UseStrongerCryptographicAlgorithmForHMACRector` (#106307)
- `IntroduceStrictTypingForCacheBeAndFeRector` (#107315)
- `MoveSchedulerFrequencyOptionsToTCARector` (#107488)
- `MigrateSysRedirectDefaultTypeRector` (#107963)
- `RemoveHttpResponseCompressionRector` (#107943)
- `RemoveConcatenateAndCompressHandlerRector` (#108055)
- `RemoveExternalOptionFromAssetRendererRector` (#107927)
- `RemoveRandomSubpageOptionRector` (#107654)
- `RemoveParameterInAuthenticationServiceRector` (#106869)
- `RemoveRegistrationOfMetadataExtractorsRector` (#107783)
- `RemoveTcaControlOptionSearchFieldsRector` (#106972)
- `RemoveIsStaticControlOptionRector` (#106863)
- `RemoveFieldSearchConfigOptionsRector` (#106976)
- `RemoveEvalYearFlagRector` (#98070)
- `MigrateTcaOptionAllowedRecordTypesForPageTypesRector` (#108557 → #97898)

---

## Key breaking changes (v13 → v14.0)

All 98 breakers landed in v14.0. **If your extension compiles against v14.0, it's already forward-compatible with 14.1/14.2/14.3.**

### Critical (most-hit)

| Change | Forge | Search | Fix |
|---|---|---|---|
| `TypoScriptFrontendController` class removed | #107831 | `grep -rn "TSFE\|TypoScriptFrontendController\|frontend.controller" Classes/` | Use `$request->getAttribute('frontend.page.information')`, `PageRenderer::addHeaderData()` |
| Fluid 5 strict VH typing | #108148 | `grep -rL "function render.*:" Classes/ViewHelpers/` | Add typed args + `render(): string` |
| Fluid VH `renderStatic()` removed | #108148 | `grep -rn "renderStatic" Classes/` | Non-static `render()` |
| Fluid `StandaloneView`, `TemplateView` removed | #105377 | `grep -rn "StandaloneView\|AbstractTemplateView" Classes/` | `Core\View\ViewFactoryInterface` |
| Fluid underscore-prefixed variables forbidden | #108148 | `grep -rEn '\{_[a-zA-Z]' Resources/Private/` | Rename variables |
| Extbase annotation namespace removed | #107229 | `grep -rn "@Extbase\\\\Annotation" Classes/` | PHP attributes `#[Validate]`, `#[IgnoreValidation]` |
| Magic repo finders removed | #105377 | `grep -rn "->findBy[A-Z]\|->findOneBy[A-Z]\|->countBy[A-Z]" Classes/` | `createQuery()` builder |
| `HashService` (Extbase) removed | #105377 | `grep -rn "HashService\|GeneralUtility::hmac(" Classes/` | Core cipher service (#108002) |
| TCA `subtype_value_field` / `subtypes_addlist` removed | #105377 | `grep -rn "subtype_value_field\|subtypes_addlist" Configuration/TCA/` | Record-type flex-form handling |
| TCA `control.searchFields` removed | #106972 | `grep -rn "searchFields" Configuration/TCA/` | Configurable search TCA |
| TCA `eval=year` removed | #98070 | `grep -rn "'eval'.*year" Configuration/TCA/` | integer field |
| TCA `pages.url` field removed | #17406 | `grep -rn "pages\\.url" Configuration/TCA/` | typolink page type |
| `tt_content.list_type` removed | #105538, #105377 | `grep -rn "list_type\|addPlugin" Configuration/` | CType-only plugins; drop 2nd/3rd args of `addPlugin()` |
| EXT:form hooks removed (10 hooks) | many | `grep -rn "'afterBuildingFinished'\|beforeFormCreate\|beforeFormSave\|beforeFormDelete\|beforeFormDuplicate\|initializeFormElement\|beforeRemoveFromParentRenderable\|afterInitializeCurrentPage\|afterSubmit\|beforeRendering" ext_localconf.php Classes/` | PSR-14 events |
| `TypolinkBuilder` signature changed | #106405 | `grep -rn "extends AbstractTypolinkBuilder\|TypolinkBuilder" Classes/` | Implement `TypolinkBuilderInterface` |
| Bootstrap Modal → native `<dialog>` | #107443 | `grep -rn "Modal.advanced\|bootstrap.*modal" Resources/Public/JavaScript/` | Native `<dialog>` API |
| `MailMessage->send()` removed | #108097 | `grep -rn "->send()" Classes/` (filter for MailMessage) | Dispatch via Mailer service |
| HMAC algorithm SHA1 → SHA256 | #106307 | automatic via Rector | Rotate existing HMACs if persisted |
| `LoginProviderInterface::render()` → `modifyView()` | internal | `grep -rn "LoginProviderInterface" Classes/` | Implement `modifyView()` |
| `composer.json` required in classic mode | #108310 | check presence in project root | Create `composer.json` with extension autoload |
| CSS/JS concat & compression removed | #108055 | `grep -rn "concatenateCss\|concatenateJs\|compressCss\|compressJs" Configuration/TypoScript/` | Use build tools (webpack/vite) |
| Frontend HTTP compression removed | #107943 | check TypoScript `config.compressionLevel` | Delegate to web server (nginx/Apache) |
| Extbase `ActionController->view` typed | #105377 | — | Type-check any custom controller overrides |

### v14.x deprecations (still callable, removed in v15.0)

These are **not** v14.0 breakers — code keeps working — but you should migrate to silence deprecation notices and prepare for v15.

| Change | Forge / Source | Search | Fix |
|---|---|---|---|
| `GeneralUtility::getIndpEnv()` deprecated (v14.3) | `cms-core` v14.3 — `Classes/Utility/GeneralUtility.php` `@deprecated` annotation | `grep -rn "GeneralUtility::getIndpEnv\|::getIndpEnv(" Classes/ Configuration/` | `$request->getAttribute('normalizedParams')->getRemoteAddress()` etc. — see `api-changes.md` |

> ⚠️ **AI-assistant warning**: Don't trust Gemini Code Assist on `getIndpEnv()` deprecation timing. It has hallucinated v13.0 deprecation / v14.0 removal, and falsely claimed `NormalizedParams::createFromServerParams()` was removed in v14.0 in favour of a non-existent `NormalizedParamsFactory`. All three claims are wrong — verified false against `typo3/cms-core` v14.3.0 vendor source. Always grep the `@deprecated` annotation in `vendor/typo3/cms-core/` to confirm.

The migration is safe across **v12.4 + v13.4 + v14.3** without compatibility shims — `NormalizedParams` is in core since v9.4, `normalizedParams` request attribute since v10. Reference migration: [netresearch/t3x-nr-passkeys-be commit b2cfd8e](https://github.com/netresearch/t3x-nr-passkeys-be/commit/b2cfd8e) (v14.3 upgrade [PR #57](https://github.com/netresearch/t3x-nr-passkeys-be/pull/57)).

### FAL / File handling

| Change | Forge | Fix |
|---|---|---|
| `AbstractFile::getIdentifier/setIdentifier()` removed | #101392 | Use concrete `File`/`Folder` methods |
| `rename/copyTo/moveTo` moved to `File` | #106427 | Cast to `File` before calling |
| `FileNameValidator` custom regex in ctor removed | #105733 | Configure via TypoScript/YAML |
| `Folder->getSubFolder()` throws | #105920 | Catch `FolderDoesNotExistException` |
| Metadata extractor registration | #107783 | Implement `MetadataExtractorInterface` + autoconfigure tag |
| Backend avatar provider registration | #107871 | Autoconfigure tag instead of `$GLOBALS` |
| `LocalPreviewHelper`, `LocalCropScaleMaskHelper` removed | #107403 | Core replacements |

### Cache

| Change | Forge | Fix |
|---|---|---|
| Cache interfaces strict-typed | #107315 | Match new signatures in custom backends |
| `AbstractBackend::__construct($context, $options)` → `__construct(array $options = [])` | #107315 | Drop `$context` parameter |
| `FreezableBackendInterface` removed | #107310 | Drop `isFrozen()`, `freeze()` |
| `CacheHashCalculator` public methods removed | #108277 | Use internal API |

### Backend / UI / JS

| Change | Forge | Fix |
|---|---|---|
| `@typo3/backend/document-save-actions.js` removed | — | Replaced in-core |
| `@typo3/backend/wizard.js` removed | — | New wizard API |
| `@typo3/t3editor/*` removed | — | Inline CodeMirror config |
| `@typo3/backend/page-tree/page-tree-element` removed | — | Use `@typo3/backend/tree/page-tree-element` |
| Button API reworked | #107884, #107823 | Use ComponentFactory |
| DocHeader MetaInformation deprecated | #107813 | New DocHeader API |
| Workspace Freeze Editing removed | #107323 | — |
| "Database Relations" module removed | #97151 | — |
| Reports interfaces reworked | #107791 | New submodule overview |

### Install / bootstrap

| Change | Forge | Impact |
|---|---|---|
| `typo3/install.php` removed → backend-route | #107536, #107537 | BC maintained; no change needed for most |
| `Environment::getComposerRootPath()` removed | #107482 | Inject composer root via DI |
| Extension title from `composer.json` | #108304 | Ensure `"description"` in `composer.json` |
| Install Tool now in backend routing | #107536 | Bookmarks/URLs may change |

---

## Expanded gotchas (v13 → v14)

The table above is the index. The sections below expand the entries that have surprised real upgrades.

### `LoginProviderInterface::modifyView()` — added in v14, two pitfalls

v14 added `modifyView(ViewInterface $view, ServerRequestInterface $request): void` alongside `render()`. Two things bite:

**1. The implementation must exist on v14, even if unused on v13.** Implementations conditional on a `class_exists()` check are too late — the interface contract is checked at class-load time. Just add the method and accept that v13 ignores it.

**2. `modifyView()` returns the template name as a RELATIVE path, not an `EXT:` path.** Returning `'EXT:my_ext/Resources/Private/Templates/Login/PasskeyLogin.html'` results in Fluid trying to resolve it as a template **name** (no file found). Return `'Login/PasskeyLogin'` and register the extension's template root path on the view:

```php
public function modifyView(ServerRequestInterface $request, ViewInterface $view): string
{
    if ($view instanceof FluidViewAdapter) {
        $view->getRenderingContext()->getTemplatePaths()->setTemplateRootPaths([
            'EXT:my_ext/Resources/Private/Templates/',
        ]);
    }
    return 'Login/PasskeyLogin'; // relative, no .html, no EXT: prefix
}
```

### `StandaloneView` removed — guard the test mocks too

> **Breaking #105377** — already in the table above.

The table covers production code. The hidden hit is in **tests**: `createMock(StandaloneView::class)` raises `Cannot use undefined class` when `StandaloneView` is missing under v14. Tests that need to run on the v12/v13/v14 matrix must guard:

```php
public function testRendersLoginScreen(): void
{
    if (!class_exists(\TYPO3\CMS\Fluid\View\StandaloneView::class)) {
        self::markTestSkipped('StandaloneView removed in TYPO3 v14');
    }
    $view = $this->createMock(\TYPO3\CMS\Fluid\View\StandaloneView::class);
    // ...
}
```

This is also why `dg/bypass-finals` alone doesn't help — bypass-finals strips `final`, but it cannot conjure a class that no longer exists.

### `ModifyPageLayoutOnLoginProviderSelectionEvent` — view parameter type drifts across versions

The event's view parameter type changes per major:

| TYPO3 | Type of `$view` |
|---|---|
| v12 | `StandaloneView` (concrete) |
| v13 | `StandaloneView \| ViewInterface` (union) |
| v14 | `ViewInterface` (StandaloneView removed) |

Cross-version event-listener tests cannot just `createMock(ViewInterface::class)` — on v12 the constructor type-hint rejects it. Detect the parameter type via reflection and mock the right one:

```php
$rc = new \ReflectionClass(ModifyPageLayoutOnLoginProviderSelectionEvent::class);
$paramType = $rc->getConstructor()->getParameters()[0]->getType();

$mockTarget = match (true) {
    $paramType instanceof \ReflectionUnionType,
    $paramType?->getName() === StandaloneView::class
        => StandaloneView::class,
    default => ViewInterface::class,
};
$view = $this->createMock($mockTarget);
```

### PHPStan v14 without `saschaegerer/phpstan-typo3`

`saschaegerer/phpstan-typo3` v2 supports v13 only — drop it on v12 **and** v14 CI runs. Without the extension, two ergonomic issues appear on the v14 build:

1. `GeneralUtility::getIndpEnv()` returns a union type rather than the narrow `string` the extension would have inferred — assignments to `string` properties trigger `assign.propertyType` errors. Migrate to `NormalizedParams` (see "v14.x deprecations" above) or annotate the call site.
2. Ignores written for v12 issues (e.g. `StandaloneView`, `Connection::PARAM_*` int-vs-enum) match nothing on v14 and trigger PHPStan's "ignored error not matched" warning.

**Fix** in `Build/phpstan.neon`:

```neon
parameters:
    # Don't fail on v12-only ignores when running against v14
    reportUnmatchedIgnoredErrors: false

    ignoreErrors:
        # v12-only — Connection::PARAM_* is int there, ParameterType enum on v13/v14
        - '~Parameter \\#2 \\$type of method .* expects .*, int given~'
        # v14-only — getIndpEnv() returns union; remove once migrated to NormalizedParams
        - '~Parameter .* of method .*::setRemoteAddress\(\) expects string, .* given~'
```

`phpstan/extension-installer` auto-loads any installed PHPStan extensions — once you remove `saschaegerer/phpstan-typo3` from the v12/v14 dev branches' `composer.json`, no manual `includes:` cleanup is needed.

---

## Dual-version compatibility guards

If supporting v13 + v14:

```php
use TYPO3\CMS\Core\Utility\GeneralUtility;

// HashService shim
if (class_exists(\TYPO3\CMS\Core\Crypto\HashService::class)) {
    $hash = GeneralUtility::makeInstance(\TYPO3\CMS\Core\Crypto\HashService::class);
} else {
    $hash = GeneralUtility::makeInstance(\TYPO3\CMS\Extbase\Security\Cryptography\HashService::class);
}

// Icon sizes — IconSize::SMALL fatals on v13 if referenced unguarded.
// Use class_exists() on the enum, not the `?? fallback` pattern.
$iconSize = class_exists(\TYPO3\CMS\Core\Imaging\IconSize::class)
    ? \TYPO3\CMS\Core\Imaging\IconSize::SMALL
    : 'small';
$icon = $iconFactory->getIcon('name', $iconSize);
```

**PHP attributes on v13+v14 dual code** — do NOT guard `use` / `#[…]` at runtime (attributes are declarative; `class_exists()` on a use statement is a no-op). Options:

- Don't add the v14-only attribute on dual-version code paths; accept missing progressive enhancement on v13.
- Ship polyfill stub classes for v13 that declare `Authorize` / `RateLimit` as no-op `#[\Attribute]` — see `typo3-conformance-skill` `references/v13-v14-dual-compatibility.md` for the full pattern.
- Branch the controller: two concrete classes, one with attributes, selected via service factory based on `(new Typo3Version())->getMajorVersion()`.

See `dual-compatibility.md` for the full v12+v13 matrix; the typo3-conformance-skill repo ships `references/v13-v14-dual-compatibility.md` with the v13+v14 variant and the polyfill-stub example.

---

## Composer dependencies (v14-only dev toolkit)

```json
{
    "require-dev": {
        "a9f/typo3-fractor": "^0.4",
        "friendsofphp/php-cs-fixer": "^3.88",
        "phpstan/phpstan": "^2.1",
        "phpstan/phpstan-deprecation-rules": "^2.0",
        "phpstan/phpstan-phpunit": "^2.0",
        "phpunit/phpunit": "^11.2.5 || ^12.1.2 || ^13.0.2",
        "rector/rector": "^2.0",
        "ssch/typo3-rector": "^3.0",
        "typo3/testing-framework": "^9.5"
    }
}
```

Notes:
- `typo3/testing-framework:^9.5` covers **both v13 and v14** cores — a single branch, no matrix split.
- PHPUnit constraint mirrors what testing-framework 9.5.0 accepts: `^11.2.5 || ^12.1.2 || ^13.0.2`.
- Symfony components are pulled transitively (`^7.3` by core); no explicit `require` needed unless you depend on a specific component.

---

## Fractor v14 rule highlights

`a9f/typo3-fractor` handles non-PHP migrations:

- `composer.json` normalization (schema + metadata from `ext_emconf.php`)
- `.htaccess` template refresh (#105244)
- TypoScript: `<INCLUDE_TYPOSCRIPT:>` → `@import`
- FlexForm XML cleanups
- `ext_tables.php` split into `Configuration/Backend/Modules.php` + `Routes.php` (prep for v15 removal, #109438)

Invoke:

```bash
vendor/bin/fractor process --dry-run
vendor/bin/fractor process
```

---

## Post-upgrade operational checks

### 1. Extension Scanner

Install Tool → Upgrade → Scan Extension Files. v14 matchers cover the #105377 umbrella + Fluid 5 + FAL + Cache interfaces.

### 2. Important #109585 — serialized credential data fix

**Scope:** Any site that ran **v14.2** (not 14.0, not 14.1).
**Action:** Run the v14.3 upgrade wizard (Install Tool → Upgrade → Upgrade Wizards). It unserializes `be_users.uc`/`user_settings`, strips password fields, re-serializes.
**When to skip:** Sites upgrading directly from v13 → v14.3.

### 3. HMAC rotation (for persisted HMACs)

SHA1 → SHA256 (#106307) may invalidate any HMACs you persisted in tables (e.g., one-time tokens in custom extensions). If applicable, force regeneration at first use after upgrade.

---

## Upgrade smoke tests

```bash
# Composer sanity
composer validate --strict
composer why typo3/cms-core

# No deprecated v13 code paths
vendor/bin/phpstan analyse --level=8 Classes/
vendor/bin/rector process --dry-run

# Fluid templates
vendor/bin/fluid analyze Resources/Private/

# No removed APIs remain
grep -rnE "HashService|->findBy[A-Z]|GLOBALS\[.TSFE.\]|StandaloneView|renderStatic|subtype_value_field|control\\.searchFields" Classes/ Configuration/
```

---

## Release notes template (after upgrade)

```markdown
## Breaking changes

- Dropped TYPO3 v12 support. Minimum TYPO3 version is now **13.4 LTS**; v14.3 LTS is supported.
- Dropped PHP 8.1 support. Minimum PHP is **8.2**.
- Removed all uses of `Extbase\Security\Cryptography\HashService` — tokens issued before this release are invalidated.
- TypoScript `<INCLUDE_TYPOSCRIPT:>` replaced with `@import`.

## Migration notes

- If upgrading from v1.x (v12-compatible), run `vendor/bin/rector process` before deploying.
- Site settings are now delivered via Site Sets (`Configuration/Sets/`) — migrate from `Configuration/TypoScript/constants.typoscript` if not already done.
```

See also:
- `api-changes.md` — detailed v13→v14 API migration patterns
- `third-party-dependency-upgrades.md` — Symfony 7.3 / Doctrine DBAL 4 / Fluid 5 / CKE 47 bump notes
- `verification.md` — success criteria
- TYPO3 Core Changelog 14.0–14.3: https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-14.html
