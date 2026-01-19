---
description: "Run Rector migrations for TYPO3 upgrade"
---

# Run Rector Migrations

Execute Rector with TYPO3-specific rules for automated code migration.

## Steps

1. **Verify Rector installation**
   ```bash
   composer show ssch/typo3-rector || composer require --dev ssch/typo3-rector
   ```

2. **Create/update rector.php config**

   ```php
   <?php
   use Rector\Config\RectorConfig;
   use Ssch\TYPO3Rector\Set\Typo3LevelSetList;

   return static function (RectorConfig $rectorConfig): void {
       $rectorConfig->paths([
           __DIR__ . '/Classes',
           __DIR__ . '/Configuration',
       ]);

       // Choose target version
       $rectorConfig->sets([
           Typo3LevelSetList::UP_TO_TYPO3_12,
           // or Typo3LevelSetList::UP_TO_TYPO3_13,
       ]);
   };
   ```

3. **Run in dry-run mode first**
   ```bash
   vendor/bin/rector process --dry-run
   ```

4. **Review proposed changes**
   - Check each file modification
   - Verify no unwanted changes
   - Note any manual follow-ups needed

5. **Apply changes**
   ```bash
   vendor/bin/rector process
   ```

6. **Run tests after Rector**
   ```bash
   composer test
   # or
   vendor/bin/phpunit
   ```

7. **Commit Rector changes**
   ```bash
   git add -A
   git commit -m "refactor: apply Rector TYPO3 {version} migrations"
   ```
