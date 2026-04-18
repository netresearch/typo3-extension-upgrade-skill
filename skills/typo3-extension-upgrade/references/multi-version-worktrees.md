# Multi-Version Worktrees and Backports

Concrete patterns for upgrading an extension across multiple TYPO3 LTS versions in parallel, and for backporting fixes from `main` to maintenance branches.

## The Rule: One Worktree Per LTS

Never switch branches in place when working on cross-version extension changes. Each TYPO3 LTS target gets its own worktree so:

- `composer.lock` doesn't get rewritten every time you switch
- DDEV/Docker containers keep their state
- Build artifacts don't get clobbered across versions
- You can run tests on v11 and v13 simultaneously in two terminals

### Layout

```
~/projects/<ext-name>/
├── .bare/              # bare git clone — source of truth
├── main/               # default branch (usually latest-supported)
├── TYPO3_11/           # v11 maintenance branch worktree
├── TYPO3_12/           # v12 maintenance branch worktree
├── TYPO3_13/           # v13 maintenance branch worktree
└── feature-XYZ/        # topical work, from whichever base applies
```

### Setup

```bash
cd ~/projects
mkdir <ext-name> && cd <ext-name>
git clone --bare <repo-url> .bare
cd .bare
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
cd ..

# One worktree per version you support
git -C .bare worktree add ../main main
git -C .bare worktree add ../TYPO3_12 TYPO3_12
git -C .bare worktree add ../TYPO3_13 TYPO3_13
```

### Absolute Paths Only

Creating a worktree with a relative path can silently produce the worktree INSIDE `.bare/` if the cwd is wrong. Always use an absolute path:

```bash
# WRONG — relative path, depends on cwd
git -C .bare worktree add ../feature-fix feature-fix

# RIGHT — absolute path
git -C /home/user/projects/ext-name/.bare worktree add /home/user/projects/ext-name/feature-fix feature-fix
```

If you find a worktree inside `.bare/`, remove it (`git worktree remove ...`) and recreate at the correct path. Never run `rm -rf` on a path under `.bare/` — you'll destroy the bare clone.

## Cache Safety

Never edit the installed extension under `vendor/<vendor>/<ext-name>/` or `typo3conf/ext/<ext-name>/`. Those are deployed copies. Edit only in the source worktree. Composer sync / deploy will overwrite the installed copy on the next build.

Pre-edit check:

```bash
pwd_real=$(realpath .)
case "$pwd_real" in
  */vendor/*|*/typo3conf/ext/*|*/\.bare/*)
    echo "REFUSING to edit installed/cache path: $pwd_real"
    exit 1
    ;;
esac
```

## Backport Workflow (TYPO3_12 from main)

### When to backport vs port

- **Backport**: the fix is a pure bug fix that applies to both versions with minor API differences.
- **Port** (rewrite): the fix uses APIs that don't exist in the older version; write the v12 version from scratch rather than force a cherry-pick.

### Step-by-step cherry-pick

```bash
# 1. Identify the fix commit on main
cd ~/projects/<ext-name>/main
git log --oneline --grep='fix: <bug>' -n 5

# 2. Switch to the maintenance worktree (never branch-switch in place)
cd ~/projects/<ext-name>/TYPO3_12

# 3. Cherry-pick
git cherry-pick <sha>

# 4. Resolve API differences — expect conflicts if the fix used v13-only APIs
# 5. Run tests in the v12 worktree ONLY (not the main worktree)
Build/Scripts/runTests.sh -s unit -p 8.1
Build/Scripts/runTests.sh -s functional -p 8.1

# 6. Commit with a trailer identifying the origin
git commit --amend -s -S -m "fix: <bug>

Backport of <sha> from main.

Signed-off-by: ..."

# 7. Push backport branch
git push -u origin backport/TYPO3_12-<bug>
```

### Backport PR conventions

- Target branch: the maintenance branch (`TYPO3_12`), not `main`.
- PR title prefix: `[TYPO3_12]` so reviewers see the target at a glance.
- Label: `backport`.
- Release notes: the backport is its own minor or patch release on the maintenance line; not tied to the main-line release number.

### Verifying the cherry-pick target

Before pushing:

```bash
pwd                                               # must match the target worktree
git branch --show-current                         # must be backport/TYPO3_12-... branch
cat composer.json | jq '.require."typo3/cms-core"' # must show the target version constraint
Build/Scripts/runTests.sh -s unit -p 8.1          # must pass in this worktree
```

If any of these show the main-branch values, you're about to push a backport to the wrong branch. Stop.

## Cross-Version CI Patterns

Extension CI should exercise every supported LTS on every PR, not just the one the PR is based on. Matrix example:

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        typo3: ["^12.4", "^13.4", "^14.0"]
        php: ["8.1", "8.2", "8.3", "8.4"]
        exclude:
          - { typo3: "^12.4", php: "8.4" }  # document WHY this is excluded
          - { typo3: "^14.0", php: "8.1" }
```

A passing test run on v13 does NOT certify v11 or v12. If a PR touches code that runs on multiple LTSes, the matrix must be green on every included cell before declaring "tested".

## Declaring Version Coverage in PR Description

Mandatory PR description section:

```markdown
## Version coverage

- [x] v14 — unit + functional green (link to CI run)
- [x] v13 — unit + functional green (link to CI run)
- [ ] v12 — not tested in this PR; follow-up in #<number>
```

If a version is "not tested", say so explicitly and link a follow-up issue. Silent coverage gaps are the pattern that causes "worked on v13, broke on v11" regressions.
