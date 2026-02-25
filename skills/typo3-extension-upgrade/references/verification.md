# Verification & Success Criteria

An upgrade is complete when ALL of these are verified.

## Tool Verification

- [ ] `rector process --dry-run` shows no changes
- [ ] `fractor process --dry-run` shows no changes
- [ ] `phpstan analyse` passes without errors
- [ ] `php-cs-fixer fix --dry-run` shows no changes
- [ ] All unit tests pass
- [ ] All functional tests pass (if any)

## Real-World Testing (Required)

**Do NOT skip this step.** Automated tools cannot catch all issues.

1. **Create a fresh TYPO3 instance** matching target version:
   ```bash
   # Example with DDEV
   ddev config --project-type=typo3 --php-version=8.3
   ddev start
   ddev composer create typo3/cms-base-distribution:^13.4
   ```

2. **Install the upgraded extension** via Composer (from local path or packagist)

3. **Verify core functionality**:
   - [ ] Extension installs without errors
   - [ ] Backend module loads (if applicable)
   - [ ] Frontend plugin renders (if applicable)
   - [ ] All content elements work (if applicable)
   - [ ] Form finishers execute (if applicable)
   - [ ] Scheduled tasks run (if applicable)

4. **Check browser console** for JavaScript errors

5. **Test with real content** if possible (import from existing site)

## Documentation Updated

- [ ] `README.md` reflects new version requirements
- [ ] `CHANGELOG.md` documents the upgrade
- [ ] `composer.json` constraints are correct
