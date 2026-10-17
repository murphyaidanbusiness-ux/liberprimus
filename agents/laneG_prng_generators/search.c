/* laneG direct-emission search.
 * usage: search CORPUS.bin NCORP PAGESTARTS.txt SEEDS.txt SHARD NSHARD OUT.txt [NG]
 * For each seed x idiom x model: emit NG symbols; compare against
 *   models a,b,c,d,s : rune corpora (real + nulls): exact Gematria-order runs (5-gram seeded, any alignment),
 *                      label-invariant runs (any bijection of the 29 symbols; seeded by exact 5-grams of the previous-occurrence-distance transform, any alignment; run = bijection-consistent extension),
 *                      Hamming match count over 64 runes at each of the 55 real page starts, every gen offset.
 *   models e,e0      : increment corpora D and -D (real + nulls): exact runs any alignment; Hamming at page starts (real D).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "prng.h"

#define NC 12956
#define STRIDE (NC + 1)
#define G5 20511149u   /* 29^5 */
#define W 64           /* hamming window */
#define MAXCORP 32
#define TOPK 12
static int NCORP, NG = 5300;
static uint8_t *XC, *XD;   /* concatenated targets with 0xFF separators */
static int NXC, NXD;
static int pstart[64], npage;

typedef struct { uint32_t code; int pos; } Ent;
static int cmp_ent(const void *a, const void *b) { uint32_t x = ((Ent*)a)->code, y = ((Ent*)b)->code; return x < y ? -1 : x > y; }
typedef struct { uint64_t h; int pos; } PEnt;
static int cmp_pent(const void *a, const void *b) { uint64_t x = ((PEnt*)a)->h, y = ((PEnt*)b)->h; return x < y ? -1 : x > y; }

typedef struct { Ent *e; int n; uint8_t *bits; } GIdx;
static void build_gidx(GIdx *g, const uint8_t *X, int n) {
    g->e = malloc(sizeof(Ent) * n); g->n = 0; g->bits = calloc(G5 / 8 + 1, 1);
    for (int p = 0; p + 5 <= n; p++) {
        uint32_t c = 0; int ok = 1;
        for (int i = 0; i < 5; i++) { if (X[p+i] > 28) { ok = 0; break; } c = c * 29 + X[p+i]; }
        if (!ok) continue;
        g->e[g->n].code = c; g->e[g->n].pos = p; g->n++; g->bits[c >> 3] |= 1 << (c & 7);
    }
    qsort(g->e, g->n, sizeof(Ent), cmp_ent);
}
static inline int lb_ent(const Ent *e, int n, uint32_t c) { int lo = 0, hi = n; while (lo < hi) { int m = (lo + hi) >> 1; if (e[m].code < c) lo = m + 1; else hi = m; } return lo; }

typedef struct { PEnt *e; int n; uint8_t *bits; } PIdx;
/* Label-invariant transform: r[i] = distance to the previous occurrence of the same symbol (1..DCAP), 0 if none within DCAP
 * (or symbol is a separator). Invariant under any bijective relabelling of the 29 runes. Seeds = exact 5-grams of r. */
#define DCAP 100
#define PBITS (1u << 26)
static void prevdist(const uint8_t *x, int n, uint8_t *r) {
    int last[256]; for (int i = 0; i < 256; i++) last[i] = -1000000;
    for (int i = 0; i < n; i++) {
        if (x[i] > 28) { r[i] = 0xFF; for (int k = 0; k < 256; k++) last[k] = -1000000; continue; }
        int d = i - last[x[i]]; r[i] = (uint8_t)(d <= DCAP ? d : 0); last[x[i]] = i;
    }
}
static inline uint64_t pcode(const uint8_t *r, int *ok) { uint64_t c = 0; for (int i = 0; i < 5; i++) { if (r[i] == 0xFF) { *ok = 0; return 0; } c = c * 101 + r[i]; } *ok = 1; return c; }
static uint8_t *RC;
static void build_pidx(PIdx *g, const uint8_t *X, int n) {
    RC = malloc(n + 64); prevdist(X, n, RC);
    g->e = malloc(sizeof(PEnt) * n); g->n = 0; g->bits = calloc(PBITS / 8, 1);
    for (int p = 0; p + 5 <= n; p++) {
        int ok; uint64_t h = pcode(RC + p, &ok); if (!ok) continue;
        g->e[g->n].h = h; g->e[g->n].pos = p; g->n++; uint32_t b = (uint32_t)((h * 0x9E3779B97F4A7C15ULL) >> 38); g->bits[b >> 3] |= 1 << (b & 7);
    }
    qsort(g->e, g->n, sizeof(PEnt), cmp_pent);
}
static inline int lb_pent(const PEnt *e, int n, uint64_t c) { int lo = 0, hi = n; while (lo < hi) { int m = (lo + hi) >> 1; if (e[m].h < c) lo = m + 1; else hi = m; } return lo; }

