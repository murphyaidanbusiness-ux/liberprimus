#!/usr/bin/env bash
# Lane O: recreate the working copy dl/aldegonde_port from the pristine community clone and
# apply agents/laneO_quagmire_dodge/port.patch. The clone itself is only read.
#
#   bash agents/laneO_quagmire_dodge/setup_port.sh            # creates dl/aldegonde_port
#   PORT_DIR=dl/aldegonde_check bash agents/.../setup_port.sh  # any other target, for testing
#
# Refuses to write into an existing target (delete it by hand first). Refuses if the clone
# no longer matches audit/clone_manifest.sha256 (recorded at the Step 0 audit).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

CLONE="dl/aldegonde_clone"
PORT="${PORT_DIR:-dl/aldegonde_port}"
LANE="agents/laneO_quagmire_dodge"
PATCH="$LANE/port.patch"
MANIFEST="$LANE/audit/clone_manifest.sha256"

[ -d "$CLONE" ] || { echo "missing $CLONE" >&2; exit 2; }
[ -f "$PATCH" ] || { echo "missing $PATCH" >&2; exit 2; }
if [ -e "$PORT" ]; then
  echo "$PORT already exists; remove it by hand, then re-run" >&2
  exit 2
fi
if ! (cd "$CLONE" && sha256sum --quiet -c "$REPO/$MANIFEST"); then
  echo "clone does not match $MANIFEST; refusing to build a port from it" >&2
  exit 3
fi

cp -r "$CLONE" "$PORT"
patch -p1 --binary --batch --forward -d "$PORT" -i "$REPO/$PATCH"  # --binary: sources are CRLF
echo "port ready at $PORT (patch: $PATCH)"
