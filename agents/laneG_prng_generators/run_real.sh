cd ./agents/laneG_prng_generators
mv search_new search
for k in 0 1 2 3; do ./search corpus.bin 21 pagestarts.txt seeds_all.txt $k 4 res/direct_$k.txt 2> res/log_direct_$k.txt & done; wait
echo direct_done > res/direct.done
# model f: real (all seeds), per-page seeds (I lines), nulls (20 D-shuffles x 1/5 of seed lines)
for k in 0 1 2 3; do ./keystream corpus.bin 21 0 pagestarts.txt seeds_all.txt $k 4 res/f_real_$k.txt 0 1 0 & done; wait
for k in 0 1 2 3; do ./keystream corpus.bin 21 0 pagestarts.txt seeds_all.txt $k 4 res/fpp_real_$k.txt 1 1 0 & done; wait
for c in $(seq 1 20); do
  for k in 0 1 2 3; do ./keystream corpus.bin 21 $c pagestarts.txt seeds_all.txt $k 4 res/f_null_${c}_$k.txt 0 5 $((c%5)) & done; wait
  for k in 0 1 2 3; do ./keystream corpus.bin 21 $c pagestarts.txt seeds_all.txt $k 4 res/fpp_null_${c}_$k.txt 1 20 $((c%20)) & done; wait
done
echo all_done > res/all.done