static GIdx gC, gD; static PIdx pC;

/* exact any-alignment runs: best[cid] */
static void exact_runs(const uint8_t *g, int ng, const GIdx *ix, const uint8_t *X, int ncorp_mod, int *best, int *bj, int *bp) {
    uint32_t c = 0; uint32_t p4 = 29u * 29 * 29 * 29;
    for (int i = 0; i < 4; i++) c = c * 29 + g[i];
    for (int j = 0; j + 5 <= ng; j++) {
        if (j) c = (c - g[j-1] * p4) * 29 + g[j+4]; else c = c * 29 + g[4];
        if (!(ix->bits[c >> 3] >> (c & 7) & 1)) continue;
        for (int k = lb_ent(ix->e, ix->n, c); k < ix->n && ix->e[k].code == c; k++) {
            int p = ix->e[k].pos, L = 5;
            while (j + L < ng && g[j+L] == X[p+L]) L++;
            int cid = (p / STRIDE) % ncorp_mod;
            if (L > best[cid]) { best[cid] = L; if (cid == 0) { *bj = j; *bp = p % STRIDE; } }
        }
    }
}
static int pat_hits_real, pat_hits_null, nopat = 0;
static void pattern_runs(const uint8_t *g, int ng, int *best, int *bj, int *bp) {
    static uint8_t r[20000]; prevdist(g, ng, r);
    const uint64_t P4 = 101ULL * 101 * 101 * 101; uint64_t c = 0;
    for (int i = 0; i < 4; i++) c = c * 101 + r[i];
    for (int j = 0; j + 5 <= ng; j++) {
        if (j) c = (c - r[j-1] * P4) * 101 + r[j+4]; else c = c * 101 + r[4];
        uint32_t b = (uint32_t)((c * 0x9E3779B97F4A7C15ULL) >> 38);
        if (!(pC.bits[b >> 3] >> (b & 7) & 1)) continue;
        for (int k = lb_pent(pC.e, pC.n, c); k < pC.n && pC.e[k].h == c; k++) {
            int p = pC.e[k].pos; int8_t fw[32], bw[32]; memset(fw, -1, 32); memset(bw, -1, 32);
            int L = 0;
            while (j + L < ng && XC[p+L] <= 28) {
                int a = g[j+L], t = XC[p+L];
                if (fw[a] < 0 && bw[t] < 0) { fw[a] = (int8_t)t; bw[t] = (int8_t)a; }
                else if (fw[a] != t) break;
                L++;
            }
            int cid = p / STRIDE;
            if (L > best[cid]) { best[cid] = L; if (cid == 0) { *bj = j; *bp = p % STRIDE; } }
        }
    }
}
/* Hamming: max over page starts t and gen offsets j of #matches in W */
static int HAMJ = 1001;
static int hamming(const uint8_t *g, int ng, const uint8_t *T, int off, int *bj, int *bt) {
    static uint8_t acc[20000]; int nj = ng - W, best = -1; if (nj > HAMJ) nj = HAMJ;
    for (int pg = 0; pg < npage; pg++) {
        int t = pstart[pg] + off;
        memset(acc, 0, nj);
        for (int i = 0; i < W; i++) { uint8_t s = T[t+i]; const uint8_t *gg = g + i; for (int j = 0; j < nj; j++) acc[j] += (gg[j] == s); }
        for (int j = 0; j < nj; j++) if (acc[j] > best) { best = acc[j]; *bj = j; *bt = pg; }
    }
    return best;
}

