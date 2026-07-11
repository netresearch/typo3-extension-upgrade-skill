#!/usr/bin/env bash
# scan-deprecations.sh - deterministic grep scan for TYPO3 API deprecations/removals
#
# Mirrors every "Search Pattern" grep recipe documented in references/api-changes.md
# (v7->v8 through v13->v14, PHP 8.4, PSR-7, SC_OPTIONS) and the two architectural-trap
# recipes in references/api-traps.md. This skill owns upgrade-execution detection; the
# underlying v13/v14 breaking-change FACTS are canonical in typo3-conformance's
# references/v14-deprecations.md.
#
# Usage: scripts/scan-deprecations.sh <path>
#   <path>  extension root to scan (contains Classes/, Configuration/, Resources/, ...)
#
# Exit: 0 always (report-only; findings are informational, not pass/fail).

set -euo pipefail

target="${1:-.}"

if [[ ! -d "$target" ]]; then
    echo "error: path not found: $target" >&2
    exit 1
fi

findings=0

check_00() {
    grep -rn "\$GLOBALS\['TYPO3_DB'\]\|exec_SELECTquery\|exec_INSERTquery\|exec_UPDATEquery\|exec_DELETEquery" "$target/Classes/"
}

check_01() {
    grep -rn "Ext\.onReady\|new Ext\.\|Prototype\.\|Element\.extend" "$target/Resources/"
}

check_02() {
    grep -rn "IconUtility::\|t3skin\|t3lib_iconWorks" "$target/Classes/"
}

check_03() {
    grep -rn "sys_domain\|config\.baseURL\|absRefPrefix\s*=\s*auto" "$target/Configuration/"
}

check_04() {
    grep -rn "AbstractUserAuthentication\|tslib_fe\|tslib_cObj" "$target/Classes/"
}

check_05() {
    grep -rn "tx_realurl\|cooluri\|simulatestatic" "$target/Configuration/"
}

check_06() {
    grep -rn "SignalSlotDispatcher\|->connect\(" "$target/Classes/"
}

check_07() {
    grep -rn "Symfony\\\\Component\\\\Console\\\\Command\|setDescription\|setHelp" "$target/Classes/Command/"
}

check_08() {
    grep -rn "GeneralUtility::makeInstance\|ObjectManager::get" "$target/Classes/"
}

check_09() {
    grep -rn "SignalSlotDispatcher\|->emit\|->connect\(" "$target/Classes/"
}

check_10() {
    grep -rn "{namespace\|xmlns:f=" "$target/Resources/Private/"
}

check_11() {
    grep -rn "TYPO3Fluid\|StandaloneView\|setTemplatePathAndFilename" "$target/Classes/"
}

check_12() {
    grep -rn "extends ActionController\|AbstractModule" "$target/Classes/Controller/"
}

check_13() {
    grep -rn "'wizards'\s*=>\|'wizard_'" "$target/Configuration/TCA/"
}

check_14() {
    grep -rn "PDO::PARAM_" "$target/Classes/"
}

check_15() {
    # -e: pattern starts with "-", which grep would otherwise parse as an option
    grep -rne "->execute()" "$target/Classes/"
}

check_16() {
    grep -rn "GeneralUtility::_GET\|GeneralUtility::_POST\|GeneralUtility::_GP" "$target/Classes/"
}

check_17() {
    grep -rn "'eval'.*'required'" "$target/Configuration/TCA/"
}

check_18() {
    grep -rn "'renderType' => 'inputLink'" "$target/Configuration/TCA/"
}

check_19() {
    grep -rn "itemFormElID" "$target/Classes/"
}

check_20() {
    grep -rn "xml2array" "$target/Classes/"
}

check_21() {
    grep -rn "<required>1</required>" "$target/Configuration/FlexForms/"
}

check_22() {
    grep -rn "\[end\]" "$target/Configuration/TypoScript/"
}

check_23() {
    grep -rn "BackendUtility::wrapClickMenuOnIcon\|getClickMenuOnIconTagParameters" "$target/Classes/"
}

