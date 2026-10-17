/* laneG: bit-exact reimplementations of era PRNGs + "draw(n)" idioms + emission models.
 * Families:
 *   F_MTPY   MT19937 seeded by CPython random.seed(): init_by_array(32-bit limbs of abs(int) / of hash(str) / of sha512-int)
 *   F_MTG    MT19937 seeded by init_genrand(uint32)  (C/C++ std::mt19937, numpy RandomState(int), PHP>=7.1 mt_srand)
 *   F_PHP5   PHP<7.1 mt_srand/mt_rand: init_genrand + the buggy twist (loBit(u) instead of loBit(v))
 *   F_GLIBC  glibc srand/srandom + rand()/random() (TYPE_3 additive feedback, 310 discards)
 *   F_MSVC   MSVC srand/rand (LCG 214013, 2531011, >>16 & 0x7fff)
 *   F_JAVA   java.util.Random(long seed)
 *   F_D48    glibc srand48/drand48 (Perl 5.14 rand())
 */
#pragma once
#include <stdint.h>
#include <string.h>

#define MTN 624
#define MTM 397
enum { F_MTPY=0, F_MTG, F_PHP5, F_GLIBC, F_MSVC, F_JAVA, F_D48, NFAM };

typedef struct {
    int fam;
    uint32_t mt[MTN]; int idx; int buggy;
    int32_t gr[31]; int gf, gb;
    uint32_t ms;
    uint64_t js;
    uint64_t x48;
} RNG;

static void mt_init_genrand(RNG *r, uint32_t s) {
    r->mt[0] = s;
    for (int i = 1; i < MTN; i++)
        r->mt[i] = 1812433253u * (r->mt[i-1] ^ (r->mt[i-1] >> 30)) + (uint32_t)i;
    r->idx = MTN;
}
static void mt_init_by_array(RNG *r, const uint32_t *key, int klen) {
    mt_init_genrand(r, 19650218u);
    uint32_t *mt = r->mt;
    int i = 1, j = 0, k = (MTN > klen ? MTN : klen);
    for (; k; k--) {
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525u)) + key[j] + (uint32_t)j;
        i++; j++;
        if (i >= MTN) { mt[0] = mt[MTN-1]; i = 1; }
        if (j >= klen) j = 0;
    }
    for (k = MTN - 1; k; k--) {
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941u)) - (uint32_t)i;
        i++;
        if (i >= MTN) { mt[0] = mt[MTN-1]; i = 1; }
    }
    mt[0] = 0x80000000u;
    r->idx = MTN;
}
static void mt_twist(RNG *r) {
    uint32_t *mt = r->mt; uint32_t y, lb; int kk;
    const int bug = r->buggy;
    for (kk = 0; kk < MTN - MTM; kk++) {
        y = (mt[kk] & 0x80000000u) | (mt[kk+1] & 0x7fffffffu);
        lb = bug ? (mt[kk] & 1u) : (mt[kk+1] & 1u);
        mt[kk] = mt[kk+MTM] ^ (y >> 1) ^ (lb ? 0x9908b0dfu : 0u);
    }
    for (; kk < MTN - 1; kk++) {
        y = (mt[kk] & 0x80000000u) | (mt[kk+1] & 0x7fffffffu);
        lb = bug ? (mt[kk] & 1u) : (mt[kk+1] & 1u);
        mt[kk] = mt[kk+(MTM-MTN)] ^ (y >> 1) ^ (lb ? 0x9908b0dfu : 0u);
    }
    y = (mt[MTN-1] & 0x80000000u) | (mt[0] & 0x7fffffffu);
    lb = bug ? (mt[MTN-1] & 1u) : (mt[0] & 1u);
    mt[MTN-1] = mt[MTM-1] ^ (y >> 1) ^ (lb ? 0x9908b0dfu : 0u);
    r->idx = 0;
}
static inline uint32_t mt_u32(RNG *r) {
    if (r->idx >= MTN) mt_twist(r);
    uint32_t y = r->mt[r->idx++];
    y ^= y >> 11; y ^= (y << 7) & 0x9d2c5680u; y ^= (y << 15) & 0xefc60000u; y ^= y >> 18;
    return y;
}
static inline double mt_res53(RNG *r) {
    uint32_t a = mt_u32(r) >> 5, b = mt_u32(r) >> 6;
    return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
}

