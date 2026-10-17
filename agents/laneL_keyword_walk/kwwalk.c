/* kwwalk: exhaustive keyword-corner brute force for Oosterhof's doublet-dodge walk.
   c_j = base_w[ g^(clock mod 5)[p_j] ]; skip (clock += 1, recompute once) when the emission equals the previous
   cipher rune; clock += 1 per rune; after each word base_{w+1} = base_w o g^((clock-1) mod 5) o sigma.
   Decryption only ever needs binv_w = base_w^{-1}:  binv_{w+1} = sigma^{-1} o g^{-e_w} o binv_w.
   At each rune two readings: N  p = g^{-t} binv(c)       valid iff c != previous cipher rune
                              D  p = g^{-(t+1)} binv(c)   valid iff g^t(p) == binv(previous cipher rune)  (a skip happened)
   Both are followed (DFS); the clock only matters mod 5.
   Stage A: all (base0, g): word 0 must be a lexicon word (prefix bitmaps + hash).
   Stage B: survivors x all sigma: word 1 must be a lexicon word; then words 2.. gated by cumulative LM score; keep top-K
            by LM score over the first NPREF runes (whole words).
   Modes: 0 global clock (Oosterhof), 1 clock reset to 0 at each word start, 2 fixed base (no walk; sigma unused).
   Usage: kwwalk TEXT NPREF OUT [-m modes_bitmask] [-K topK] [-b baselist] [-s siglist] [-g glist] [-A amax]
   Lists are files of indices (one per line) into A.bin (bases, sigmas) and G.bin.                                   */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#include <time.h>
#include <immintrin.h>
#define M 29
#define V 30
#define BND 29
#define MAXW 400
#define MAXN 16000
static int NA, NG; static uint8_t *Aall, *Ginv5, *Gfw5;   /* Ginv5[g][k][x] = g^{-k}(x); Gfw5[g][k][x] = g^k(x) */
static uint8_t *Ainv;                                     /* Ainv[a][x] = a^{-1}(x) */
static int16_t *LM;
static int nw, lens[MAXW], st[MAXW], N; static int cip[MAXN];
static int npref, nwp;                                    /* words used for the prefix */
/* ---------- lexicon ---------- */
#define HB 22
static uint64_t *H; static uint8_t *pre4[17];             /* pre4[L] bitmap over first-4 runes (L>=4) */
static uint8_t pre3[17][M*M*M], pre2[17][M*M], pre1[17][M]; static uint8_t *pre5[17];
static inline uint64_t hkey(int L, const int *p){ uint64_t k = 0x9E3779B97F4A7C15ULL ^ (uint64_t)L; for (int i=0;i<L;i++){ k = (k ^ (uint64_t)(p[i]+1)) * 0x100000001B3ULL; k ^= k>>29; } return k | 1; }
static inline uint64_t hmix(uint64_t k){ k ^= k>>33; k *= 0xff51afd7ed558ccdULL; k ^= k>>33; return k; }
static void hins(uint64_t k){ uint64_t h = hmix(k) & ((1ULL<<HB)-1); while (H[h] && H[h]!=k) h = (h+1) & ((1ULL<<HB)-1); H[h]=k; }
static inline int hhas(uint64_t k){ uint64_t h = hmix(k) & ((1ULL<<HB)-1); while (H[h]){ if (H[h]==k) return 1; h = (h+1) & ((1ULL<<HB)-1);} return 0; }
static inline int inlex(int L, const int *p){ if (L>16) return 0; return hhas(hkey(L,p)); }
static inline int prefok(int L, int d, const int *p){   /* d = number of runes decoded so far (1..4) */
  if (L>16) return 1;
  if (d==1) return pre1[L][p[0]];
  if (d==2) return pre2[L][p[0]*M+p[1]];
  if (d==3) return pre3[L][(p[0]*M+p[1])*M+p[2]];
  if (d==4 && L>=4){ int i=((p[0]*M+p[1])*M+p[2])*M+p[3]; return (pre4[L][i>>3]>>(i&7))&1; }
  if (d==5 && L>=5 && pre5[L]){ int i=(((p[0]*M+p[1])*M+p[2])*M+p[3])*M+p[4]; return (pre5[L][i>>3]>>(i&7))&1; }
  return 1;
}
static inline int lmword(const int *p, int L){ int a=BND,b=BND,c=BND,s=0; for(int i=0;i<L;i++){ s+=LM[((a*V+b)*V+c)*V+p[i]]; a=b;b=c;c=p[i]; } s+=LM[((a*V+b)*V+c)*V+BND]; return s; }
/* ---------- gates ---------- */
static double GA = -6.0, GB = 0.0;     /* cumulative LM gate for words>=2: cum >= 1000*(GA*n - GB*sqrt(n)), n = symbols */
#include <math.h>
static int gate[MAXN+MAXW]; static double DYN = 0; static int NSYM = 0; static int lexgate[MAXW];
/* ---------- top-K ---------- */
typedef struct { int score; int b, g, s, mode; int t0; } Cand;
static int K = 1000;
typedef struct { Cand *h; int n; } Heap;
static void hpush(Heap *hp, Cand c){
  if (hp->n < K){ int i=hp->n++; hp->h[i]=c; while(i>0){ int p=(i-1)/2; if (hp->h[p].score<=hp->h[i].score) break; Cand t=hp->h[p];hp->h[p]=hp->h[i];hp->h[i]=t; i=p; } return; }
  if (c.score <= hp->h[0].score) return;
  hp->h[0]=c; int i=0; for(;;){ int l=2*i+1,r=l+1,m=i; if(l<hp->n&&hp->h[l].score<hp->h[m].score)m=l; if(r<hp->n&&hp->h[r].score<hp->h[m].score)m=r; if(m==i)break; Cand t=hp->h[m];hp->h[m]=hp->h[i];hp->h[i]=t;i=m; }
}
/* ---------- per-thread search context ---------- */
typedef struct {
  const uint8_t *gi, *gf;    /* g^{-k} and g^k tables [5][29] */
  const uint8_t *si;         /* sigma^{-1} */
  int mode; int b, g, s;
  Heap *hp; long long nend, nw1;
  int lazy; const uint8_t *b0inv; int e0;   /* word-1 base filled only at needed runes until word 1 passes */
  int plain[MAXN];
} Ctx;
/* recursive word-level DFS from word w with inverse base binv, clock t (mod 5) at word start, cumulative LM cum.
   xprev = binv-image of the previous cipher rune under THIS word's base (computed inside). */
