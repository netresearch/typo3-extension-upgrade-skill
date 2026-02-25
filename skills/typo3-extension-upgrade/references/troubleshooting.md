# Troubleshooting

## Rector Broke My Code

If Rector applied changes that broke the extension:

### Immediate Recovery

```bash
# Option 1: Revert all Rector changes
git checkout -- .

# Option 2: Revert specific files
git diff --name-only | xargs git checkout --

# Option 3: If already committed
git revert HEAD
```

### Diagnose the Problem

1. Run Rector on a single file to isolate: `./vendor/bin/rector process path/to/file.php --dry-run`
2. Check which rule caused the issue (look at rule name in output)
3. Exclude problematic rules in `rector.php`:

```php
return static function (RectorConfig $rectorConfig): void {
    $rectorConfig->skip([
        // Skip a specific rule globally
        \Ssch\TYPO3Rector\Rector\v12\SomeProblematicRector::class,

        // Skip a rule for specific files
        \Ssch\TYPO3Rector\Rector\v12\SomeRector::class => [
            __DIR__ . '/Classes/Problematic.php',
        ],
    ]);
};
```

### Common Rector Failures

- **Extbase action return types**: May break if controller has custom response handling
- **Dependency injection**: May fail with complex factory patterns
- **Signal/slot to PSR-14**: Requires manual event class creation

## PHPStan Errors After Upgrade

If PHPStan reports many errors after Rector:

1. **Baseline approach**: Create a baseline for pre-existing issues:
   ```bash
   ./vendor/bin/phpstan analyse --generate-baseline
   ```

2. **Incremental fix**: Fix errors file by file, not all at once

3. **Common post-upgrade errors**:
   - Missing return types (add them manually)
   - Deprecated method calls Rector missed (check changelog)
   - Type mismatches from changed TYPO3 APIs

## Tests Fail After Upgrade

1. **Identify scope**: How many tests fail? All? Some?
2. **Check test framework**: Is `typo3/testing-framework` compatible with target TYPO3?
3. **Check test fixtures**: Do fixtures use deprecated APIs?
4. **Update test bootstrap**: May need new bootstrap for changed TYPO3 internals

## Extension Installs But Doesn't Work

If the extension installs without errors but functionality is broken:

1. **Check backend logs**: TYPO3 Admin Tools > Log
2. **Check PHP error log**: Often reveals missing classes/methods
3. **Clear all caches**: Admin Tools > Maintenance > Flush TYPO3 and PHP Caches
4. **Verify database**: Extension Manager may need to update database schema
