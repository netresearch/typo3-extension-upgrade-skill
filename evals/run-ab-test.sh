#!/usr/bin/env bash
# A/B test: WITHOUT skill vs WITH skill
# Measures: output volume (chars), assertion pass rate, specificity
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_FILE="$REPO_DIR/skills/typo3-extension-upgrade/SKILL.md"
REFS_DIR="$REPO_DIR/skills/typo3-extension-upgrade/references"
RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$RESULTS_DIR"

# Build skill context from SKILL.md + all references
build_skill_context() {
    echo "=== SKILL CONTEXT ==="
    cat "$SKILL_FILE"
    echo ""
    for ref in "$REFS_DIR"/*.md; do
        echo "=== $(basename "$ref") ==="
        cat "$ref"
        echo ""
    done
}

SKILL_CONTEXT=$(build_skill_context)

# Read evals
EVALS_FILE="$SCRIPT_DIR/evals.json"
EVAL_COUNT=$(jq length "$EVALS_FILE")

echo "Running A/B tests on $EVAL_COUNT evals..."
echo "================================================"

# CSV header
echo "eval_name,without_chars,with_chars,without_assertions_pass,with_assertions_pass,without_assertions_total,with_assertions_total" > "$RESULTS_DIR/ab-results.csv"

for i in $(seq 0 $((EVAL_COUNT - 1))); do
    EVAL_NAME=$(jq -r ".[$i].name" "$EVALS_FILE")
    EVAL_PROMPT=$(jq -r ".[$i].prompt" "$EVALS_FILE")
    ASSERTION_COUNT=$(jq ".[$i].assertions | length" "$EVALS_FILE")

    echo ""
    echo "[$((i+1))/$EVAL_COUNT] Testing: $EVAL_NAME"

    # A: WITHOUT skill (no tools, no skill context)
    echo "  Running WITHOUT skill..."
    WITHOUT_OUTPUT=$(claude -p --tools "" --model sonnet --no-session-persistence \
        --disable-slash-commands \
        "$EVAL_PROMPT Answer concisely with specific technical details." 2>/dev/null || echo "ERROR")
    echo "$WITHOUT_OUTPUT" > "$RESULTS_DIR/${EVAL_NAME}_without.txt"
    WITHOUT_CHARS=${#WITHOUT_OUTPUT}

    # B: WITH skill (include skill context as system prompt)
    echo "  Running WITH skill..."
    WITH_OUTPUT=$(claude -p --tools "" --model sonnet --no-session-persistence \
        --disable-slash-commands \
        --append-system-prompt "You are a TYPO3 extension upgrade specialist. Use the following skill knowledge to answer questions precisely:

$SKILL_CONTEXT" \
        "$EVAL_PROMPT Answer concisely with specific technical details." 2>/dev/null || echo "ERROR")
    echo "$WITH_OUTPUT" > "$RESULTS_DIR/${EVAL_NAME}_with.txt"
    WITH_CHARS=${#WITH_OUTPUT}

    # Check assertions
    WITHOUT_PASS=0
    WITH_PASS=0
    for j in $(seq 0 $((ASSERTION_COUNT - 1))); do
        ASSERT_TYPE=$(jq -r ".[$i].assertions[$j].type" "$EVALS_FILE")
        ASSERT_VALUE=$(jq -r ".[$i].assertions[$j].value" "$EVALS_FILE")
        ASSERT_DESC=$(jq -r ".[$i].assertions[$j].description" "$EVALS_FILE")

        if [ "$ASSERT_TYPE" = "content_contains" ]; then
            if echo "$WITHOUT_OUTPUT" | grep -qiF "$ASSERT_VALUE"; then
                WITHOUT_PASS=$((WITHOUT_PASS + 1))
            fi
            if echo "$WITH_OUTPUT" | grep -qiF "$ASSERT_VALUE"; then
                WITH_PASS=$((WITH_PASS + 1))
            fi
        fi
    done

    echo "  WITHOUT: ${WITHOUT_CHARS} chars, ${WITHOUT_PASS}/${ASSERTION_COUNT} assertions"
    echo "  WITH:    ${WITH_CHARS} chars, ${WITH_PASS}/${ASSERTION_COUNT} assertions"

    echo "$EVAL_NAME,$WITHOUT_CHARS,$WITH_CHARS,$WITHOUT_PASS,$WITH_PASS,$ASSERTION_COUNT,$ASSERTION_COUNT" >> "$RESULTS_DIR/ab-results.csv"
done

echo ""
echo "================================================"
echo "Results saved to $RESULTS_DIR/ab-results.csv"

# Generate summary
echo ""
echo "=== SUMMARY ==="
awk -F',' 'NR>1 {
    without_pass += $4; with_pass += $5; total += $6;
    without_chars += $2; with_chars += $3;
    count++
} END {
    printf "Evals: %d\n", count
    printf "WITHOUT skill: %d/%d assertions (%.0f%%)\n", without_pass, total, (without_pass/total)*100
    printf "WITH skill:    %d/%d assertions (%.0f%%)\n", with_pass, total, (with_pass/total)*100
    printf "Avg output WITHOUT: %.0f chars\n", without_chars/count
    printf "Avg output WITH:    %.0f chars\n", with_chars/count
}' "$RESULTS_DIR/ab-results.csv"
