#!/usr/bin/env bash
# Publish findings + code from this (private lab) checkout to the public repo (remote "public") as ONE squashed commit
# on its main. The private working layer never goes public: CLAUDE.md, AGENTS.md, CHANGELOG.md, .claude/, docs/ and
# jobs/*/SKILL.md, jobs/*/PROOF.md, plus the Discord scan files in PRIV_EXTRA below. Aborts if a personal path or the
# owner's address appears in a published file.
#
#   scripts/sync_public.sh "Round three: findings and code"            # publish the current branch
#   scripts/sync_public.sh --dry-run "message"                         # build and show the commit, push nothing
set -euo pipefail
DRY=0
if [ "${1:-}" = "--dry-run" ]; then DRY=1; shift; fi
MSG="${1:?usage: scripts/sync_public.sh [--dry-run] \"commit message\"}"
SRC=$(git rev-parse HEAD)
ROOT=$(git rev-parse --show-toplevel)
W="$(mktemp -d)/lp-public"
git fetch -q public
git worktree add -q -B public-findings "$W" public/main
cleanup() { git worktree remove --force "$W" >/dev/null 2>&1 || true; }
trap cleanup EXIT
cd "$W"
git rm -r -q --cached . >/dev/null
git clean -fdq
git checkout -q "$SRC" -- .
# Also private: the 2026-10-19 Discord scan (scout7), which was read through the owner's own Discord client.
PRIV_EXTRA="research/scout7_discord.md jobs/community-scout/runs/2026-10-19-discord"
git rm -r -q --cached --ignore-unmatch CLAUDE.md AGENTS.md CHANGELOG.md .claude docs $PRIV_EXTRA
git ls-files | grep -E '^jobs/[^/]+/(SKILL|PROOF)\.md$' | xargs -r git rm -q --cached
rm -rf CLAUDE.md AGENTS.md CHANGELOG.md .claude docs jobs/*/SKILL.md jobs/*/PROOF.md $PRIV_EXTRA
# Redactions (community handles kept out of public) from the private list docs/PUBLIC_REDACTIONS.tsv; aborts if any
# pattern survives.
if [ -f "$ROOT/docs/PUBLIC_REDACTIONS.tsv" ]; then
  python "$ROOT/scripts/redact_public.py" "$ROOT/docs/PUBLIC_REDACTIONS.tsv"
  git add -u
fi
# Privacy check. The personal strings are read from the environment at run time, so none is written in this file:
# the profile folder name (and its 8.3 short form from TEMP) after "Users/" or "Users\", the git user's address and
# its local part, and any e-mail address outside a short allowlist.
prof="${USERPROFILE:-$HOME}"
name="${prof##*[\\/]}"
short=$(printf '%s' "${TEMP:-}" | sed -n 's#.*Users[\\/]\([^\\/]*\).*#\1#p')
esc() { printf '%s' "$1" | sed 's/[][\.*^$+?(){}|]/\\&/g'; }
pat="Users[\\/]+($(esc "$name")${short:+|$(esc "$short")})"
me=$(git config user.email || true)
bad=$(git ls-files -z | xargs -0 grep -l -iE "$pat" 2>/dev/null || true)
if [ -n "$me" ]; then
  bad="$bad
$(git ls-files -z | xargs -0 grep -l -iF "${me%@*}@" 2>/dev/null || true)"
fi
bad="$bad
$(git ls-files -z | xargs -0 grep -o -H -I -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' 2>/dev/null \
  | grep -v -i -E ':(you@example\.org|noreply@anthropic\.com)$' | cut -d: -f1 || true)"
bad=$(printf '%s\n' "$bad" | sed '/^$/d' | sort -u)
if [ -n "$bad" ]; then
  printf '%s\n' "$bad"
  echo "ABORT: a personal path or address is in the files above"; exit 1
fi
if git diff --cached --quiet; then echo "nothing to publish"; exit 0; fi
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git show --stat --oneline HEAD | tail -3
if [ "$DRY" = 1 ]; then echo "dry run: not pushed"; exit 0; fi
git push -q public public-findings:main
echo "published to public main"
