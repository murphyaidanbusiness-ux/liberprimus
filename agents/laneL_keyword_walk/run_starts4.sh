#!/bin/bash
cd ./agents/laneL_keyword_walk
until [ -f runs/starts.done ]; do sleep 20; done
./kwwalk texts/real_page08.txt 150 runs/start4_real_page08 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page08.log 2>&1
./kwwalk texts/real_page11.txt 150 runs/start4_real_page11 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page11.log 2>&1
./kwwalk texts/real_page15.txt 150 runs/start4_real_page15 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page15.log 2>&1
./kwwalk texts/real_page30.txt 150 runs/start4_real_page30 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page30.log 2>&1
./kwwalk texts/real_page35.txt 150 runs/start4_real_page35 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page35.log 2>&1
./kwwalk texts/real_page37.txt 150 runs/start4_real_page37 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page37.log 2>&1
./kwwalk texts/real_page48.txt 150 runs/start4_real_page48 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_page48.log 2>&1
./kwwalk texts/real_sec03.txt 150 runs/start4_real_sec03 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_sec03.log 2>&1
./kwwalk texts/real_sec06.txt 150 runs/start4_real_sec06 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_sec06.log 2>&1
./kwwalk texts/real_sec07.txt 150 runs/start4_real_sec07 -m 7 -b lists/aCicR1.txt -s lists/aCicR1.txt -g lists/goost.txt > runs/start4_real_sec07.log 2>&1
echo DONE > runs/starts4.done