check_24() {
    grep -rn "\$TSFE->fe_user\|\$GLOBALS\['TSFE'\]->fe_user" "$target/Classes/"
}

check_25() {
    grep -rn "ext_typoscript_setup\.typoscript\|ext_typoscript_constants" "$target"
}

check_26() {
    grep -rn "registerModule\|TYPO3_MOD_PATH" "$target/ext_tables.php"
}

check_27() {
    grep -rn "'type'\s*=>\s*'text'" "$target/Configuration/TCA/"
}

check_28() {
    # Find TypoScript userFunc references
    grep -rn "userFunc\|preUserFunc\|postUserFunc" "$target/Configuration/TypoScript/"
    # Find PHP classes referenced in TypoScript
    # -e: pattern starts with "-", which grep would otherwise parse as an option
    grep -rne "->render\|->process" "$target/Configuration/TypoScript/" | grep -v "#"
}

check_29() {
    grep -rn "ExtensionConfiguration::getAll\|->getAll()" "$target/Classes/"
}

check_30() {
    # -e: pattern starts with "-", which grep would otherwise parse as an option
    grep -rne "->getName()\|Type::getName" "$target/Classes/"
}

check_31() {
    grep -rn "Icon::SIZE_SMALL\|Icon::SIZE_DEFAULT\|Icon::SIZE_MEDIUM\|Icon::SIZE_LARGE" "$target/Classes/"
}

check_32() {
    grep -rn "f:uri.resource\|<f:uri.resource" "$target/Resources/Private/"
}

check_33() {
    grep -rn "AdditionalFieldProviderInterface\|getAdditionalFields" "$target/Classes/Task/"
}

check_34() {
    grep -rn "btn-default\|badge-primary\|badge-success\|badge-danger\|badge-warning\|badge-info" "$target/Resources/"
}

check_35() {
    grep -rn "\['config'\]\['type'\]" "$target/Classes/Hook/"
}

check_36() {
    grep -rn "role=\"main\"\|aria-label\|aria-describedby" "$target/Resources/Private/"
}

check_37() {
    grep -rn "GeneralUtility::getIndpEnv\|::getIndpEnv(" "$target/Classes/" "$target/Configuration/"
}

check_38() {
    # Find parameters with null default but no explicit nullable type
    grep -rn '\(.*\$[a-zA-Z_]* = null\)' "$target/Classes/" | grep -v '?[a-zA-Z_\\]*\s*\$'
}

check_39() {
    grep -rn "'items'\s*=>\s*\[" "$target/Configuration/TCA/" | grep -v "label"
}

check_40() {
    grep -rn "\$_GET\['\|\$_POST\['" "$target/Classes/"
}

check_41() {
    grep -rn "SC_OPTIONS\['t3lib/class.t3lib_page.php'\]" "$target/ext_localconf.php"
    grep -rn "additionalQueryRestrictions" "$target/ext_localconf.php"
}

check_42() {
    grep -rn "PropertyInfo\\Type\|Type::BUILTIN_TYPE_" "$target/Classes/"
}

check_43() {
    # -e: pattern starts with "-", which grep would otherwise parse as an option
    grep -rne "->select(\|Connection::select" "$target/Classes"
}

check_44() {
    grep -rn "callUserFunction\|userFunc\s*=" "$target/Classes" "$target/Configuration"
}

