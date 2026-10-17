#!/bin/bash
cd ./agents/laneK_walk_search
job(){ ./walk_sa $1 lm4.bin $2 $3 $4 $5 $6 $7 > runs/walk_$8.log; }
export -f job
cat walk_jobs.txt | xargs -P 4 -L 1 bash -c 'job "$@"' _
