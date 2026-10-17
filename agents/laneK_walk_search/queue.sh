#!/bin/bash
cd ./agents/laneK_walk_search
while pgrep -f ladder.sh >/dev/null; do sleep 10; done
./ladder2.sh; echo ladder2 done $(date)
./walk_run.sh; echo walk done $(date)
./real_run.sh real_jobs.txt; echo real done $(date)