static void dfs_word(Ctx *cx, int w, const uint8_t *binv, int t, int cum);
static void dfs_rune(Ctx *cx, int w, const uint8_t *binv, int j, int t, int t0, int *p, int cum){
  int L = lens[w];
  if (j == L){
    int sc = cum + lmword(p, L);
    if (lexgate[w] && cx->mode != 2) { if (!inlex(L,p)) return; if (w==1) cx->nw1++; }
    else if (w >= 1) { if (sc < gate[st[w]+L+w+1]) return; }
    if (DYN > 0 && w >= 1 && cx->hp->n >= K){ int nsym = st[w]+L+w+1; double bound = sc - DYN*1000.0*(NSYM - nsym); if (bound < cx->hp->h[0].score) return; }
    memcpy(cx->plain + st[w], p, sizeof(int)*L);
    if (w+1 >= nwp){ cx->nend++; Cand c = {sc, cx->b, cx->g, cx->s, cx->mode, t0}; hpush(cx->hp, c); return; }
    if (cx->lazy){ uint8_t *fb = (uint8_t *)binv; const uint8_t *ge0 = cx->gi + cx->e0*M; for (int x=0;x<M;x++) fb[x] = cx->si[ ge0[ cx->b0inv[x] ] ]; cx->lazy = 0; }
    uint8_t nb[M];
    if (cx->mode == 2) memcpy(nb, binv, M);
    else { int e = (t + 4) % 5; const uint8_t *ge = cx->gi + e*M; for (int x=0;x<M;x++) nb[x] = cx->si[ ge[ binv[x] ] ]; }
    dfs_word(cx, w+1, nb, cx->mode==1 ? 0 : t, sc);
    return;
  }
  int i = st[w] + j; int c = cip[i]; int x = binv[c];
  int prevc = i>0 ? cip[i-1] : -1;
  /* N reading */
  int pg = lexgate[w] && cx->mode != 2;
  if (c != prevc){ p[j] = cx->gi[t*M + x]; if (!pg || prefok(L, j+1, p)) dfs_rune(cx, w, binv, j+1, (t+1)%5, t0, p, cum); }
  /* D reading */
  if (prevc >= 0){ int t1=(t+1)%5; int pd = cx->gi[t1*M + x]; if (cx->gf[t*M + pd] == binv[prevc]){ p[j]=pd; if (!pg || prefok(L, j+1, p)) dfs_rune(cx, w, binv, j+1, (t+2)%5, t0, p, cum); } }
}
static void dfs_word(Ctx *cx, int w, const uint8_t *binv, int t, int cum){ int p[64]; dfs_rune(cx, w, binv, 0, t, t, p, cum); }

