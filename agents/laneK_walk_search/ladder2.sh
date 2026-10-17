#!/bin/bash
# jobs: name K skip tied knownA knownPh iters restarts T0 ptype seed [knowng]
cd ./agents/laneK_walk_search
job(){ name=$1; K=$2; sk=$3; ti=$4; ka=$5; kp=$6; it=$7; rs=$8; T=$9; pt=${10}; sd=${11}; kg=${12:-0}
  f=inst/${name}_${sd}.txt
  python3 gen_inst.py $f $K $sk $ti $sd $pt > /dev/null
  ./mk_sa $f lm4.bin $K $sk $ti $ka $kp $it $rs $sd $T runs/${name}_${sd} $kg > runs/${name}_${sd}.log
}
export -f job
cat ladder_jobs2.txt | xargs -P 4 -L 1 bash -c 'job "$@"' _
