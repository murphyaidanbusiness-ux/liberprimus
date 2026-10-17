### model f: one key stream per seed (continuous and per-page restart)
real: 143022 seed lines, 38569920 (seed x idiom x decode) trials; null: 154279680 trials on 20 D-shuffled corpora
null per-trial IoC mean 1.02301 sd 0.00058; real overall max 1.02769 (PYGM, M/ Y,R, seed py27h64:later) z=8.02; null overall max 1.02818 z=8.86
  fraction of trials with IoC >= 1.030: real 0, null 0
  fraction of trials with IoC >= 1.032: real 0, null 0
  fraction of trials with IoC >= 1.034: real 0, null 0
  fraction of trials with IoC >= 1.036: real 0, null 0
  fraction of trials with IoC >= 1.040: real 0, null 0
  fraction of trials with IoC >= 1.050: real 0, null 0

| idiom | best decode | real max IoC | seed | null max (same idiom, all decodes) |
|---|---|---|---|---|
| PY2 | M* X,R | 1.02734 | int:28034[int] | 1.02811 |
| PY3 | M/ X,C | 1.02720 | int:14815[int] | 1.02753 |
| PYGM | M/ Y,R | 1.02769 | py27h64:later | 1.02771 |
| MTMOD | A+ X,R | 1.02763 | int:26148[int] | 1.02774 |
| NPR53 | M/ Y,R | 1.02715 | int:10706[int] | 1.02816 |
| NPINT | M* X,R | 1.02700 | int:2012304[date_YYYYDDD_2012-10-30] | 1.02745 |
| STDUID | M/ Y,C | 1.02704 | int:2357[int] | 1.02786 |
| PHP7R | A+ X,R | 1.02763 | int:26148[int] | 1.02774 |
| PHP7M | A- Y,C | 1.02718 | int:29241[int] | 1.02760 |
| PHP5R | A- Y,R | 1.02726 | int:42627[int] | 1.02749 |
| PHP5M | A- X,C | 1.02703 | crc32:Their | 1.02745 |
| GLMOD | A- Y,C | 1.02691 | int:24405[int] | 1.02768 |
| GLSC | M* X,C | 1.02752 | int:1178457[3301*357] | 1.02786 |
| GLDIV | M* X,C | 1.02752 | int:1178457[3301*357] | 1.02786 |
| MSMOD | A+ Y,C | 1.02726 | int:1354363200[unix_2012-12-01_12:00Z] | 1.02723 |
| MSSC | A+ X,R | 1.02737 | int:36392[int] | 1.02746 |
| JINT | A+ Y,R | 1.02692 | int:29516[int] | 1.02818 |
| JDBL | M* X,R | 1.02696 | int:2013084[date_YYYYDDD_2013-03-25] | 1.02731 |
| D48 | A- Y,C | 1.02755 | int:1363564800[unix_2013-03-18_00:00Z] | 1.02786 |

### model f, fresh seed per page (seed = s + page index)
real: 114674 seed lines, 17430448 (seed x idiom x decode) trials; null: 17430448 trials on 20 D-shuffled corpora
null per-trial IoC mean 1.02302 sd 0.00058; real overall max 1.02758 (PHP7R, A- Y,R, seed int:90710[int]) z=7.82; null overall max 1.02803 z=8.60
  fraction of trials with IoC >= 1.030: real 0, null 0
  fraction of trials with IoC >= 1.032: real 0, null 0
  fraction of trials with IoC >= 1.034: real 0, null 0
  fraction of trials with IoC >= 1.036: real 0, null 0
  fraction of trials with IoC >= 1.040: real 0, null 0
  fraction of trials with IoC >= 1.050: real 0, null 0

| idiom | best decode | real max IoC | seed | null max (same idiom, all decodes) |
|---|---|---|---|---|
| PY2 | A+ Y,R | 1.02704 | int:140219[date_YYMMDD_2014-02-19] | 1.02698 |
| PY3 | M* X,R | 1.02693 | int:20042015[date_DDMMYYYY_2015-04-20] | 1.02686 |
| PYGM | A- X,R | 1.02686 | int:67240[int] | 1.02699 |
| MTMOD | A- Y,R | 1.02758 | int:90710[int] | 1.02696 |
| NPR53 | A- Y,R | 1.02696 | int:41569[int] | 1.02703 |
| NPINT | A+ Y,R | 1.02716 | int:41962[int] | 1.02710 |
| STDUID | A+ X,R | 1.02713 | int:67045[int] | 1.02731 |
| PHP7R | A- Y,R | 1.02758 | int:90710[int] | 1.02696 |
| PHP7M | M/ Y,R | 1.02700 | int:7212011[date_MMDDYYYY_2011-07-21] | 1.02734 |
| PHP5R | M* X,R | 1.02690 | int:48794[int] | 1.02683 |
| PHP5M | M/ X,R | 1.02678 | int:1407[int] | 1.02706 |
| GLMOD | A- X,R | 1.02713 | int:20150109[date_YYYYMMDD_2015-01-09] | 1.02685 |
| GLSC | M* Y,R | 1.02667 | int:31180[int] | 1.02803 |
| GLDIV | M* Y,R | 1.02667 | int:31180[int] | 1.02803 |
| MSMOD | A+ Y,R | 1.02744 | int:13855[int] | 1.02685 |
| MSSC | M/ X,R | 1.02717 | int:35144[int] | 1.02729 |
| JINT | M/ X,R | 1.02730 | int:96465[int] | 1.02693 |
| JDBL | A- Y,R | 1.02735 | int:34997[int] | 1.02696 |
| D48 | M/ X,R | 1.02694 | int:414[int] | 1.02689 |

