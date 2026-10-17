/* laneG model (f): generator output as the per-position key of the chain cipher; screen by IoC of the decoded stream.
 * usage: keystream CORPUS.bin NCORP CIDX PAGESTARTS SEEDS SHARD NSHARD OUT PERPAGE SUBMOD SUBRES
 *   CIDX     : which corpus copy (0 = real, 1..20 = D-shuffle nulls)
 *   PERPAGE  : 0 = one stream per seed (continuous across pages, and restarted at each page)
 *              1 = a fresh seed per page: page p uses integer seed (iv + p)   (I lines only)
 *   SUBMOD/SUBRES : process only seed lines with (lineno % SUBMOD == SUBRES)  (null subsampling)
 * Decodes (D_i = c_i - c_{i-1} mod 29, prev = 0 at each page start):
 *   app 0  A+ : D==0 -> EA ; else p = (D-1+k) mod 28        k = draw(28)
 *   app 1  A- : D==0 -> EA ; else p = (D-1-k) mod 28
 *   app 2  M* : p = D*K mod 29, K = 1+k                      (x(EA)=0)
 *   app 3  M/ : p = D*K^-1 mod 29
 *   conv X: key index advances at every rune; conv Y: not on D==0
 *   mode C: key index continuous over the corpus; mode R: key index restarts at each page
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "prng.h"
#define NC 12956
#define NV 16
#define TOPK 15
#define HB 400
static uint8_t D[NC]; static int pst[64], plen[64], npage, pageof[NC], posin[NC];
static int INV[29];
static double ioc_counts(const long *n, long N) { double s = 0; for (int i = 0; i < 29; i++) s += (double)n[i] * (n[i] - 1); return 29.0 * s / ((double)N * (N - 1)); }
static inline int dec(int app, int d, int k) {
    switch (app) {
    case 0: return d ? (d - 1 + k) % 28 : 28;
    case 1: return d ? ((d - 1 - k) % 28 + 28) % 28 : 28;
    case 2: return (d * (k + 1)) % 29;
    default: return (d * INV[k + 1]) % 29;
    }
}
typedef struct { double v; char lab[100]; } Top;
static Top top[NIDI][NV][TOPK];
static long long hist[NIDI][NV][HB + 1], cnt[NIDI][NV];
static double sum[NIDI][NV], sumsq[NIDI][NV];
static void add(int idi, int v, double x, const char *lab) {
    cnt[idi][v]++; sum[idi][v] += x; sumsq[idi][v] += x * x;
    int b = (int)floor((x - 0.95) / 0.0005); if (b < 0) b = 0; if (b > HB) b = HB; hist[idi][v][b]++;
    Top *t = top[idi][v]; if (x <= t[TOPK-1].v) return;
    int k = TOPK - 1; while (k > 0 && t[k-1].v < x) { t[k] = t[k-1]; k--; }
    t[k].v = x; strncpy(t[k].lab, lab, 99); t[k].lab[99] = 0;
}
int main(int argc, char **argv) {
    int NCORP = atoi(argv[2]), cidx = atoi(argv[3]); int shard = atoi(argv[6]), nshard = atoi(argv[7]);
    int perpage = atoi(argv[9]), submod = atoi(argv[10]), subres = atoi(argv[11]);
    uint8_t *raw = malloc(NC * NCORP); FILE *f = fopen(argv[1], "rb"); if (fread(raw, 1, NC * NCORP, f) != (size_t)NC * NCORP) return 1; fclose(f);
    uint8_t *c = raw + NC * cidx;
    f = fopen(argv[4], "r"); npage = 0; while (fscanf(f, "%d", &pst[npage]) == 1) npage++; fclose(f);
    for (int p = 0; p < npage; p++) { plen[p] = (p + 1 < npage ? pst[p+1] : NC) - pst[p]; for (int i = 0; i < plen[p]; i++) { pageof[pst[p]+i] = p; posin[pst[p]+i] = i; } }
    for (int i = 0; i < NC; i++) D[i] = (uint8_t)((c[i] - (posin[i] ? c[i-1] : 0) + 29) % 29);
    for (int a = 1; a < 29; a++) for (int b = 1; b < 29; b++) if (a * b % 29 == 1) INV[a] = b;
    for (int a = 0; a < NIDI; a++) for (int v = 0; v < NV; v++) for (int k = 0; k < TOPK; k++) top[a][v][k].v = -1;
    FILE *sf = fopen(argv[5], "r"); static char line[1 << 16]; long ln = -1, done = 0; static uint32_t key[8192];
    static uint8_t ks[NC + 8];
    while (fgets(line, sizeof line, sf)) {
        ln++; if (ln % nshard != shard) continue; if (ln % submod != subres) continue;
        char *p = line, *e; char kind = *p; p += 2; int klen = 0; long long iv = 0; int mtpy_only = 0, nonpy_only = 0;
        if (kind == 'I') { iv = strtoll(p, &e, 10); p = e; }
        else if (kind == 'K') { if (perpage) continue; klen = (int)strtol(p, &e, 10); p = e; for (int i = 0; i < klen; i++) { key[i] = (uint32_t)strtoul(p, &e, 10); p = e; } mtpy_only = 1; }
        else if (kind == 'J') { if (perpage) continue; iv = strtoll(p, &e, 10); p = e; nonpy_only = 1; }
        else continue;
        while (*p == ' ') p++; char lab[128]; int L = 0; while (*p && *p != '\n' && L < 120) lab[L++] = *p++; lab[L] = 0;
        for (int idi = 0; idi < NIDI; idi++) {
            int fam = IDI_FAM[idi]; if (mtpy_only && fam != F_MTPY) continue; if (nonpy_only && fam == F_MTPY) continue;
            long n[NV][29]; memset(n, 0, sizeof n);
            if (!perpage) {
                RNG r;
                if (kind == 'I') { unsigned long long a = iv < 0 ? -iv : iv; klen = 0; if (!a) key[klen++] = 0; while (a) { key[klen++] = (uint32_t)a; a >>= 32; } }
                rng_seed(&r, fam, key, klen, (uint64_t)iv);
                for (int i = 0; i < NC; i++) ks[i] = (uint8_t)draw(&r, idi, 28);
                for (int app = 0; app < 4; app++) {
                    int jx = 0, jy = 0;
                    for (int i = 0; i < NC; i++) {
                        int d = D[i], pi = posin[i];
                        if (pi == 0) { jy = 0; }
                        /* continuous */
                        n[app*4+0][dec(app, d, ks[i])]++;                 /* X,C */
                        n[app*4+1][dec(app, d, ks[jx])]++; if (d) jx++;  /* Y,C */
                        n[app*4+2][dec(app, d, ks[pi])]++;                /* X,R */
                        n[app*4+3][dec(app, d, ks[jy])]++; if (d) jy++;  /* Y,R */
                    }
                }
            } else {
                for (int pg = 0; pg < npage; pg++) {
                    RNG r; long long sv = iv + pg; unsigned long long a = sv < 0 ? -sv : sv; klen = 0; if (!a) key[klen++] = 0; while (a) { key[klen++] = (uint32_t)a; a >>= 32; }
                    rng_seed(&r, fam, key, klen, (uint64_t)sv);
                    for (int i = 0; i < plen[pg]; i++) ks[i] = (uint8_t)draw(&r, idi, 28);
                    for (int app = 0; app < 4; app++) {
                        int jy = 0;
                        for (int i = 0; i < plen[pg]; i++) {
                            int d = D[pst[pg]+i];
                            n[app*4+2][dec(app, d, ks[i])]++;
                            n[app*4+3][dec(app, d, ks[jy])]++; if (d) jy++;
                        }
                    }
                }
            }
            for (int v = 0; v < NV; v++) { if (perpage && (v % 4) < 2) continue; add(idi, v, ioc_counts(n[v], NC), lab); }
        }
        done++;
    }
    FILE *o = fopen(argv[8], "w"); fprintf(o, "SEEDS %ld\n", done);
    for (int a = 0; a < NIDI; a++) for (int v = 0; v < NV; v++) {
        if (!cnt[a][v]) continue;
        fprintf(o, "S %d %d %lld %.10g %.10g\n", a, v, cnt[a][v], sum[a][v], sumsq[a][v]);
        for (int b = 0; b <= HB; b++) if (hist[a][v][b]) fprintf(o, "H %d %d %d %lld\n", a, v, b, hist[a][v][b]);
        for (int k = 0; k < TOPK; k++) if (top[a][v][k].v >= 0) fprintf(o, "T %d %d %.6f %s\n", a, v, top[a][v][k].v, top[a][v][k].lab);
    }
    fclose(o); return 0;
}
