#!/bin/bash
cd ./agents/laneL_keyword_walk
[ -s runs/start_real_page16.txt ] && grep -q "mode 2" runs/start_real_page16.txt || ./kwwalk texts/real_page16.txt 150 runs/start_real_page16 -m 7  > runs/start_real_page16.log 2>&1
[ -s runs/start_real_page31.txt ] && grep -q "mode 2" runs/start_real_page31.txt || ./kwwalk texts/real_page31.txt 150 runs/start_real_page31 -m 7  > runs/start_real_page31.log 2>&1
[ -s runs/start_real_page46.txt ] && grep -q "mode 2" runs/start_real_page46.txt || ./kwwalk texts/real_page46.txt 150 runs/start_real_page46 -m 7  > runs/start_real_page46.log 2>&1
[ -s runs/start_real_page06.txt ] && grep -q "mode 2" runs/start_real_page06.txt || ./kwwalk texts/real_page06.txt 150 runs/start_real_page06 -m 7 -b lists/aR1.txt -s lists/aR1.txt > runs/start_real_page06.log 2>&1
[ -s runs/start_real_page13.txt ] && grep -q "mode 2" runs/start_real_page13.txt || ./kwwalk texts/real_page13.txt 150 runs/start_real_page13 -m 7 -b lists/aR1.txt -s lists/aR1.txt > runs/start_real_page13.log 2>&1
[ -s runs/start_real_page18.txt ] && grep -q "mode 2" runs/start_real_page18.txt || ./kwwalk texts/real_page18.txt 150 runs/start_real_page18 -m 7 -b lists/aR1.txt -s lists/aR1.txt > runs/start_real_page18.log 2>&1
[ -s runs/start_real_page38.txt ] && grep -q "mode 2" runs/start_real_page38.txt || ./kwwalk texts/real_page38.txt 150 runs/start_real_page38 -m 7 -b lists/aR1.txt -s lists/aR1.txt > runs/start_real_page38.log 2>&1
[ -s runs/start_real_sec12.txt ] && grep -q "mode 2" runs/start_real_sec12.txt || ./kwwalk texts/real_sec12.txt 150 runs/start_real_sec12 -m 7 -b lists/aR1.txt -s lists/aR1.txt > runs/start_real_sec12.log 2>&1
[ -s runs/start_real_page01.txt ] && grep -q "mode 2" runs/start_real_page01.txt || ./kwwalk texts/real_page01.txt 150 runs/start_real_page01 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page01.log 2>&1
[ -s runs/start_real_page09.txt ] && grep -q "mode 2" runs/start_real_page09.txt || ./kwwalk texts/real_page09.txt 150 runs/start_real_page09 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page09.log 2>&1
[ -s runs/start_real_page19.txt ] && grep -q "mode 2" runs/start_real_page19.txt || ./kwwalk texts/real_page19.txt 150 runs/start_real_page19 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page19.log 2>&1
[ -s runs/start_real_page52.txt ] && grep -q "mode 2" runs/start_real_page52.txt || ./kwwalk texts/real_page52.txt 150 runs/start_real_page52 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page52.log 2>&1
[ -s runs/start_real_page08.txt ] && grep -q "mode 2" runs/start_real_page08.txt || ./kwwalk texts/real_page08.txt 150 runs/start_real_page08 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page08.log 2>&1
[ -s runs/start_real_page11.txt ] && grep -q "mode 2" runs/start_real_page11.txt || ./kwwalk texts/real_page11.txt 150 runs/start_real_page11 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page11.log 2>&1
[ -s runs/start_real_page15.txt ] && grep -q "mode 2" runs/start_real_page15.txt || ./kwwalk texts/real_page15.txt 150 runs/start_real_page15 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page15.log 2>&1
[ -s runs/start_real_page30.txt ] && grep -q "mode 2" runs/start_real_page30.txt || ./kwwalk texts/real_page30.txt 150 runs/start_real_page30 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page30.log 2>&1
[ -s runs/start_real_page35.txt ] && grep -q "mode 2" runs/start_real_page35.txt || ./kwwalk texts/real_page35.txt 150 runs/start_real_page35 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page35.log 2>&1
[ -s runs/start_real_page37.txt ] && grep -q "mode 2" runs/start_real_page37.txt || ./kwwalk texts/real_page37.txt 150 runs/start_real_page37 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page37.log 2>&1
[ -s runs/start_real_page48.txt ] && grep -q "mode 2" runs/start_real_page48.txt || ./kwwalk texts/real_page48.txt 150 runs/start_real_page48 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_page48.log 2>&1
[ -s runs/start_real_sec03.txt ] && grep -q "mode 2" runs/start_real_sec03.txt || ./kwwalk texts/real_sec03.txt 150 runs/start_real_sec03 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_sec03.log 2>&1
[ -s runs/start_real_sec06.txt ] && grep -q "mode 2" runs/start_real_sec06.txt || ./kwwalk texts/real_sec06.txt 150 runs/start_real_sec06 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_sec06.log 2>&1
[ -s runs/start_real_sec07.txt ] && grep -q "mode 2" runs/start_real_sec07.txt || ./kwwalk texts/real_sec07.txt 150 runs/start_real_sec07 -m 7 -b lists/aR1.txt -s lists/aR1.txt -g lists/goost.txt > runs/start_real_sec07.log 2>&1
echo DONE > runs/starts.done