/* ---------- stage A survivors ---------- */
typedef struct { int b, g, t1; int sc; uint8_t p0[16]; } Surv;   /* t1 = clock mod 5 after word 0 */
static Surv *SV; static long long nSV = 0, capSV = 0;

static int L0g; static int eqg[MAXN];
static long long nExact = 0;
static void exactA(int b, int g, const int *x){
  const uint8_t *I = Ginv5 + (size_t)g*5*M, *F = Gfw5 + (size_t)g*5*M; int L0 = L0g;
  int stt[64], sopt[64]; int p[64]; int d = 0; stt[0]=0; sopt[0]=0;
  while (d >= 0){
    int j = d, t = stt[d];
    if (j == L0){
      if (inlex(L0, p)){
        Surv s; s.b=b; s.g=g; s.t1=t; s.sc=lmword(p,L0); for(int k=0;k<L0&&k<16;k++) s.p0[k]=p[k];
        #pragma omp critical
        { if (nSV==capSV){ capSV*=2; SV=realloc(SV,capSV*sizeof(Surv)); } SV[nSV++]=s; }
      }
      d--; continue;
    }
    int o = sopt[d]++;
    if (o == 0){ if (!eqg[j]){ p[j]=I[t*M+x[j]]; if (prefok(L0,j+1,p)){ d++; stt[d]=(t+1)%5; sopt[d]=0; } } continue; }
    if (o == 1){ if (j>0){ int t1=(t+1)%5; int pd=I[t1*M+x[j]]; if (F[t*M+pd]==x[j-1]){ p[j]=pd; if (prefok(L0,j+1,p)){ d++; stt[d]=(t+2)%5; sopt[d]=0; } } } continue; }
    d--;
  }
}
static int *readlist(const char *fn, int *n){ FILE *f=fopen(fn,"r"); if(!f){perror(fn);exit(1);} int cap=1024,k=0; int *a=malloc(cap*sizeof(int)); int x; while(fscanf(f,"%d",&x)==1){ if(k==cap){cap*=2;a=realloc(a,cap*sizeof(int));} a[k++]=x;} fclose(f); *n=k; return a; }

