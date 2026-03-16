# TYPO3 Extension Upgrade Skill

A Claude Code skill for systematically upgrading TYPO3 extensions to newer LTS versions.

**Developed by [Netresearch DTT GmbH](https://www.netresearch.de/)**

## 🔌 Compatibility

This is an **Agent Skill** following the [open standard](https://agentskills.io) originally developed by Anthropic and released for cross-platform use.

**Supported Platforms:**
- ✅ Claude Code (Anthropic)
- ✅ Cursor
- ✅ GitHub Copilot
- ✅ Other skills-compatible AI agents

> Skills are portable packages of procedural knowledge that work across any AI agent supporting the Agent Skills specification.


## Overview

This skill guides extension developers through upgrading TYPO3 extensions (third-party or custom) to newer TYPO3 LTS versions with modern PHP compatibility. It covers:

- **Extension Scanner** - Backend module for diagnosing deprecated/removed APIs
- **Rector** - Automated PHP code migrations
- **Fractor** - Automated non-PHP file migrations (FlexForms, TypoScript, YAML, Fluid)
- **PHPStan** - Static analysis
- **PHPUnit** - Testing framework setup

## Scope

This skill is for **extension developers** upgrading extension code. It does NOT cover:
- Upgrading TYPO3 project installations
- TYPO3 core upgrades
- Site/instance migrations

## Supported Upgrade Paths

| From | To | Status |
|------|-----|--------|
| v7 | v8 | Documented |
| v8 | v9 | Documented |
| v9 | v10 | Documented |
| v10 | v11 | Documented |
| v11 | v12 | Documented |
| v12 | v13 | Documented |
| v13 | v14 | Monitoring |
| v12 | v12+v13 (dual) | Documented |

## Installation

### Marketplace (Recommended)

Add the [Netresearch marketplace](https://github.com/netresearch/claude-code-marketplace) once, then browse and install skills:

```bash
# Claude Code
/plugin marketplace add netresearch/claude-code-marketplace
```

### npx ([skills.sh](https://skills.sh))

Install with any [Agent Skills](https://agentskills.io)-compatible agent:

```bash
npx skills add https://github.com/netresearch/typo3-extension-upgrade-skill --skill typo3-extension-upgrade
```

### Download Release

Download the [latest release](https://github.com/netresearch/typo3-extension-upgrade-skill/releases/latest) and extract to your agent's skills directory.

### Git Clone

```bash
git clone https://github.com/netresearch/typo3-extension-upgrade-skill.git
```

### Composer (PHP Projects)

```bash
composer require netresearch/typo3-extension-upgrade-skill
```

Requires [netresearch/composer-agent-skill-plugin](https://github.com/netresearch/composer-agent-skill-plugin).
## Usage

The skill activates automatically when Claude detects:
- TYPO3 extension upgrade requests
- Compatibility issues with newer TYPO3 versions
- Extension modernization tasks

Example prompts:
- "Upgrade this extension to TYPO3 v13"
- "Make this extension compatible with TYPO3 12 and 13"
- "Fix the deprecated API usage in this TYPO3 extension"

## Contents

```
typo3-extension-upgrade-skill/
├── SKILL.md                 # Main skill instructions
├── README.md                # This file
├── assets/                  # Configuration templates
│   ├── rector.php           # Rector configuration
│   ├── fractor.php          # Fractor configuration
│   ├── phpstan.neon         # PHPStan configuration
│   ├── phpunit.xml          # PHPUnit configuration
│   └── .php-cs-fixer.php    # PHP-CS-Fixer configuration
└── references/              # Detailed documentation
    ├── api-changes.md       # Version-specific API migrations (v7-v14)
    └── pre-upgrade.md       # Pre-upgrade checklist
```

## Key Resources

### Official TYPO3 Changelogs

- [v14 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-14.html)
- [v13 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-13.html)
- [v12 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-12.html)
- [v11 Changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog-11.html)

### Tools

- [TYPO3 Rector](https://github.com/sabbelasichon/typo3-rector) - PHP migrations
- [TYPO3 Fractor](https://github.com/andreaswolf/fractor) - Non-PHP migrations
- [Extension Scanner](https://docs.typo3.org/m/typo3/reference-coreapi/main/en-us/ExtensionArchitecture/HowTo/UpdateExtensions/ExtensionScanner.html) - API diagnostics

## Author

**Netresearch DTT GmbH**
[https://www.netresearch.de/](https://www.netresearch.de/)

Netresearch is a Leipzig-based technology company specializing in e-commerce, logistics, and TYPO3 solutions. With extensive experience in TYPO3 extension development and maintenance, Netresearch contributes to the TYPO3 ecosystem through open-source extensions and community involvement.

## License

This project uses split licensing:

- **Code** (scripts, workflows, configs): [MIT](LICENSE-MIT)
- **Content** (skill definitions, documentation, references): [CC-BY-SA-4.0](LICENSE-CC-BY-SA-4.0)

See the individual license files for full terms.

## Credits

Developed and maintained by [Netresearch DTT GmbH](https://www.netresearch.de/).
