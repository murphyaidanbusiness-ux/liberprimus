#!/bin/bash
cd ./agents/laneA_keyword_chain
run(){ ./kc2 $1 $2 keys.txt $3 30 2> log_$(basename $3 .tsv).txt; }
run 1 units_pages.txt res_f1_pages.tsv
run 2 units_pages.txt res_f2_pages.tsv
run 3 units_pages.txt res_f3_pages.tsv
run 1 units_sections.txt res_f1_sec.tsv
run 2 units_sections.txt res_f2_sec.tsv
run 3 units_sections.txt res_f3_sec.tsv
run 2 units_nullD.txt res_f2_null.tsv
run 3 units_nullR.txt res_f3_null.tsv
run 1 units_nullD.txt res_f1_null.tsv
run 2 units_nullDsec.txt res_f2_nullsec.tsv
run 3 units_nullRsec.txt res_f3_nullsec.tsv
run 1 units_nullDsec.txt res_f1_nullsec.tsv
echo ALLDONE > done.flag
