---
description: "Assess extension upgrade complexity and effort"
---

# Upgrade Assessment

Quickly assess the upgrade complexity for a TYPO3 extension.

## Steps

1. **Detect versions**
   ```bash
   # Read current constraints
   cat composer.json | grep -A5 "typo3/cms"
   cat ext_emconf.php | grep -A5 "constraints"
   ```

2. **Run Extension Scanner**
   ```bash
   # If DDEV available
   ddev exec vendor/bin/typo3 extensionscanner:scan --extension-key=myext
   ```

3. **Count deprecated usages**
   ```bash
   # Search for common deprecations
   grep -r "GeneralUtility::makeInstance" Classes/ | wc -l
   grep -r "\$GLOBALS\['TYPO3_DB'\]" Classes/ | wc -l
   grep -r "extbase" Configuration/TCA/ | wc -l
   ```

4. **Check for Rector support**
   ```bash
   # Verify rector is available
   composer show ssch/typo3-rector 2>/dev/null || echo "Rector not installed"
   ```

5. **Generate assessment**

   ```
   ## Upgrade Assessment: {extension}

   ### Version Jump
   From: TYPO3 {from} / PHP {php_from}
   To: TYPO3 {to} / PHP {php_to}

   ### Complexity: {Low|Medium|High|Very High}

   ### Issues Found
   - Deprecated APIs: X occurrences
   - Removed features: Y usages
   - Configuration changes: Z files

   ### Recommended Approach
   1. {approach}

   ### Estimated Effort
   - Automated: X hours
   - Manual: Y hours
   - Testing: Z hours
   - **Total: N hours**
   ```

6. **Recommend next steps**
   - Suggest starting with Rector
   - Identify manual-only changes
   - Propose testing strategy
