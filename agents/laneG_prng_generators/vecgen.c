/* usage: vecgen IDIOM MODEL N  ival  [limb...]   (limbs used for F_MTPY; if none given, limbs of ival) */
#include <stdio.h>
#include <stdlib.h>
#include "prng.h"
int main(int argc, char **argv) {
    int idi = atoi(argv[1]), mod = atoi(argv[2]), n = atoi(argv[3]);
    long long iv = strtoll(argv[4], 0, 10);
    uint32_t key[4096]; int kl = 0;
    for (int i = 5; i < argc; i++) key[kl++] = (uint32_t)strtoul(argv[i], 0, 10);
    if (!kl) { unsigned long long a = iv < 0 ? -iv : iv; if (!a) key[kl++] = 0; while (a) { key[kl++] = (uint32_t)a; a >>= 32; } }
    RNG r; rng_seed(&r, IDI_FAM[idi], key, kl, (uint64_t)iv);
    uint8_t out[100000];
    if (mod < 0) { /* raw draws draw(r, idi, -mod) */
        for (int i = 0; i < n; i++) printf("%d ", draw(&r, idi, -mod));
    } else { emit(&r, idi, mod, out, n); for (int i = 0; i < n; i++) printf("%d ", out[i]); }
    printf("\n"); return 0;
}
