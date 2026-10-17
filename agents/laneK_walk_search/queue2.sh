#!/bin/bash
cd ./agents/laneK_walk_search
until grep -q 'real done' queue_nohup.txt; do sleep 20; done
./ladder3.sh; echo ladder3 done $(date) >> queue_nohup.txt
