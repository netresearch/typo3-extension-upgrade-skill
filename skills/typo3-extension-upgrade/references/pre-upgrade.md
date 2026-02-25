# Pre-Upgrade Checklist

Use this checklist before starting a TYPO3 extension upgrade.

## Repository Status

- [ ] Git repository is clean (`git status` shows no changes)
- [ ] On main/master branch
- [ ] All tests passing on current version
- [ ] CI/CD pipeline green

## Current State Assessment

- [ ] Document current TYPO3 version support
- [ ] Document current PHP version requirement
- [ ] List all deprecated API usages (run PHPStan with deprecation rules)
- [ ] Identify database-related code (for DBAL migration)
- [ ] Check for direct `$GLOBALS['TSFE']` usage
- [ ] Check for `GeneralUtility::_GET/POST/GP` usage
- [ ] Check for `PDO::PARAM_*` constants

## Dependency Check

- [ ] Review `composer.json` dependencies
- [ ] Check for abandoned packages
- [ ] Verify testing framework compatibility
- [ ] Check Rector/PHPStan version requirements

## Backup & Branch

- [ ] Create feature branch: `git checkout -b feature/typo3-v12-v13-upgrade`
- [ ] Tag current state: `git tag v-before-upgrade`
- [ ] Ensure local development environment works

## Environment Setup

- [ ] DDEV or local environment ready
- [ ] Can install TYPO3 v12.4 LTS
- [ ] Can install TYPO3 v13.4 LTS
- [ ] Database access configured

## Documentation Review

- [ ] Read TYPO3 v12 changelog: https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/12.0/Index.html
- [ ] Read TYPO3 v13 changelog: https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/13.0/Index.html
- [ ] Review breaking changes relevant to extension

## Version Hardcoding Locations

Check ALL files with hardcoded PHP/TYPO3 versions before starting:

- [ ] `composer.json` (require.php, require.typo3/cms-core)
- [ ] `.github/workflows/*.yml` (PHP version matrix)
- [ ] `.ddev/config.yaml` (php_version)
- [ ] `Dockerfile`, `docker-compose.yml`
- [ ] `rector.php` (LevelSetList, SetList)
- [ ] `fractor.php` (Typo3LevelSetList)
- [ ] `phpstan.neon` (phpVersion)
- [ ] `Build/phpstan/*.neon`
- [ ] `README.md`, `Documentation/*.rst` (version requirements)
- [ ] `ext_emconf.php` (constraints)

## Planning Phase (Major Upgrades)

When performing major upgrades (PHP version drops, TYPO3 major versions), complete these steps before any code changes:

1. **List all files with hardcoded versions** (composer.json, CI, Docker, Rector)
2. **Document scope** - how many places need changes?
3. **Present plan to user** for approval
4. **Track progress** with todo list

### Understand Your Situation First

Before running any automated tools, answer these questions:

- **Current TYPO3 support**: What versions does `composer.json` currently support?
- **Current PHP requirement**: What `php` constraint is in `composer.json`?
- **Test status**: Do tests pass on the current version? (If not, fix first)
- **Target TYPO3 version(s)**: Which LTS version(s) will you support?
- **Target PHP version(s)**: What PHP versions must the extension run on?
- **Dropping support?**: Will you drop support for older TYPO3/PHP versions?
- **Business driver**: Client requirement? Security? End-of-life support?
- **Dependencies**: Do other extensions/projects depend on this one?

### Risk Assessment

- Does this extension have tests? (No tests = high risk)
- Does it use complex APIs (DBAL, Extbase, Fluid ViewHelpers)?
- Does it hook into TYPO3 internals (PSR-15, signals/slots)?
- How much custom JavaScript/CSS? (May need build system updates)

**If any answer raises concerns, document them before proceeding.**

## Team Communication

- [ ] Inform team about upgrade work
- [ ] Set up review process for changes
- [ ] Plan testing strategy
