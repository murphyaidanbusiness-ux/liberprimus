cd ./agents/laneG_prng_generators
for k in 0 1 2 3; do ./search_new ctrl/corpus_ctrl.bin 21 pagestarts.txt ctrl/seeds_ctrl.txt $k 4 ctrl/res_ctrl_$k.txt 2> ctrl/log_ctrl_$k.txt & done; wait; echo done > ctrl/done