/* glibc srandom_r / random_r, TYPE_3 (deg 31, sep 3) */
static void gl_srand(RNG *r, uint32_t seed) {
    if (seed == 0) seed = 1;
    int32_t word = (int32_t)seed;
    r->gr[0] = word;
    for (int i = 1; i < 31; i++) {
        long hi = word / 127773, lo = word % 127773;
        word = (int32_t)(16807 * lo - 2836 * hi);
        if (word < 0) word += 2147483647;
        r->gr[i] = word;
    }
    r->gf = 3; r->gb = 0;
    for (int k = 0; k < 310; k++) {
        uint32_t v = (uint32_t)r->gr[r->gf] + (uint32_t)r->gr[r->gb];
        r->gr[r->gf] = (int32_t)v;
        if (++r->gf >= 31) { r->gf = 0; ++r->gb; } else if (++r->gb >= 31) r->gb = 0;
    }
}
static inline int32_t gl_random(RNG *r) {
    uint32_t v = (uint32_t)r->gr[r->gf] + (uint32_t)r->gr[r->gb];
    r->gr[r->gf] = (int32_t)v;
    int32_t res = (int32_t)(v >> 1);
    if (++r->gf >= 31) { r->gf = 0; ++r->gb; } else if (++r->gb >= 31) r->gb = 0;
    return res;
}
static inline int32_t ms_rand(RNG *r) { r->ms = r->ms * 214013u + 2531011u; return (int32_t)((r->ms >> 16) & 0x7fff); }

#define JMUL 0x5DEECE66DULL
#define JMASK ((1ULL << 48) - 1)
static inline int32_t j_next(RNG *r, int bits) {
    r->js = (r->js * JMUL + 0xBULL) & JMASK;
    return (int32_t)(int64_t)(r->js >> (48 - bits));
}
static inline int32_t j_nextInt(RNG *r, int32_t bound) {
    if ((bound & -bound) == bound) return (int32_t)(((int64_t)bound * (int64_t)j_next(r, 31)) >> 31);
    int32_t bits, val;
    do { bits = j_next(r, 31); val = bits % bound; } while ((int32_t)((uint32_t)bits - (uint32_t)val + (uint32_t)(bound - 1)) < 0);
    return val;
}
static inline double j_nextDouble(RNG *r) {
    int64_t a = j_next(r, 26), b = j_next(r, 27);
    return (double)((a << 27) + b) * (1.0 / (double)(1ULL << 53));
}
static inline double d48(RNG *r) {
    r->x48 = (r->x48 * 0x5DEECE66DULL + 0xBULL) & JMASK;
    return (double)r->x48 / 281474976710656.0;
}

/* ---- seeding ---- */
/* key: limbs for F_MTPY; ival: integer seed for the others */
static void rng_seed(RNG *r, int fam, const uint32_t *key, int klen, uint64_t ival) {
    r->fam = fam; r->buggy = 0;
    switch (fam) {
    case F_MTPY: mt_init_by_array(r, key, klen); break;
    case F_MTG: mt_init_genrand(r, (uint32_t)ival); break;
    case F_PHP5: mt_init_genrand(r, (uint32_t)ival); r->buggy = 1; break;
    case F_GLIBC: gl_srand(r, (uint32_t)ival); break;
    case F_MSVC: r->ms = (uint32_t)ival; break;
    case F_JAVA: r->js = (ival ^ JMUL) & JMASK; break;
    case F_D48: r->x48 = (((uint64_t)(uint32_t)ival) << 16) | 0x330EULL; break;
    }
}

/* ---- draw idioms: uniform-ish integer in [0,n) as the library/idiom computes it ---- */
enum { I_PY2=0, I_PY3, I_PYGM, I_MTMOD, I_NPR53, I_NPINT, I_STDUID, I_PHP7R, I_PHP7M, I_PHP5R, I_PHP5M,
       I_GLMOD, I_GLSC, I_GLDIV, I_MSMOD, I_MSSC, I_JINT, I_JDBL, I_D48, NIDI };
static const int IDI_FAM[NIDI] = { F_MTPY, F_MTPY, F_MTPY, F_MTG, F_MTG, F_MTG, F_MTG, F_MTG, F_MTG, F_PHP5, F_PHP5,
       F_GLIBC, F_GLIBC, F_GLIBC, F_MSVC, F_MSVC, F_JAVA, F_JAVA, F_D48 };
static const char *IDI_NAME[NIDI] = {
 "py2.7 int(random()*n)=randrange/randint/choice", "py3.2+ _randbelow (getrandbits(k) reject) =randrange/randint/choice",
 "py getrandbits(k)%n", "mt19937(init_genrand) u32%n", "numpy int(random_sample()*n)", "numpy RandomState.randint (masked reject)",
 "libstdc++4.6 uniform_int_distribution(mt19937)", "PHP>=7.1 mt_rand(0,n-1)", "PHP>=7.1 mt_rand()%n",
 "PHP<7.1 mt_rand(0,n-1) (buggy twist, RAND_RANGE)", "PHP<7.1 mt_rand()%n (buggy twist)",
 "glibc rand()%n", "glibc (int)(n*rand()/(RAND_MAX+1.0)) =PHP5 rand(0,n-1)", "glibc rand()/(RAND_MAX/n+1)",
 "MSVC rand()%n", "MSVC rand()*n/(RAND_MAX+1)", "Java Random.nextInt(n)", "Java (int)(nextDouble()*n)", "drand48: (int)(drand48()*n) =Perl int(rand(n))" };
