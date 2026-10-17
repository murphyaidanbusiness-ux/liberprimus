#!/bin/bash
# M_K real + doublet-matched shuffle nulls, identical budget. jobs: tag K skip ptype iters restarts
cd ./agents/laneK_walk_search
job(){ tag=$1; K=$2; sk=$3; pt=$4; it=$5; rs=$6; sd=$7
  name=${tag}_${pt%%sec*}; f=inst/$name.txt
  python3 gen_inst.py $f $K $sk 0 $sd $pt > /dev/null
  ./mk_sa $f lm4.bin $K $sk 0 0 0 $it $rs $sd 5 runs/$name > runs/$name.log
}
export -f job
cat $1 | xargs -P 4 -L 1 bash -c 'job "$@"' _
