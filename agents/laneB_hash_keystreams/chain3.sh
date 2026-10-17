#!/bin/bash
cd ./agents/laneB_hash_keystreams
while [ ! -f chain2_done.txt ]; do sleep 10; done
LANEB_ROOTS=8,10,11,14,15,18,19,21,26,27 python3 run_real.py G_core > log_G_core.txt 2>&1
python3 run_real.py G_null 0.05 20 40 > log_G_null2.txt 2>&1
python3 run_real.py P_null 0.05 20 40 > log_P_null2.txt 2>&1
echo done > chain3_done.txt