static const char *IDI_SHORT[NIDI] = { "PY2","PY3","PYGM","MTMOD","NPR53","NPINT","STDUID","PHP7R","PHP7M","PHP5R","PHP5M",
 "GLMOD","GLSC","GLDIV","MSMOD","MSSC","JINT","JDBL","D48" };

static inline int bitlen(uint32_t n) { int k = 0; while (n) { k++; n >>= 1; } return k; }

static inline int draw(RNG *r, int idiom, int n) {
    switch (idiom) {
    case I_PY2: return (int)(mt_res53(r) * n);
    case I_PY3: { int k = bitlen((uint32_t)n); uint32_t v; do v = mt_u32(r) >> (32 - k); while (v >= (uint32_t)n); return (int)v; }
    case I_PYGM: { int k = bitlen((uint32_t)n); return (int)((mt_u32(r) >> (32 - k)) % (uint32_t)n); }
    case I_MTMOD: return (int)(mt_u32(r) % (uint32_t)n);
    case I_NPR53: return (int)(mt_res53(r) * n);
    case I_NPINT: { uint32_t mx = (uint32_t)(n - 1), mask = mx; mask |= mask >> 1; mask |= mask >> 2; mask |= mask >> 4; mask |= mask >> 8; mask |= mask >> 16;
                    uint32_t v; do v = mt_u32(r) & mask; while (v > mx); return (int)v; }
    case I_STDUID: { uint64_t urng = 0xFFFFFFFFULL, ue = (uint64_t)n, sc = urng / ue, past = ue * sc, v;
                     do v = mt_u32(r); while (v >= past); return (int)(v / sc); }
    case I_PHP7R: { uint32_t um = (uint32_t)n, v = mt_u32(r);
                    if (um & (um - 1)) { uint32_t limit = 0xFFFFFFFFu - (0xFFFFFFFFu % um) - 1; while (v > limit) v = mt_u32(r); }
                    return (int)(v % um); }
    case I_PHP7M: return (int)((mt_u32(r) >> 1) % (uint32_t)n);
    case I_PHP5R: { uint32_t v = mt_u32(r) >> 1; return (int)(long)((double)n * (v / 2147483648.0)); }
    case I_PHP5M: return (int)((mt_u32(r) >> 1) % (uint32_t)n);
    case I_GLMOD: return gl_random(r) % n;
    case I_GLSC: return (int)(n * (gl_random(r) / 2147483648.0));
    case I_GLDIV: return gl_random(r) / (2147483647 / n + 1);
    case I_MSMOD: return ms_rand(r) % n;
    case I_MSSC: return (ms_rand(r) * n) / 32768;
    case I_JINT: return j_nextInt(r, n);
    case I_JDBL: return (int)(j_nextDouble(r) * n);
    case I_D48: return (int)(d48(r) * n);
    }
    return -1;
}

/* ---- emission models ---- */
enum { M_A=0, M_B, M_C, M_D, M_S, M_CH, M_CH0, NMOD };
static const char *MOD_NAME[NMOD] = {
 "a: rune=draw(29)", "b: redraw while ==prev", "c: if ==prev use next draw (once)", "d: draw(28) skipping prev (=choice of list without prev)",
 "s: concatenated Fisher-Yates shuffles of the 29 runes", "e: chain c+=1+draw(28) (compare increments to D)", "e0: chain c+=draw(29) (compare increments to D)" };
static const char *MOD_SHORT[NMOD] = { "a","b","c","d","s","e","e0" };
/* writes n symbols; for M_CH/M_CH0 writes increments (0..28) */
static void emit(RNG *r, int idiom, int model, uint8_t *out, int n) {
    int prev = -1;
    switch (model) {
    case M_A: for (int i = 0; i < n; i++) out[i] = (uint8_t)draw(r, idiom, 29); break;
    case M_B: for (int i = 0; i < n; i++) { int v; do v = draw(r, idiom, 29); while (v == prev); out[i] = (uint8_t)v; prev = v; } break;
    case M_C: for (int i = 0; i < n; i++) { int v = draw(r, idiom, 29); if (v == prev) v = draw(r, idiom, 29); out[i] = (uint8_t)v; prev = v; } break;
    case M_D: for (int i = 0; i < n; i++) { int v; if (prev < 0) v = draw(r, idiom, 29); else { v = draw(r, idiom, 28); if (v >= prev) v++; } out[i] = (uint8_t)v; prev = v; } break;
    case M_S: { int i = 0; while (i < n) { uint8_t p[29]; for (int k = 0; k < 29; k++) p[k] = (uint8_t)k;
                  for (int k = 28; k >= 1; k--) { int j = draw(r, idiom, k + 1); uint8_t t = p[k]; p[k] = p[j]; p[j] = t; }
                  for (int k = 0; k < 29 && i < n; k++) out[i++] = p[k]; } } break;
    case M_CH: for (int i = 0; i < n; i++) out[i] = (uint8_t)(1 + draw(r, idiom, 28)); break;
    case M_CH0: for (int i = 0; i < n; i++) out[i] = (uint8_t)draw(r, idiom, 29); break;
    }
}