labels=(
    "v7 → v8 Upgrade: Database Layer: TYPO3_DB → Doctrine DBAL"
    "v7 → v8 Upgrade: ExtJS/Prototype Removal"
    "v7 → v8 Upgrade: Icon Factory"
    "v8 → v9 Upgrade: Site Configuration Introduction"
    "v8 → v9 Upgrade: PSR-15 Middleware"
    "v8 → v9 Upgrade: Routing API"
    "v8 → v9 Upgrade: Signal/Slot Deprecation Start"
    "v9 → v10 Upgrade: Symfony 5 Upgrade"
    "v9 → v10 Upgrade: Dependency Injection"
    "v9 → v10 Upgrade: PSR-14 Events"
    "v9 → v10 Upgrade: Fluid Namespace"
    "v10 → v11 Upgrade: Fluid Standalone"
    "v10 → v11 Upgrade: Backend Controller Changes"
    "v10 → v11 Upgrade: TCA Wizard Changes"
    "v11 → v12 Upgrade: Doctrine DBAL 4.x (Critical)"
    "v11 → v12 Upgrade: Doctrine DBAL 4.x (Critical)"
    "v11 → v12 Upgrade: GeneralUtility Deprecated Methods"
    "v11 → v12 Upgrade: TCA Required Field"
    "v11 → v12 Upgrade: TCA inputLink → type=link"
    "v11 → v12 Upgrade: Form Element Data Structure"
    "v11 → v12 Upgrade: xml2array Null Handling"
    "v11 → v12 Upgrade: FlexForm Structure (Fractor handles)"
    "v11 → v12 Upgrade: TypoScript Conditions"
    "v11 → v12 Upgrade: Click Menu Parameters"
    "v12 → v13 Upgrade: Request Attributes (Critical)"
    "v12 → v13 Upgrade: Site Sets Introduction"
    "v12 → v13 Upgrade: Backend Module Registration"
    "v12 → v13 Upgrade: TCA Type Changes"
    "v13 → v14 Upgrade: TypoScript/TSconfig Callables Require #[AsAllowedCallable] Attribute (Critical)"
    "v13 → v14 Upgrade: ExtensionConfiguration::getAll() Removed (Critical)"
    "v13 → v14 Upgrade: Doctrine DBAL 4.x Type::getName() Removed"
    "v13 → v14 Upgrade: Icon::SIZE_* Constants Replaced with IconSize Enum"
    "v13 → v14 Upgrade: f:uri.resource Not Available in Non-Extbase Modules"
    "v13 → v14 Upgrade: Scheduler Interface Signature Changes"
    "v13 → v14 Upgrade: Bootstrap 5 CSS Class Changes"
    "v13 → v14 Upgrade: TCA renderType vs type"
    "v13 → v14 Upgrade: ARIA Accessibility Requirements"
    "v13 → v14 Upgrade: GeneralUtility::getIndpEnv() Deprecated -- Use NormalizedParams (v14.3)"
    "PHP 8.4 Compatibility: Implicit Nullable Parameters (Critical)"
    "PHP 8.4 Compatibility: TCA Items Array Format"
    "PSR-7 Request Handling Patterns: Query Parameter Access in Context Classes"
    "SC_OPTIONS Hooks to PSR-14 Events: Page Visibility Hooks (Critical for v12+)"
    "Symfony Component Deprecations: PropertyInfo Type Class (Symfony 7.3+)"
    "api-traps.md: Connection::select() applies TCA restrictions silently"
    "api-traps.md: callUserFunction() bypasses Dependency Injection"
)

fns=(
    check_00
    check_01
    check_02
    check_03
    check_04
    check_05
    check_06
    check_07
    check_08
    check_09
    check_10
    check_11
    check_12
    check_13
    check_14
    check_15
    check_16
    check_17
    check_18
    check_19
    check_20
    check_21
    check_22
    check_23
    check_24
    check_25
    check_26
    check_27
    check_28
    check_29
    check_30
    check_31
    check_32
    check_33
    check_34
    check_35
    check_36
    check_37
    check_38
    check_39
    check_40
    check_41
    check_42
    check_43
    check_44
)

for i in "${!fns[@]}"; do
    fn="${fns[$i]}"
    label="${labels[$i]}"
    out=$("$fn" 2>/dev/null || true)
    if [[ -n "$out" ]]; then
        echo "=== $label ==="
        echo "$out"
        echo
        findings=$((findings + 1))
    fi
done

if [[ "$findings" -eq 0 ]]; then
    echo "No matches for any documented deprecation/removal/trap pattern."
else
    echo "$findings pattern group(s) matched -- cross-check against"
    echo "references/api-changes.md and typo3-conformance's v14-deprecations.md"
    echo "before treating a match as a required fix. Some patterns (e.g. PHP 8.4"
    echo "implicit-nullable) have false positives that need manual review."
fi
