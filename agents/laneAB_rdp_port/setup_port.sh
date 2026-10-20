#!/usr/bin/env bash
# Lane AB: recreate the working copy dl/rdp_port from the pristine RuneDecrypterPrime v1.0.0 clone (dl/rdp) and apply
# agents/laneAB_rdp_port/port.patch. The clone itself is only read. Also creates the isolated Python environment
# dl/rdp_venv (system site-packages visible, so the machine's numpy is reused) with RDP's missing dependencies.
#
#   bash agents/laneAB_rdp_port/setup_port.sh             # creates dl/rdp_port (and dl/rdp_venv if missing)
#   PORT_DIR=dl/rdp_check bash agents/laneAB_rdp_port/setup_port.sh   # any other target, for the rebuild check
#
# Then build the three native modules with MSVC:  cmd //c agents\\laneAB_rdp_port\\build_native.bat [port dir]
# Refuses to write into an existing target. Refuses if the clone no longer matches audit/clone_manifest.sha256.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

CLONE="dl/rdp"
PORT="${PORT_DIR:-dl/rdp_port}"
LANE="agents/laneAB_rdp_port"
PATCH="$LANE/port.patch"
MANIFEST="$LANE/audit/clone_manifest.sha256"
VENV="dl/rdp_venv"

[ -d "$CLONE" ] || { echo "missing $CLONE (run scripts/fetch_sources.sh)" >&2; exit 2; }
[ -f "$PATCH" ] || { echo "missing $PATCH" >&2; exit 2; }
if [ -e "$PORT" ]; then
  echo "$PORT already exists; remove it by hand, then re-run" >&2
  exit 2
fi
if [ "$(git -C "$CLONE" rev-parse HEAD)" != "61bf2c7865892944a3a4ae3d72b6c8e9745c86f0" ]; then
  echo "$CLONE is not at RDP v1.0.0 (61bf2c78)" >&2
  exit 3
fi
if ! (cd "$CLONE" && sha256sum --quiet -c "$REPO/$MANIFEST"); then
  echo "clone does not match $MANIFEST; refusing to build a port from it" >&2
  exit 3
fi

cp -r "$CLONE" "$PORT"
if [ -s "$PATCH" ]; then
  patch -p1 --binary --batch --forward -d "$PORT" -i "$REPO/$PATCH"
fi
echo "port ready at $PORT (patch: $PATCH)"

if [ ! -x "$VENV/Scripts/python.exe" ]; then
  python -m venv --system-site-packages "$VENV"
  "$VENV/Scripts/python.exe" -m pip install --disable-pip-version-check -q -r "$LANE/requirements_port.txt"
  echo "venv ready at $VENV"
fi
