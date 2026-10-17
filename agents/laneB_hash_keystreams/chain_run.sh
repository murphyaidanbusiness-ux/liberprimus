#!/bin/bash
cd ./agents/laneB_hash_keystreams
python3 run_real.py G_real 0 > log_G_real_k0.txt 2>&1
for c in G2 G3 G4 P1; do python3 control.py $c > control_$c.log 2>&1; done
python3 run_real.py P_real 0 > log_P_real_k0.txt 2>&1
python3 run_real.py PB_real > log_PB_real.txt 2>&1
python3 run_real.py G_null 0.05 0 20 > log_G_null.txt 2>&1
python3 run_real.py P_null 0.05 0 20 > log_P_null.txt 2>&1
echo ALLDONE > chain_done.txt
