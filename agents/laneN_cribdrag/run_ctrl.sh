#!/bin/bash
cd ./agents/laneN_cribdrag
export DRAGDIR=$PWD
for v in chain_A chain_B vig_A vig_B; do
  ./drag ctrl/$v.bin cribs.txt ctrl/out_$v.txt 0 3.0 9 5 ctrl/dump_$v.txt > ctrl/log_$v.txt 2>&1
done
echo done > ctrl/done.flag