/* aggregation */
enum { ST_EXACT = 0, ST_PAT, ST_HAM, NST };
static const char *ST_NAME[NST] = { "exact", "pattern", "hamming" };
static long long histR[NIDI][NMOD][NST][1024], histN[NIDI][NMOD][NST][1024];
static long long nstreams[NIDI][NMOD];
typedef struct { int v; int j, p; char lab[96]; } Top;
static Top top[NIDI][NMOD][NST][TOPK];
static void top_add(Top *t, int v, int j, int p, const char *lab) {
    if (v <= t[TOPK-1].v) return;
    int k = TOPK - 1; while (k > 0 && t[k-1].v < v) { t[k] = t[k-1]; k--; }
    t[k].v = v; t[k].j = j; t[k].p = p; strncpy(t[k].lab, lab, 95); t[k].lab[95] = 0;
}
static inline int capv(int v) { return v > 1023 ? 1023 : v; }

static void run_stream(RNG *base, int idi, int mod, const char *lab) {
    static uint8_t g[20000]; RNG r = *base;
    emit(&r, idi, mod, g, NG); g[NG] = 0xFE;
    int best[MAXCORP], bj = -1, bp = -1, hj = -1, ht = -1;
    nstreams[idi][mod]++;
    if (mod == M_CH || mod == M_CH0) {
        memset(best, 0, sizeof best);
        exact_runs(g, NG, &gD, XD, NCORP, best, &bj, &bp);
        histR[idi][mod][ST_EXACT][capv(best[0])]++; for (int c = 1; c < NCORP; c++) histN[idi][mod][ST_EXACT][capv(best[c])]++;
        top_add(top[idi][mod][ST_EXACT], best[0], bj, bp, lab);
        int h = hamming(g, NG, XD, 1, &hj, &ht);  /* real D, skip the page's first increment */
        histR[idi][mod][ST_HAM][h]++; top_add(top[idi][mod][ST_HAM], h, hj, ht, lab);
    } else {
        memset(best, 0, sizeof best);
        exact_runs(g, NG, &gC, XC, NCORP, best, &bj, &bp);
        histR[idi][mod][ST_EXACT][capv(best[0])]++; for (int c = 1; c < NCORP; c++) histN[idi][mod][ST_EXACT][capv(best[c])]++;
        top_add(top[idi][mod][ST_EXACT], best[0], bj, bp, lab);
        memset(best, 0, sizeof best); bj = bp = -1;
        if (!nopat) pattern_runs(g, NG, best, &bj, &bp);
        histR[idi][mod][ST_PAT][capv(best[0])]++; for (int c = 1; c < NCORP; c++) histN[idi][mod][ST_PAT][capv(best[c])]++;
        top_add(top[idi][mod][ST_PAT], best[0], bj, bp, lab);
        int h = hamming(g, NG, XC, 0, &hj, &ht);
        histR[idi][mod][ST_HAM][h]++; top_add(top[idi][mod][ST_HAM], h, hj, ht, lab);
    }
}

