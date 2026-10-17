#!/bin/bash
# main batch: controls, real page 0, 20 nulls (full keyword corner, modes global/reset/fixed)
cd ./agents/laneL_keyword_walk
for t in plant1 plant2 real_page00 $(for s in $(seq -w 0 19); do echo null_p0_s$s; done); do
  if [ ! -s runs/full_$t.txt ] || ! grep -q "mode 2" runs/full_$t.txt; then
    ./kwwalk texts/$t.txt 150 runs/full_$t -m 7 > runs/full_$t.log 2>&1
  fi
done
echo DONE > runs/main.done
