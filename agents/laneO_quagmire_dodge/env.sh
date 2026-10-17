# Lane O run environment. Source from the repo root:  source agents/laneO_quagmire_dodge/env.sh
# PYTHONUTF8: aldegonde's n-gram loader calls open() without an encoding (cp1252 on Windows).
# PYTHONPATH: the aldegonde package lives in dl/aldegonde_port/src and is not installed.
# DODGE_KERNEL_DLL: MSVC build from build_kernel.bat (replaces the `cc` build of dodge_score_kernel).
# DODGE_PROSE: the sweep's register text (Moby-Dick, not Gutenberg 1342; see RESULTS.md).
export PYTHONUTF8=1
export PYTHONPATH="dl/aldegonde_port/src"
export DODGE_KERNEL_DLL="$(cygpath -w "$PWD/agents/laneO_quagmire_dodge/build/dodge_score_kernel_m29.dll")"
export DODGE_PROSE="$(cygpath -w "$PWD/dl/dukotah/liber-primus/data/keys/armada18/melville_moby_dick.txt")"
