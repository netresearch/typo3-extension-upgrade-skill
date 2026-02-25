# Understanding Rector/Fractor Output

**CRITICAL: Always run with `--dry-run` first and review the output before applying changes.**

## Reading Rector Dry-Run Output

```bash
./vendor/bin/rector process --dry-run
```

The output shows:
- **File path**: Which file will be modified
- **Rule name**: Which Rector rule triggered (e.g., `ExtbaseControllerActionsMustReturnResponseInterfaceRector`)
- **Diff**: Exact changes that will be made (red = removed, green = added)

**Before applying, check:**
1. Does the rule apply correctly to your code context?
2. Are there edge cases Rector might miss?
3. Will this break dual-version compatibility? (See `dual-compatibility.md`)

## Reading Fractor Dry-Run Output

```bash
./vendor/bin/fractor process --dry-run
```

Fractor modifies non-PHP files. Watch for:
- **TypoScript**: Removed/renamed options
- **FlexForms**: Changed XML structures
- **YAML configurations**: Service definitions, routes
