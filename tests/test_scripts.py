#!/usr/bin/env python3
"""Behaviour tests for the shell scripts this repository ships.

Covered: skills/typo3-extension-upgrade/scripts/scan-deprecations.sh,
Build/Scripts/check-plugin-version.sh with the Build/hooks/pre-push hook that
calls it, and scripts/verify-harness.sh. evals/run-ab-test.sh is not covered:
it calls the `claude` CLI, which runs paid model requests.

Each test builds a small TYPO3 extension, git repository or harness layout in
a temporary directory, runs one script as a subprocess and checks its exit
code and output. Standard library only; run with
``python3 tests/test_scripts.py``.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN = ROOT / "skills" / "typo3-extension-upgrade" / "scripts" / "scan-deprecations.sh"
CHECK_VERSION = ROOT / "Build" / "Scripts" / "check-plugin-version.sh"
PRE_PUSH = ROOT / "Build" / "hooks" / "pre-push"
VERIFY_HARNESS = ROOT / "scripts" / "verify-harness.sh"

# Isolate git from the developer's configuration (signing, hooks, templates).
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}
ENV.pop("GITHUB_ACTIONS", None)

# One entry per check function of scan-deprecations.sh, in the order of its
# `labels` array: the label the script prints, and a file (path relative to
# the extension root, content) that only this check is meant to find.
SCAN_CASES: list[tuple[str, str, str]] = [
    (
        "v7 → v8 Upgrade: Database Layer: TYPO3_DB → Doctrine DBAL",
        "Classes/Repo.php",
        "$GLOBALS['TYPO3_DB']->exec_SELECTquery('*', 'pages');",
    ),
    (
        "v7 → v8 Upgrade: ExtJS/Prototype Removal",
        "Resources/Public/JavaScript/app.js",
        "Ext.onReady(function () {});",
    ),
    (
        "v7 → v8 Upgrade: Icon Factory",
        "Classes/Icon.php",
        "IconUtility::getSpriteIcon('x');",
    ),
    (
        "v8 → v9 Upgrade: Site Configuration Introduction",
        "Configuration/TypoScript/setup.typoscript",
        "config.baseURL = https://example.org/",
    ),
    (
        "v8 → v9 Upgrade: PSR-15 Middleware",
        "Classes/Frontend.php",
        "class Frontend extends tslib_fe {}",
    ),
    (
        "v8 → v9 Upgrade: Routing API",
        "Configuration/RealUrl.php",
        "$config['tx_realurl'] = [];",
    ),
    (
        "v8 → v9 Upgrade: Signal/Slot Deprecation Start",
        "Classes/Wiring.php",
        "$dispatcher->connect(A::class, 'b', C::class, 'd');",
    ),
    (
        "v9 → v10 Upgrade: Symfony 5 Upgrade",
        "Classes/Command/ImportCommand.php",
        "$this->setDescription('Import');",
    ),
    (
        "v9 → v10 Upgrade: Dependency Injection",
        "Classes/Factory.php",
        "GeneralUtility::makeInstance(Foo::class);",
    ),
    (
        "v9 → v10 Upgrade: PSR-14 Events",
        "Classes/Emitter.php",
        "$this->emit('afterSave');",
    ),
    (
        "v9 → v10 Upgrade: Fluid Namespace",
        "Resources/Private/Templates/Show.html",
        "{namespace v=Vendor\\Demo}",
    ),
    (
        "v10 → v11 Upgrade: Fluid Standalone",
        "Classes/Mailer.php",
        "$view = new StandaloneView();",
    ),
    (
        "v10 → v11 Upgrade: Backend Controller Changes",
        "Classes/Controller/DemoController.php",
        "class DemoController extends ActionController {}",
    ),
    (
        "v10 → v11 Upgrade: TCA Wizard Changes",
        "Configuration/TCA/tx_demo.php",
        "'wizards' => [],",
    ),
    (
        "v11 → v12 Upgrade: Doctrine DBAL 4.x (Critical)",
        "Classes/Query.php",
        "$q->setParameter('a', 1, PDO::PARAM_INT);",
    ),
    # Label 15 repeats label 14 in the script; its case is the `->execute()`
    # pattern, asserted separately below because the label alone cannot show it.
    (
        "v11 → v12 Upgrade: Doctrine DBAL 4.x (Critical)",
        "Classes/Run.php",
        "$statement->execute();",
    ),
    (
        "v11 → v12 Upgrade: GeneralUtility Deprecated Methods",
        "Classes/Input.php",
        "GeneralUtility::_GP('id');",
    ),
    (
        "v11 → v12 Upgrade: TCA Required Field",
        "Configuration/TCA/tx_required.php",
        "'eval' => 'required,trim',",
    ),
    (
        "v11 → v12 Upgrade: TCA inputLink → type=link",
        "Configuration/TCA/tx_link.php",
        "'renderType' => 'inputLink',",
    ),
    (
        "v11 → v12 Upgrade: Form Element Data Structure",
        "Classes/Element.php",
        "$id = $this->data['itemFormElID'];",
    ),
    (
        "v11 → v12 Upgrade: xml2array Null Handling",
        "Classes/Xml.php",
        "$data = GeneralUtility::xml2array($xml);",
    ),
    (
        "v11 → v12 Upgrade: FlexForm Structure (Fractor handles)",
        "Configuration/FlexForms/Demo.xml",
        "<required>1</required>",
    ),
    (
        "v11 → v12 Upgrade: TypoScript Conditions",
        "Configuration/TypoScript/cond.typoscript",
        "[end]",
    ),
    (
        "v11 → v12 Upgrade: Click Menu Parameters",
        "Classes/Menu.php",
        "BackendUtility::wrapClickMenuOnIcon($icon, 'pages', 1);",
    ),
    (
        "v12 → v13 Upgrade: Request Attributes (Critical)",
        "Classes/User.php",
        "$user = $GLOBALS['TSFE']->fe_user;",
    ),
    (
        "v12 → v13 Upgrade: Site Sets Introduction",
        "Documentation/Notes.txt",
        "see ext_typoscript_setup.typoscript",
    ),
    (
        "v12 → v13 Upgrade: Backend Module Registration",
        "ext_tables.php",
        "ExtensionManagementUtility::registerModule('demo');",
    ),
    (
        "v12 → v13 Upgrade: TCA Type Changes",
        "Configuration/TCA/tx_text.php",
        "'type' => 'text',",
    ),
    (
        "v13 → v14 Upgrade: TypoScript/TSconfig Callables Require #[AsAllowedCallable] Attribute (Critical)",
        "Configuration/TypoScript/user.typoscript",
        "lib.demo.userFunc = Vendor\\Demo\\Hook->render",
    ),
    (
        "v13 → v14 Upgrade: ExtensionConfiguration::getAll() Removed (Critical)",
        "Classes/Settings.php",
        "$all = $extensionConfiguration->getAll();",
    ),
    (
        "v13 → v14 Upgrade: Doctrine DBAL 4.x Type::getName() Removed",
        "Classes/Schema.php",
        "$name = $column->getType()->getName();",
    ),
    (
        "v13 → v14 Upgrade: Icon::SIZE_* Constants Replaced with IconSize Enum",
        "Classes/Icons.php",
        "$size = Icon::SIZE_SMALL;",
    ),
    (
        "v13 → v14 Upgrade: f:uri.resource Not Available in Non-Extbase Modules",
        "Resources/Private/Templates/Module.html",
        "<link href=\"{f:uri.resource(path: 'Css/a.css')}\" />",
    ),
    (
        "v13 → v14 Upgrade: Scheduler Interface Signature Changes",
        "Classes/Task/DemoTask.php",
        "class DemoTask implements AdditionalFieldProviderInterface {}",
    ),
    (
        "v13 → v14 Upgrade: Bootstrap 5 CSS Class Changes",
        "Resources/Private/Partials/Button.html",
        '<button class="btn btn-default">Save</button>',
    ),
    (
        "v13 → v14 Upgrade: TCA renderType vs type",
        "Classes/Hook/FormHook.php",
        "if ($field['config']['type'] === 'input') {}",
    ),
    (
        "v13 → v14 Upgrade: ARIA Accessibility Requirements",
        "Resources/Private/Layouts/Default.html",
        '<nav aria-label="Main">',
    ),
    (
        "v13 → v14 Upgrade: GeneralUtility::getIndpEnv() Deprecated -- Use NormalizedParams (v14.3)",
        "Classes/Host.php",
        "$host = GeneralUtility::getIndpEnv('HTTP_HOST');",
    ),
    (
        "PHP 8.4 Compatibility: Implicit Nullable Parameters (Critical)",
        "Classes/Service.php",
        "public function find(string $name = null): void {}",
    ),
    (
        "PHP 8.4 Compatibility: TCA Items Array Format",
        "Configuration/TCA/tx_items.php",
        "'items' => [",
    ),
    (
        "PSR-7 Request Handling Patterns: Query Parameter Access in Context Classes",
        "Classes/Legacy.php",
        "$id = (int)$_GET['id'];",
    ),
    (
        "SC_OPTIONS Hooks to PSR-14 Events: Page Visibility Hooks (Critical for v12+)",
        "ext_localconf.php",
        "$GLOBALS['TYPO3_CONF_VARS']['SC_OPTIONS']['additionalQueryRestrictions'][] = X::class;",
    ),
    (
        "Symfony Component Deprecations: PropertyInfo Type Class (Symfony 7.3+)",
        "Classes/Types.php",
        "use Symfony\\Component\\PropertyInfo\\Type;",
    ),
    (
        "api-traps.md: Connection::select() applies TCA restrictions silently",
        "Classes/Pages.php",
        "$rows = $connection->select(['*'], 'pages');",
    ),
    (
        "api-traps.md: callUserFunction() bypasses Dependency Injection",
        "Classes/Caller.php",
        "GeneralUtility::callUserFunction($ref, $params, $this);",
    ),
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=cwd, env=ENV, capture_output=True, text=True, check=False
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TempDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class ScanDeprecationsTest(TempDirTestCase):
    def scan(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run(["bash", str(SCAN), *args], cwd=self.tmp)

    def test_cases_cover_every_check(self) -> None:
        script = SCAN.read_text(encoding="utf-8")
        self.assertEqual(script.count("\ncheck_"), len(SCAN_CASES))

    def test_each_check_finds_its_pattern(self) -> None:
        for index, (label, relpath, content) in enumerate(SCAN_CASES):
            with self.subTest(check=f"check_{index:02d}", label=label):
                ext = self.tmp / f"ext{index:02d}"
                write(ext / relpath, content + "\n")
                result = self.scan(str(ext))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"=== {label} ===", result.stdout)
                self.assertIn(f"{relpath}:1:", result.stdout)

    def test_execute_pattern_reports_the_dbal_group(self) -> None:
        write(self.tmp / "Classes" / "Run.php", "$statement->execute();\n")
        result = self.scan(str(self.tmp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "=== v11 → v12 Upgrade: Doctrine DBAL 4.x (Critical) ===", result.stdout
        )
        self.assertIn("1 pattern group(s) matched", result.stdout)

    def test_required_anywhere_in_the_eval_list_is_reported(self) -> None:
        write(
            self.tmp / "Configuration" / "TCA" / "a.php", "'eval' => 'trim,required',\n"
        )
        result = self.scan(str(self.tmp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("=== v11 → v12 Upgrade: TCA Required Field ===", result.stdout)

    def test_migrated_required_option_is_not_reported(self) -> None:
        write(
            self.tmp / "Configuration" / "TCA" / "a.php",
            "'required' => true, 'eval' => 'trim',\n",
        )
        result = self.scan(str(self.tmp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("TCA Required Field", result.stdout)

    def test_explicit_nullable_parameter_is_not_reported(self) -> None:
        write(
            self.tmp / "Classes" / "Service.php",
            "public function find(?string $name = null): void {}\n",
        )
        result = self.scan(str(self.tmp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Implicit Nullable Parameters", result.stdout)

    def test_clean_extension_reports_no_matches(self) -> None:
        write(self.tmp / "Classes" / "Clean.php", "<?php\n\ndeclare(strict_types=1);\n")
        result = self.scan(str(self.tmp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "No matches for any documented deprecation/removal/trap pattern.",
            result.stdout,
        )

    def test_counts_matched_groups(self) -> None:
        write(self.tmp / "Classes" / "Two.php", "IconUtility::x();\nxml2array($x);\n")
        result = self.scan(str(self.tmp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 pattern group(s) matched", result.stdout)

    def test_missing_path_fails(self) -> None:
        result = self.scan(str(self.tmp / "missing"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("error: path not found:", result.stderr)

    def test_defaults_to_current_directory(self) -> None:
        write(self.tmp / "Classes" / "Legacy.php", "$id = $_POST['id'];\n")
        result = self.scan()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Query Parameter Access in Context Classes", result.stdout)


class CheckPluginVersionTest(TempDirTestCase):
    def setUp(self) -> None:
        super().setUp()
        write(
            self.tmp / ".claude-plugin" / "plugin.json",
            '{"name": "demo", "version": "1.2.3"}\n',
        )
        for cmd in (
            ["git", "init", "-q"],
            ["git", "add", "."],
            ["git", "commit", "-q", "-m", "init"],
        ):
            result = run(cmd, cwd=self.tmp)
            self.assertEqual(result.returncode, 0, result.stderr)

    def tag(self, name: str) -> None:
        result = run(["git", "tag", name], cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)

    def check(self) -> subprocess.CompletedProcess[str]:
        return run(["bash", str(CHECK_VERSION)], cwd=self.tmp)

    def test_untagged_head_passes(self) -> None:
        self.assertEqual(self.check().returncode, 0)

    def test_matching_tag_passes(self) -> None:
        self.tag("v1.2.3")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_matching_tag_without_prefix_passes(self) -> None:
        self.tag("1.2.3")
        self.assertEqual(self.check().returncode, 0)

    def test_mismatching_tag_fails(self) -> None:
        self.tag("v1.2.4")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "version (1.2.3) does not match any semver tag at HEAD", result.stderr
        )
        self.assertIn("1.2.4", result.stderr)

    def test_non_semver_tag_is_ignored(self) -> None:
        self.tag("release-candidate")
        self.assertEqual(self.check().returncode, 0)

    def test_pre_push_hook_runs_the_check(self) -> None:
        self.tag("v2.0.0")
        result = run(["bash", str(PRE_PUSH)], cwd=self.tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match any semver tag at HEAD", result.stderr)


class VerifyHarnessTest(TempDirTestCase):
    def verify(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run(["bash", str(VERIFY_HARNESS), "--format=text", *args], cwd=self.tmp)

    def complete_level2(self) -> None:
        write(
            self.tmp / "AGENTS.md",
            "# Demo\n\n## Commands\n\nSee [docs](docs/ARCHITECTURE.md).\n",
        )
        write(self.tmp / "docs" / "ARCHITECTURE.md", "# Architecture\n")
        write(
            self.tmp / ".github" / "workflows" / "harness-verify.yml", "name: Harness\n"
        )

    def test_empty_directory_fails(self) -> None:
        result = self.verify("--level=1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("AGENTS.md missing at repo root", result.stdout)
        self.assertIn("Summary: Level 1 NONE | 4 error(s), 0 warning(s)", result.stdout)

    def test_complete_level2_passes(self) -> None:
        self.complete_level2()
        result = self.verify("--level=2")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "Summary: Level 2 COMPLETE | 0 error(s), 0 warning(s)", result.stdout
        )

    def test_complete_level3_without_git_passes(self) -> None:
        # A local PR template keeps check_pr_template from querying the GitHub API.
        self.complete_level2()
        write(self.tmp / ".github" / "pull_request_template.md", "## Summary\n")
        write(self.tmp / ".envrc", "git config core.hooksPath Build/hooks\n")
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Git hooks auto-setup via .envrc", result.stdout)
        self.assertIn(
            "Summary: Level 3 COMPLETE | 0 error(s), 0 warning(s)", result.stdout
        )

    def test_long_agents_md_fails(self) -> None:
        self.complete_level2()
        write(self.tmp / "AGENTS.md", "# Demo\n\n## Commands\n" + "line\n" * 150)
        result = self.verify("--level=1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("(should be under 150)", result.stdout)

    def test_broken_reference_is_a_warning(self) -> None:
        self.complete_level2()
        write(self.tmp / "AGENTS.md", "# Demo\n\n## Commands\n\n[x](missing.md)\n")
        result = self.verify("--check=refs")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("missing.md not found", result.stdout)

    def test_undocumented_composer_script_is_a_warning(self) -> None:
        self.complete_level2()
        write(self.tmp / "AGENTS.md", "# Demo\n\n## Commands\n\n`composer ci:test`\n")
        write(self.tmp / "composer.json", '{"scripts": {}}\n')
        result = self.verify("--check=commands")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn(
            "composer ci:test: no matching composer.json script", result.stdout
        )

    def test_github_format_emits_annotations(self) -> None:
        result = run(
            ["bash", str(VERIFY_HARNESS), "--format=github", "--level=1"], cwd=self.tmp
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "::error file=AGENTS.md::AGENTS.md missing at repo root", result.stdout
        )

    def test_invalid_arguments_are_rejected(self) -> None:
        self.assertEqual(self.verify("--level=4").returncode, 1)
        self.assertEqual(self.verify("--check=bogus").returncode, 1)
        self.assertEqual(self.verify("--bogus").returncode, 1)


if __name__ == "__main__":
    unittest.main()
