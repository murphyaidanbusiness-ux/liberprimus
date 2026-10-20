#!/usr/bin/env bash
# Clones the community repositories the analysis depends on into ./dl/ (git-ignored).
# Every script in this repo expects to be run from the repository root.
set -euo pipefail
mkdir -p dl && cd dl
[ -d dukotah ]       || git clone --depth 1 https://github.com/Dukotah/cicada3301 dukotah
[ -d leo ]           || git clone --depth 1 https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis leo
[ -d theron ]        || git clone --depth 1 https://github.com/TheronEagle/liber-primus-research theron
[ -d aldegonde_clone ] || git clone --depth 1 https://github.com/micheloosterhof/aldegonde aldegonde_clone
# RuneDecrypterPrime pinned to its first release (2026-09-14, tag v1.0.0 = 61bf2c78); lane AB
[ -d rdp ]           || git -c advice.detachedHead=false clone --depth 1 --branch v1.0.0 https://github.com/mortlach/RuneDecrypterPrime rdp
echo "sources ready under ./dl"