int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage\n"); return 1; }
    NCORP = atoi(argv[2]); int shard = atoi(argv[5]), nshard = atoi(argv[6]);
    if (argc > 8) NG = atoi(argv[8]);
    if (getenv("HAMJ")) HAMJ = atoi(getenv("HAMJ"));
    if (getenv("NOPAT")) nopat = 1;
    const char *only_mod = getenv("ONLY_MODELS"); /* e.g. "abdsee0" not used if null */
    uint8_t *raw = malloc(NC * NCORP);
    FILE *f = fopen(argv[1], "rb"); if (fread(raw, 1, NC * NCORP, f) != (size_t)(NC * NCORP)) { fprintf(stderr, "corpus read\n"); return 1; } fclose(f);
    f = fopen(argv[3], "r"); npage = 0; while (fscanf(f, "%d", &pstart[npage]) == 1) npage++; fclose(f);
    NXC = STRIDE * NCORP; XC = malloc(NXC + 64); memset(XC, 0xFF, NXC + 64);
    NXD = STRIDE * NCORP * 2; XD = malloc(NXD + 64); memset(XD, 0xFF, NXD + 64);
    for (int c = 0; c < NCORP; c++) {
        memcpy(XC + c * STRIDE, raw + c * NC, NC);
        for (int i = 0; i < NC; i++) {
            int d = i ? (raw[c*NC+i] - raw[c*NC+i-1] + 29) % 29 : raw[c*NC];
            XD[c * STRIDE + i] = (uint8_t)d; XD[(NCORP + c) * STRIDE + i] = (uint8_t)((29 - d) % 29);
        }
    }
    build_gidx(&gC, XC, NXC); build_gidx(&gD, XD, NXD); build_pidx(&pC, XC, NXC);
    for (int a = 0; a < NIDI; a++) for (int b = 0; b < NMOD; b++) for (int s = 0; s < NST; s++) for (int k = 0; k < TOPK; k++) top[a][b][s][k].v = -1;
    fprintf(stderr, "indexes built: C %d D %d P %d\n", gC.n, gD.n, pC.n);

    FILE *sf = fopen(argv[4], "r"); char line[1 << 16]; long ln = -1, done = 0;
    static uint32_t key[8192];
    while (fgets(line, sizeof line, sf)) {
        ln++; if (ln % nshard != shard) continue;
        char *p = line, *e; char kind = *p; p += 2;
        int klen = 0; long long iv = 0; int mtpy_only = 0, nonpy_only = 0;
        if (kind == 'I') { iv = strtoll(p, &e, 10); p = e; unsigned long long a = iv < 0 ? -iv : iv; if (!a) key[klen++] = 0; while (a) { key[klen++] = (uint32_t)a; a >>= 32; } }
        else if (kind == 'K') { klen = (int)strtol(p, &e, 10); p = e; for (int i = 0; i < klen; i++) { key[i] = (uint32_t)strtoul(p, &e, 10); p = e; } mtpy_only = 1; }
        else if (kind == 'J') { iv = strtoll(p, &e, 10); p = e; nonpy_only = 1; }
        else continue;
        while (*p == ' ') p++; char lab[128]; int L = 0; while (*p && *p != '\n' && L < 120) lab[L++] = *p++; lab[L] = 0;
        RNG base[NFAM]; int have[NFAM] = {0};
        for (int idi = 0; idi < NIDI; idi++) {
            int fam = IDI_FAM[idi];
            if (mtpy_only && fam != F_MTPY) continue;
            if (nonpy_only && fam == F_MTPY) continue;
            if (!have[fam]) { rng_seed(&base[fam], fam, key, klen, (uint64_t)iv); have[fam] = 1; }
            char lab2[128]; snprintf(lab2, sizeof lab2, "%s", lab);
            for (int mod = 0; mod < NMOD; mod++) {
                if (only_mod && !strchr(only_mod, 'a' + mod)) continue;
                run_stream(&base[fam], idi, mod, lab2);
            }
        }
        done++;
        if (done % 2000 == 0) { fprintf(stderr, "shard %d: %ld seeds\n", shard, done); }
    }
    FILE *o = fopen(argv[7], "w");
    fprintf(o, "SEEDS %ld\n", done);
    for (int a = 0; a < NIDI; a++) for (int b = 0; b < NMOD; b++) {
        if (!nstreams[a][b]) continue;
        fprintf(o, "N %d %d %lld\n", a, b, nstreams[a][b]);
        for (int s = 0; s < NST; s++) {
            for (int v = 0; v < 1024; v++) if (histR[a][b][s][v] || histN[a][b][s][v]) fprintf(o, "H %d %d %d %d %lld %lld\n", a, b, s, v, histR[a][b][s][v], histN[a][b][s][v]);
            for (int k = 0; k < TOPK; k++) if (top[a][b][s][k].v >= 0) fprintf(o, "T %d %d %d %d %d %d %s\n", a, b, s, top[a][b][s][k].v, top[a][b][s][k].j, top[a][b][s][k].p, top[a][b][s][k].lab);
        }
    }
    fclose(o);
    return 0;
}
