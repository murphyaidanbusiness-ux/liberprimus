cd ./agents/laneM_title_cribs
cat runlist.txt | xargs -P4 -I{} sh -c './frag lm.bin htab.bin jobs/{}.txt runs/{} && echo done {}' > runs/run_all.log 2>&1
echo ALLDONE >> runs/run_all.log
