#!/bin/bash
cd ./agents/laneL_keyword_walk
for n in real_page06 real_page13 real_page18 real_page38 real_sec12; do
  ./kwwalk texts/$n.txt 150 runs/start_$n -m 5 -dyn 4.0 -b lists/aR1.txt -s lists/aR1.txt -g lists/ggem.txt > runs/start_$n.log 2>&1
done
for n in real_page01 real_page09 real_page19 real_page52; do
  ./kwwalk texts/$n.txt 150 runs/start_$n -m 5 -dyn 4.0 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_$n.log 2>&1
done
echo DONE > runs/starts.done
