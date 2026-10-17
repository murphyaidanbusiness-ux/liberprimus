#!/bin/bash
cd "<repo>"
L=agents/laneS_totient_skip/logs
python agents/laneS_totient_skip/lane_s.py control > $L/control_stdout.txt 2>&1
python agents/laneS_totient_skip/lane_s.py null --sign +1 > $L/null_fwd_stdout.txt 2>&1
python agents/laneS_totient_skip/lane_s.py null --sign -1 > $L/null_rev_stdout.txt 2>&1
python agents/laneS_totient_skip/lane_s.py real > $L/real_stdout.txt 2>&1
python agents/laneS_totient_skip/lane_s.py report > $L/report_stdout.txt 2>&1
echo QUEUE_DONE >> $L/report_stdout.txt