int main(int argc, char **argv){
  if (argc < 4){ fprintf(stderr,"usage\n"); return 1; }
  const char *dir = getenv("KWDIR") ? getenv("KWDIR") : ".";
  char fn[1024];
  int modes = 1; char *bl=NULL,*sl=NULL,*gl=NULL;
  npref = atoi(argv[2]); const char *out = argv[3];
  for (int i=4;i<argc;i++){
    if(!strcmp(argv[i],"-m")) modes=atoi(argv[++i]); else if(!strcmp(argv[i],"-K")) K=atoi(argv[++i]);
    else if(!strcmp(argv[i],"-b")) bl=argv[++i]; else if(!strcmp(argv[i],"-s")) sl=argv[++i]; else if(!strcmp(argv[i],"-g")) gl=argv[++i];
    else if(!strcmp(argv[i],"-ga")) GA=atof(argv[++i]); else if(!strcmp(argv[i],"-gb")) GB=atof(argv[++i]); else if(!strcmp(argv[i],"-dyn")) DYN=atof(argv[++i]);
  }
  /* text */
  FILE *f = fopen(argv[1],"r"); if(!f){perror(argv[1]);return 1;}
  if (fscanf(f,"%d",&nw)!=1) return 1; N=0; for(int w=0;w<nw;w++){ if(fscanf(f,"%d",&lens[w])!=1) return 1; st[w]=N; N+=lens[w]; }
  for(int i=0;i<N;i++) if(fscanf(f,"%d",&cip[i])!=1) return 1; fclose(f);
  nwp=0; { int n=0; while(nwp<nw && n<npref){ n+=lens[nwp]; nwp++; } }
  int nr=0; for(int w=0;w<nwp;w++) nr+=lens[w]; NSYM = nr + nwp;
  { int acc=0; for (int w=1; w<nw; w++){ if (acc < 5){ lexgate[w]=1; acc += lens[w]; } } }   /* lexicon-gate words 1..k until >= 5 runes */
  for (int n=0;n<MAXN+MAXW;n++) gate[n] = (int)(1000.0*(GA*n - GB*sqrt((double)n)));
  /* sets */
  sprintf(fn,"%s/A.bin",dir); f=fopen(fn,"rb"); fseek(f,0,SEEK_END); NA=ftell(f)/M; rewind(f); Aall=malloc((size_t)NA*M); if(fread(Aall,1,(size_t)NA*M,f)!=(size_t)NA*M) return 1; fclose(f);
  Ainv=malloc((size_t)NA*M); for(long a=0;a<NA;a++) for(int x=0;x<M;x++) Ainv[a*M+Aall[a*M+x]]=x;
  sprintf(fn,"%s/G.bin",dir); f=fopen(fn,"rb"); fseek(f,0,SEEK_END); NG=ftell(f)/M; rewind(f); uint8_t *G=malloc((size_t)NG*M); if(fread(G,1,(size_t)NG*M,f)!=(size_t)NG*M) return 1; fclose(f);
  Gfw5=malloc((size_t)NG*5*M); Ginv5=malloc((size_t)NG*5*M);
  for(long g=0;g<NG;g++){ uint8_t *F=Gfw5+g*5*M, *I=Ginv5+g*5*M; for(int x=0;x<M;x++) F[x]=x; for(int k=1;k<5;k++) for(int x=0;x<M;x++) F[k*M+x]=G[g*M+F[(k-1)*M+x]];
    for(int k=0;k<5;k++) for(int x=0;x<M;x++) I[k*M+F[k*M+x]]=x; }
  /* lexicon */
  H=calloc(1ULL<<HB,8); for(int L=4;L<=16;L++) pre4[L]=calloc(M*M*M*M/8+1,1);
  sprintf(fn,"%s/lex.bin",dir); f=fopen(fn,"rb"); uint8_t rec[17]; long nlex=0;
  while(fread(rec,1,17,f)==17){ int L=rec[0]; int p[16]; for(int i=0;i<L;i++) p[i]=rec[1+i]; hins(hkey(L,p)); nlex++;
    pre1[L][p[0]]=1; if(L>=2) pre2[L][p[0]*M+p[1]]=1; if(L>=3) pre3[L][(p[0]*M+p[1])*M+p[2]]=1;
    if(L>=4){ int i=((p[0]*M+p[1])*M+p[2])*M+p[3]; pre4[L][i>>3]|=1<<(i&7);} }
  fclose(f);
  for (int w2=0; w2<2 && w2<nw; w2++){ int L=lens[w2]; if (L>=5 && L<=16 && !pre5[L]){ pre5[L]=calloc(M*M*M*M*M/8+1,1);
      FILE *f2=fopen(fn,"rb"); while(fread(rec,1,17,f2)==17){ if(rec[0]!=L) continue; int i=((((int)rec[1]*M+rec[2])*M+rec[3])*M+rec[4])*M+rec[5]; pre5[L][i>>3]|=1<<(i&7);} fclose(f2);} }
  for(int L=1;L<=16;L++){ if(L<2) memset(pre2[L],1,M*M); if(L<3) memset(pre3[L],1,M*M*M); }
  LM=malloc(sizeof(int16_t)*V*V*V*V); sprintf(fn,"%s/lm16.bin",dir); f=fopen(fn,"rb"); if(fread(LM,2,V*V*V*V,f)!=V*V*V*V) return 1; fclose(f);
  /* lists */
  int nb, ns, ng; int *BL, *SL, *GL;
  if (bl) BL=readlist(bl,&nb); else { nb=NA; BL=malloc(nb*sizeof(int)); for(int i=0;i<nb;i++) BL[i]=i; }
  if (sl) SL=readlist(sl,&ns); else { ns=NA; SL=malloc(ns*sizeof(int)); for(int i=0;i<ns;i++) SL[i]=i; }
  if (gl) GL=readlist(gl,&ng); else { ng=NG; GL=malloc(ng*sizeof(int)); for(int i=0;i<ng;i++) GL[i]=i; }
  int nth = omp_get_max_threads();
  fprintf(stderr,"text %s: %d words %d runes; prefix %d words %d runes; word0 len %d word1 len %d; |base|=%d |g|=%d |sigma|=%d lexicon %ld threads %d\n",
          argv[1], nw, N, nwp, nr, lens[0], lens[1], nb, ng, ns, nlex, nth);
  /* ---------- stage A ---------- */
  double t0 = omp_get_wtime(); L0g = lens[0]; int L0 = L0g;
  capSV = 1<<20; SV = malloc(capSV*sizeof(Surv));
  long long nA = (long long)nb*ng;
  for(int j=0;j<L0;j++) eqg[j] = j>0 && cip[j]==cip[j-1];
  int simd = (L0 >= 4 && L0 <= 16 && !eqg[2] && !eqg[3] && !getenv("KW_SCALAR"));
  if (!simd){
    const int GBLK = 4096;
    for (int g0 = 0; g0 < ng; g0 += GBLK){
      int g1 = g0+GBLK < ng ? g0+GBLK : ng;
      #pragma omp parallel for schedule(dynamic,256)
      for (int bi = 0; bi < nb; bi++){
        int b = BL[bi]; const uint8_t *binv = Ainv + (size_t)b*M; int x[64]; for(int j=0;j<L0;j++) x[j]=binv[cip[j]];
        int eqany = 0; for(int j=1;j<L0&&j<4;j++) eqany |= eqg[j];
        const uint8_t *P4 = pre4[L0 >= 4 && L0 <= 16 ? L0 : 4];
        for (int gi = g0; gi < g1; gi++){
          int g = GL[gi]; const uint8_t *I = Ginv5 + (size_t)g*5*M;
          if (L0 >= 4 && L0 <= 16 && !eqany){
            int q0 = x[0], q1 = I[M+x[1]], q2 = I[2*M+x[2]], q3 = I[3*M+x[3]];
            int amb = (q1==q0) | (q2==q1) | (q3==q2);
            int idx = ((q0*M+q1)*M+q2)*M+q3;
            if (!amb && !((P4[idx>>3]>>(idx&7))&1)) continue;
          }
          exactA(b, g, x);
        }
      }
    }
  } else {
    /* AVX-512 VBMI driver: bases grouped by (x0,x1); per g and group the plaintext p0,p1 are scalars and
       p2,p3 for 64 bases come from vpermb; the 4-prefix test uses a per-(p0,p1) table of 29-bit masks. */
    int ngrp = M*M; int *gcnt = calloc(ngrp+1, sizeof(int)), *gst = calloc(ngrp+1, sizeof(int));
    for (int bi=0; bi<nb; bi++){ const uint8_t *bv = Ainv + (size_t)BL[bi]*M; gcnt[bv[cip[0]]*M + bv[cip[1]]]++; }
    for (int k=1;k<=ngrp;k++) gst[k] = gst[k-1] + gcnt[k-1];
    int *pos = calloc(ngrp, sizeof(int)); int *gb = malloc(nb*sizeof(int)); uint8_t *X2 = malloc(nb+64), *X3 = malloc(nb+64), *XA = malloc((size_t)nb*L0);
    for (int bi=0; bi<nb; bi++){ const uint8_t *bv = Ainv + (size_t)BL[bi]*M; int k = bv[cip[0]]*M + bv[cip[1]]; int i = gst[k] + pos[k]++;
      gb[i] = BL[bi]; X2[i] = bv[cip[2]]; X3[i] = bv[cip[3]]; for(int j=0;j<L0;j++) XA[(size_t)i*L0+j] = bv[cip[j]]; }
    uint32_t *MT = calloc((size_t)M*M*32, 4); const uint8_t *P4 = pre4[L0];
    for (int a0=0;a0<M;a0++) for(int a1=0;a1<M;a1++) for(int a2=0;a2<M;a2++){ uint32_t m=0; for(int a3=0;a3<M;a3++){ int idx=((a0*M+a1)*M+a2)*M+a3; if((P4[idx>>3]>>(idx&7))&1) m|=1u<<a3; } MT[(a0*M+a1)*32+a2]=m; }
    long long nExactL = 0;
    #pragma omp parallel for schedule(dynamic,64) reduction(+:nExactL)
    for (int gi = 0; gi < ng; gi++){
      int g = GL[gi]; const uint8_t *I = Ginv5 + (size_t)g*5*M;
      __m512i Iv[5]; for (int k=0;k<5;k++) Iv[k] = _mm512_maskz_loadu_epi8((1ULL<<M)-1, I + k*M);
      for (int key = 0; key < ngrp; key++){
        int n = gcnt[key]; if (!n) continue;
        int x0 = key / M, x1 = key % M;
        int np = 0, P1[2], T2[2];
        int q1 = I[M + x1];
        if (!eqg[1]) { P1[np]=q1; T2[np]=2; np++; }
        if (q1 == x0) { P1[np]=I[2*M + x1]; T2[np]=3; np++; }       /* D-reading at j=1 (skip) */
        int keep[2], nk=0; for (int pi=0;pi<np;pi++) if (pre2[L0][x0*M+P1[pi]]) keep[nk++]=pi;
        if (!nk) continue;
        int s0 = gst[key];
        for (int c = 0; c < n; c += 64){
          int m = n - c < 64 ? n - c : 64; __mmask64 lm = m == 64 ? ~0ULL : ((1ULL<<m)-1);
          __m512i x2v = _mm512_maskz_loadu_epi8(lm, X2 + s0 + c), x3v = _mm512_maskz_loadu_epi8(lm, X3 + s0 + c);
          __mmask64 cand = 0;
          for (int kk=0; kk<nk; kk++){
            int pi = keep[kk]; int t2 = T2[pi] % 5, t3 = (T2[pi]+1) % 5; int p1 = P1[pi];
            __m512i q2 = _mm512_permutexvar_epi8(x2v, Iv[t2]), q3 = _mm512_permutexvar_epi8(x3v, Iv[t3]);
            int t4 = (T2[pi]+2) % 5, t5 = (T2[pi]+3) % 5;
            __m512i q2d = _mm512_permutexvar_epi8(x2v, Iv[t3]);           /* D at j=2: clock t2+1 */
            __m512i q3d = _mm512_permutexvar_epi8(x3v, Iv[t4]);           /* then N at j=3 with clock t2+2 */
            __m512i q3n_d = _mm512_permutexvar_epi8(x3v, Iv[t4]);         /* N path, D at j=3: clock t3+1 = t2+2 */
            __mmask64 amb2 = _mm512_cmpeq_epi8_mask(q2, _mm512_set1_epi8((char)p1));
            __mmask64 amb3 = _mm512_cmpeq_epi8_mask(q3, q2);
            __mmask64 ambDD = amb2 & _mm512_cmpeq_epi8_mask(q3d, q2d);   /* D,D: rare, sent to exact */
            (void)t5;
            const uint32_t *mt = MT + (x0*M + p1)*32; __m512i mlo = _mm512_loadu_si512(mt), mhi = _mm512_loadu_si512(mt+16);
            __m512i one = _mm512_set1_epi32(1);
            #define OK4(Q2,Q3,OUT) { __mmask64 _o=0; \
              for (int _h=0; _h<4; _h++){ __m128i _a = _mm512_extracti32x4_epi32(Q2,0), _b = _mm512_extracti32x4_epi32(Q3,0); \
                if(_h==1){_a=_mm512_extracti32x4_epi32(Q2,1);_b=_mm512_extracti32x4_epi32(Q3,1);} \
                if(_h==2){_a=_mm512_extracti32x4_epi32(Q2,2);_b=_mm512_extracti32x4_epi32(Q3,2);} \
                if(_h==3){_a=_mm512_extracti32x4_epi32(Q2,3);_b=_mm512_extracti32x4_epi32(Q3,3);} \
                __m512i qa=_mm512_cvtepu8_epi32(_a), qb=_mm512_cvtepu8_epi32(_b); __m512i mm=_mm512_permutex2var_epi32(mlo,qa,mhi); \
                __mmask16 _t=_mm512_test_epi32_mask(_mm512_srlv_epi32(mm,qb),one); _o |= ((__mmask64)_t)<<(16*_h); } OUT=_o; }
            __mmask64 okNN, okND = 0, okDN = 0;
            OK4(q2, q3, okNN)
            if (amb3 & lm) { OK4(q2, q3n_d, okND) okND &= amb3; }
            if (amb2 & lm) { OK4(q2d, q3d, okDN) okDN &= amb2; }
            #undef OK4
            __mmask64 ok = okNN | okND | okDN | ambDD, amb = 0;
            cand |= (ok | amb) & lm;
          }
          while (cand){
            int l = __builtin_ctzll(cand); cand &= cand-1;
            int b = gb[s0 + c + l]; const uint8_t *xa = XA + (size_t)(s0+c+l)*L0; int x[64]; for(int j=0;j<L0;j++) x[j]=xa[j];
            nExactL++; exactA(b, g, x);
          }
        }
      }
    }
    free(gcnt); free(gst); free(pos); free(gb); free(X2); free(X3); free(XA); free(MT); nExact = nExactL;
  }
  double tA = omp_get_wtime()-t0;
  fprintf(stderr,"stage A: %lld (base,g) pairs in %.1fs = %.2e /s; exact DFS calls %lld (%.2e); survivors %lld (%.2e)\n", nA, tA, nA/tA, nExact, (double)nExact/nA, nSV, (double)nSV/nA);
  /* ---------- stage B ---------- */
  char ofn[1100]; sprintf(ofn,"%s.txt",out); FILE *fo=fopen(ofn,"w");
  fprintf(fo,"# text %s words %d runes %d prefix_words %d prefix_runes %d |base| %d |g| %d |sigma| %d stageA_pairs %lld survivors %lld stageA_s %.1f\n",
          argv[1], nw, N, nwp, nr, nb, ng, ns, nA, nSV, tA);
  for (int mode=0; mode<3; mode++){
    if (!(modes & (1<<mode))) continue;
    double t1 = omp_get_wtime();
    Heap *heaps = calloc(nth, sizeof(Heap)); for(int i=0;i<nth;i++){ heaps[i].h=malloc(K*sizeof(Cand)); heaps[i].n=0; }
    long long nend=0, nw1=0, ntr=0;
    int nsig = (mode==2) ? 1 : ns;
    #pragma omp parallel reduction(+:nend,nw1,ntr)
    {
      Ctx *cx = malloc(sizeof(Ctx)); cx->hp = &heaps[omp_get_thread_num()]; cx->mode = mode; cx->nend=0; cx->nw1=0;
      #pragma omp for schedule(dynamic,1)
      for (long long k = 0; k < nSV; k++){
        Surv *s = &SV[k]; cx->b=s->b; cx->g=s->g; cx->gi = Ginv5 + (size_t)s->g*5*M; cx->gf = Gfw5 + (size_t)s->g*5*M;
        const uint8_t *binv0 = Ainv + (size_t)s->b*M;
        int p0[64]; for(int j=0;j<L0;j++) p0[j]=s->p0[j];
        int L1 = lens[1], e0 = (s->t1+4)%5; int y[64], yprev, eq1any = 0;
        for (int j=0;j<L1 && j<64;j++){ y[j] = cx->gi[e0*M + binv0[cip[st[1]+j]]]; if (j<4) eq1any |= (cip[st[1]+j] == cip[st[1]+j-1]); }
        yprev = cx->gi[e0*M + binv0[cip[st[1]-1]]];
        const uint8_t *P41 = pre4[L1 >= 4 && L1 <= 16 ? L1 : 4];
        int need[64], nneed = 0; { int seen[M]={0}; for (int i=st[1]-1;i<st[1]+L1;i++){ int x=cip[i]; if(!seen[x]){seen[x]=1; need[nneed++]=x;} } }
        for (int si = 0; si < nsig; si++){
          cx->s = (mode==2) ? -1 : SL[si]; cx->si = (mode==2) ? binv0 : Ainv + (size_t)SL[si]*M;
          if (mode != 2 && L1 >= 4 && L1 <= 16 && !eq1any){
            const uint8_t *si = cx->si; int tt = (mode==1) ? 0 : s->t1;
            int z0 = si[y[0]], zp = si[yprev];
            int q0 = cx->gi[tt*M+z0], q1 = cx->gi[((tt+1)%5)*M+si[y[1]]], q2 = cx->gi[((tt+2)%5)*M+si[y[2]]], q3 = cx->gi[((tt+3)%5)*M+si[y[3]]];
            int amb = (cx->gi[M+z0]==zp) | (q1==q0) | (q2==q1) | (q3==q2);
            int idx = ((q0*M+q1)*M+q2)*M+q3;
            if (!amb && !((P41[idx>>3]>>(idx&7))&1)) { ntr++; continue; }
          }
          uint8_t nb1[M];
          if (mode==2) { memcpy(nb1, binv0, M); cx->lazy = 0; }
          else { const uint8_t *ge = cx->gi + e0*M; for (int r=0;r<nneed;r++){ int x=need[r]; nb1[x] = cx->si[ ge[ binv0[x] ] ]; } cx->lazy = 1; cx->b0inv = binv0; cx->e0 = e0; }
          memcpy(cx->plain, p0, sizeof(int)*L0);
          if (nwp == 1){ Cand c={s->sc, s->b, s->g, cx->s, mode, 0}; hpush(cx->hp,c); continue; }
          dfs_word(cx, 1, nb1, mode==1 ? 0 : s->t1, s->sc);
          ntr++;
        }
      }
      nend += cx->nend; nw1 += cx->nw1; free(cx);
    }
    /* merge heaps */
    Heap all; all.h = malloc(K*sizeof(Cand)); all.n=0;
    for (int i=0;i<nth;i++) for(int j=0;j<heaps[i].n;j++) hpush(&all, heaps[i].h[j]);
    /* sort descending */
    for (int i=0;i<all.n;i++) for(int j=i+1;j<all.n;j++) if (all.h[j].score>all.h[i].score){ Cand t=all.h[i]; all.h[i]=all.h[j]; all.h[j]=t; }
    double tB = omp_get_wtime()-t1;
    fprintf(stderr,"mode %d stage B: %lld (survivor,sigma) trials in %.1fs = %.2e /s; word1 lexicon pass %lld; reached prefix end %lld; kept %d\n", mode, ntr, tB, ntr/tB, nw1, nend, all.n);
    fprintf(fo,"# mode %d stageB_trials %lld stageB_s %.1f word1_pass %lld reached_end %lld total_keys %.4e\n", mode, ntr, tB, nw1, nend, (double)nA*(mode==2?1:ns));
    for (int i=0;i<all.n;i++){ int dup=0; for(int j=0;j<i;j++) if(all.h[j].b==all.h[i].b&&all.h[j].g==all.h[i].g&&all.h[j].s==all.h[i].s){dup=1;break;} if(dup) continue;
      fprintf(fo,"%d %d %d %d %d %.4f\n", all.h[i].mode, all.h[i].b, all.h[i].g, all.h[i].s, all.h[i].score, all.h[i].score/1000.0/(nr+nwp)); }
  }
  fclose(fo);
  return 0;
}
