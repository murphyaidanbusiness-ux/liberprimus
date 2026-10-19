#!/usr/bin/env bash
# Publish findings + code from this (private lab) checkout to the public repo (remote "public") as ONE squashed commit
# on its main. The private working layer never goes public: CLAUDE.md, AGENTS.md, CHANGELOG.md, .claude/, docs/ and
# jobs/*/SKILL.md, jobs/*/PROOF.md. Aborts if a personal path or the owner's address appears in a published file.
#
#   scripts/sync_public.sh "Round three: findings and code"            # publish the current branch
#   scripts/sync_public.sh --dry-run "message"                         # build and show the commit, push nothing
set -euo pipefail
DRY=0
if [ "${1:-}" = "--dry-run" ]; then DRY=1; shift; fi
MSG="${1:?usage: scripts/sync_public.sh [--dry-run] \"commit message\"}"
SRC=$(git rev-parse HEAD)
W="$(mktemp -d)/lp-public"
git fetch -q public
git worktree add -q -B public-findings "$W" public/main
cleanup() { git worktree remove --force "$W" >/dev/null 2>&1 || true; }
trap cleanup EXIT
cd "$W"
git rm -r -q --cached . >/dev/null
git clean -fdq
git checkout -q "$SRC" -- .
git rm -r -q --cached --ignore-unmatch CLAUDE.md AGENTS.md CHANGELOG.md .claude docs
git ls-files | grep -E '^jobs/[^/]+/(SKILL|PROOF)\.md$' | xargs -r git rm -q --cached
rm -rf CLAUDE.md AGENTS.md CHANGELOG.md .claude docs jobs/*/SKILL.md jobs/*/PROOF.md
if git ls-files -z | xargs -0 grep -l -iE 'AIDANM~1|aidan murphy\|/c/Users/aidan|murphyaidanbusiness@' 2>/dev/null; then
  echo "ABORT: a personal path or address is in the files above"; exit 1
fi
if git diff --cached --quiet; then echo "nothing to publish"; exit 0; fi
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git show --stat --oneline HEAD | tail -3
if [ "$DRY" = 1 ]; then echo "dry run: not pushed"; exit 0; fi
git push -q public public-findings:main
echo "published to public main"
