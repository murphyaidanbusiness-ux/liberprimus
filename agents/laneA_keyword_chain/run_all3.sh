#!/bin/bash
cd ./agents/laneA_keyword_chain
while kill -0 16050 2>/dev/null; do sleep 20; done
full(){ ./kc2 $1 $2 keys.txt $3 30 2> log_$(basename $3 .tsv).txt; }
prun(){ ./kc3 $1 $2 keys.txt $3 30 64 -7.0 2> log_$(basename $3 .tsv).txt; }
prun 1 units_sections.txt res_f1p_sec.tsv
prun 2 units_sections.txt res_f2p_sec.tsv
prun 3 units_sections.txt res_f3p_sec.tsv
prun 2 units_nullDsec.txt res_f2p_nullsec.tsv
prun 3 units_nullRsec.txt res_f3p_nullsec.tsv
prun 1 units_nullDsec.txt res_f1p_nullsec.tsv
full 1 units_pages.txt res_f1_pages.tsv
full 1 units_nullD_sub.txt res_f1_nullsub.tsv
echo ALLDONE > done.flag
