#!/bin/bash
cd ./agents/laneA_keyword_chain
full(){ ./kc2 $1 $2 keys.txt $3 30 2> log_$(basename $3 .tsv).txt; }
prun(){ ./kc3 $1 $2 keys.txt $3 30 64 -7.0 2> log_$(basename $3 .tsv).txt; }
full 2 units_pages.txt res_f2_pages.tsv
full 3 units_pages.txt res_f3_pages.tsv
full 2 units_nullD.txt res_f2_null.tsv
full 3 units_nullR.txt res_f3_null.tsv
prun 1 units_pages.txt res_f1p_pages.tsv
prun 1 units_nullD.txt res_f1p_null.tsv
full 1 units_pages.txt res_f1_pages.tsv
full 2 units_sections.txt res_f2_sec.tsv
full 3 units_sections.txt res_f3_sec.tsv
prun 1 units_sections.txt res_f1p_sec.tsv
full 2 units_nullDsec.txt res_f2_nullsec.tsv
full 3 units_nullRsec.txt res_f3_nullsec.tsv
prun 1 units_nullDsec.txt res_f1p_nullsec.tsv
full 1 units_nullD_sub.txt res_f1_nullsub.tsv
echo ALLDONE > done.flag
