#!/bin/bash
# resumable batch: F0: real + 50 nulls ; F1: real + 20 nulls
cd ./agents/laneN_cribdrag
export DRAGDIR=$PWD
mkdir -p out
run() { # F name stream
  f=out/F$1_$2.txt
  if [ ! -s $f ]; then ./drag $3 cribs.txt $f.tmp $1 99 99 99 > out/F$1_$2.log 2>&1 && mv $f.tmp $f; fi
}
run 0 real streams/real.bin
for i in $(seq -w 1 50); do run 0 null$i streams/null$i.bin; done
run 1 real streams/real.bin
for i in $(seq -w 1 20); do run 1 null$i streams/null$i.bin; done
echo finished > out/ALL_DONE
