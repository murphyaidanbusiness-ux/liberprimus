/* mk_sa: simulated annealing key search for the M_K cipher family.
   c_j = A_{t mod K}[p_j], t starts at per-word phase phi_w; skip rule:
     skip=0 none; skip=1 'adv' (Oosterhof): if emission == previous cipher rune, t+=1 and recompute once,
     extra step persists in the word; skip=2 'redraw': only this position uses t+1.
   Per-word phase and skip branches are PROFILED OUT: word score = max over phi (or the known phi) and over
   ambiguous skip branches of the word-internal 4-gram log-prob of the decryption.
   Parameters: free mode: K free alphabets; tied mode: A_k = base o g^k with g of order 5 (fixed-point
   count preserved; g moves = conjugation by a transposition).
   Usage: mk_sa inst lm.bin K skip tied knownA knownPhase iters restarts seed T0 [out_prefix]
   inst format: nw / lens... / cipher... / plain... (or -1s) / truePhase... / trueA (K*29) or base(29) g(29) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
#define V 30
#define B 29
#define MAXN 20000
#define MAXW 4000
#define MAXK 8
static float *LM;
static int nw, N, K, SKIP, TIED, KNOWNA, KNOWNPH;
static int len_[MAXW], st_[MAXW], ciph[MAXN], plain[MAXN], tph[MAXW], prevc[MAXW];
static int A[MAXK][29], Ai[MAXK][29], base_[29], g_[29], tA[MAXK][29], tbase[29], tg[29];
static double wsc[MAXW], nsc[MAXW];
static int bph[MAXW];
static int *touch[29], ntouch[29];
static uint64_t rs;
static inline uint64_t rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double urand(void){ return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

static double best_word; static int bestbuf[64], curbuf[64]; static int nbranch;
static void dfs(int w, int j, int t, int prev, int a, int b, int c, double sc){
  int L = len_[w];
  if (j == L){ sc += LM[((a*V+b)*V+c)*V+B]; if (sc > best_word){ best_word = sc; memcpy(bestbuf, curbuf, L*sizeof(int)); } return; }
  int cc = ciph[st_[w]+j];
  int pN = Ai[t%K][cc];
  if (!SKIP){ curbuf[j]=pN; dfs(w,j+1,t+1,cc,b,c,pN,sc+LM[((a*V+b)*V+c)*V+pN]); return; }
  int okN = (cc != prev);
  int pD = Ai[(t+1)%K][cc];
  int okD = (A[t%K][pD] == prev);
  if (okN){ curbuf[j]=pN; dfs(w,j+1,t+1,cc,b,c,pN,sc+LM[((a*V+b)*V+c)*V+pN]); }
  if (okD && (!okN || nbranch < 16)){ if (okN) nbranch++; curbuf[j]=pD;
     dfs(w,j+1,(SKIP==1)?t+2:t+1,cc,b,c,pD,sc+LM[((a*V+b)*V+c)*V+pD]); }
  if (!okN && !okD){ curbuf[j]=pN; dfs(w,j+1,t+1,cc,b,c,pN,sc-6.0+LM[((a*V+b)*V+c)*V+pN]); }
}
static double score_word(int w, int *phout, int *pbuf){
  double best = -1e30; int bp = 0;
  int p0 = KNOWNPH ? tph[w] : 0, p1 = KNOWNPH ? tph[w]+1 : K;
  for (int ph = p0; ph < p1; ph++){
    best_word = -1e30; nbranch = 0;
    dfs(w, 0, ph, prevc[w], B, B, B, 0.0);
    if (best_word > best){ best = best_word; bp = ph; if (pbuf) memcpy(pbuf, bestbuf, len_[w]*sizeof(int)); }
  }
  if (phout) *phout = bp; return best;
}
static void build_tied(void){
  int gp[29]; for (int i=0;i<29;i++) gp[i]=i;
  for (int k=0;k<K;k++){ for (int p=0;p<29;p++){ A[k][p]=base_[gp[p]]; Ai[k][A[k][p]]=p; }
    int ng[29]; for (int p=0;p<29;p++) ng[p]=g_[gp[p]]; memcpy(gp,ng,sizeof ng); }
}
static void inv_all(void){ for (int k=0;k<K;k++) for (int p=0;p<29;p++) Ai[k][A[k][p]]=p; }
static double total(void){ double s=0; for (int w=0;w<nw;w++){ wsc[w]=score_word(w,&bph[w],NULL); s+=wsc[w]; } return s; }
static double accuracy(void){
  int ok=0, tot=0, buf[64];
  for (int w=0;w<nw;w++){ int ph; score_word(w,&ph,buf); for (int j=0;j<len_[w];j++){ if (plain[st_[w]+j]>=0){ tot++; ok += (buf[j]==plain[st_[w]+j]); } } }
  return tot? (double)ok/tot : -1;
}
int main(int argc, char **argv){
  if (argc < 12){ fprintf(stderr,"usage\n"); return 1; }
  FILE *f = fopen(argv[1],"r"); K=atoi(argv[3]); SKIP=atoi(argv[4]); TIED=atoi(argv[5]); KNOWNA=atoi(argv[6]); KNOWNPH=atoi(argv[7]);
  long iters=atol(argv[8]); int restarts=atoi(argv[9]); rs = 0x9E3779B97F4A7C15ULL ^ (uint64_t)atoll(argv[10])*2654435761ULL; double T0=atof(argv[11]);
  const char *outp = argc > 12 ? argv[12] : NULL;
  if (fscanf(f,"%d",&nw)!=1) return 2; N=0;
  for (int w=0;w<nw;w++){ fscanf(f,"%d",&len_[w]); st_[w]=N; N+=len_[w]; }
  for (int i=0;i<N;i++) fscanf(f,"%d",&ciph[i]);
  for (int i=0;i<N;i++) fscanf(f,"%d",&plain[i]);
  for (int w=0;w<nw;w++) fscanf(f,"%d",&tph[w]);
  if (TIED){ for (int i=0;i<29;i++) fscanf(f,"%d",&tbase[i]); for (int i=0;i<29;i++) fscanf(f,"%d",&tg[i]); }
  else for (int k=0;k<K;k++) for (int i=0;i<29;i++) fscanf(f,"%d",&tA[k][i]);
  fclose(f);
  LM = malloc(sizeof(float)*V*V*V*V); f=fopen(argv[2],"rb"); fread(LM,sizeof(float),V*V*V*V,f); fclose(f);
  for (int w=0;w<nw;w++) prevc[w] = w ? ciph[st_[w]-1] : -1;
  /* touch lists: word w is touched by cipher symbol x if x in w or x == prevc[w] */
  for (int x=0;x<29;x++){ touch[x]=malloc(sizeof(int)*nw); ntouch[x]=0; }
  for (int w=0;w<nw;w++){ int seen[29]={0}; for (int j=0;j<len_[w];j++) seen[ciph[st_[w]+j]]=1; if (prevc[w]>=0) seen[prevc[w]]=1;
    for (int x=0;x<29;x++) if (seen[x]) touch[x][ntouch[x]++]=w; }
  int *stamp = calloc(nw,sizeof(int)), *aff = malloc(sizeof(int)*nw); int stampv=0;
  double gbest=-1e30;
  /* truth score */
  if (TIED){ memcpy(base_,tbase,sizeof base_); memcpy(g_,tg,sizeof g_); build_tied(); } else { memcpy(A,tA,sizeof A); inv_all(); }
  double tsc = total(); double tacc = accuracy();
  printf("TRUTH score %.1f acc %.4f\n", tsc, tacc); fflush(stdout);
  for (int r=0;r<restarts;r++){
    clock_t c0=clock();
    if (!KNOWNA){
      if (TIED){ int pts[29]; for(int i=0;i<29;i++) pts[i]=i; for(int i=28;i>0;i--){int j=rnd()%(i+1);int t=pts[i];pts[i]=pts[j];pts[j]=t;}
        memcpy(base_,pts,sizeof pts);
        /* g: random conjugate of the TRUE cycle type (fixed points count), since the cycle type is cheap to enumerate */
        int nfix=0; for(int i=0;i<29;i++) nfix+=(tg[i]==i);
        for(int i=28;i>0;i--){int j=rnd()%(i+1);int t=pts[i];pts[i]=pts[j];pts[j]=t;}
        for(int i=0;i<29;i++) g_[i]=i;
        for(int k=nfix;k+5<=29;k+=5) for(int i=0;i<5;i++) g_[pts[k+i]]=pts[k+(i+1)%5];
        if (KNOWNA==0 && argc>13 && atoi(argv[13])==1) memcpy(g_,tg,sizeof g_); /* known g */
        build_tied();
      } else { for (int k=0;k<K;k++){ int pts[29]; for(int i=0;i<29;i++) pts[i]=i; for(int i=28;i>0;i--){int j=rnd()%(i+1);int t=pts[i];pts[i]=pts[j];pts[j]=t;} memcpy(A[k],pts,sizeof pts);} inv_all(); }
    }
    double cur = total(); double best = cur; long acc_moves=0;
    int knowng = (argc>13 && atoi(argv[13])==1);
    for (long it=0; it<iters && !KNOWNA; it++){
      double T = T0 * (1.0 - (double)it/iters) + 1e-3;
      int gmove = TIED && !knowng && (rnd()%10==0);
      int x, y, a=0, i0=0, j0=0; int na=0; stampv++;
      int saveA[MAXK][29], saveAi[MAXK][29], saveb[29], saveg[29];
      if (TIED){ memcpy(saveb,base_,sizeof saveb); memcpy(saveg,g_,sizeof saveg); memcpy(saveA,A,sizeof saveA); memcpy(saveAi,Ai,sizeof saveAi); }
      if (gmove){
        do { i0=rnd()%29; j0=rnd()%29; } while (i0==j0);
        /* g' = tau g tau, tau=(i0 j0) */
        int ng[29]; for (int p=0;p<29;p++){ int q = p==i0?j0:(p==j0?i0:p); int r2=g_[q]; ng[p]= r2==i0?j0:(r2==j0?i0:r2); }
        memcpy(g_,ng,sizeof ng); build_tied();
        for (int w=0;w<nw;w++) aff[na++]=w;
      } else {
        do { x=rnd()%29; y=rnd()%29; } while (x==y);
        if (TIED){ /* swap base entries holding cipher symbols x,y */
          int ix=-1, iy=-1; for (int i=0;i<29;i++){ if (base_[i]==x) ix=i; if (base_[i]==y) iy=i; }
          base_[ix]=y; base_[iy]=x; build_tied();
        } else { a = rnd()%K; int u=Ai[a][x], v=Ai[a][y]; Ai[a][x]=v; Ai[a][y]=u; A[a][u]=y; A[a][v]=x; }
        for (int q=0;q<ntouch[x];q++){ int w=touch[x][q]; if (stamp[w]!=stampv){ stamp[w]=stampv; aff[na++]=w; } }
        for (int q=0;q<ntouch[y];q++){ int w=touch[y][q]; if (stamp[w]!=stampv){ stamp[w]=stampv; aff[na++]=w; } }
      }
      double d=0; for (int q=0;q<na;q++){ int w=aff[q]; nsc[w]=score_word(w,NULL,NULL); d += nsc[w]-wsc[w]; }
      if (d >= 0 || urand() < exp(d/T)){ cur += d; acc_moves++; for (int q=0;q<na;q++) wsc[aff[q]]=nsc[aff[q]]; if (cur>best) best=cur; }
      else { /* revert */
        if (TIED){ memcpy(base_,saveb,sizeof saveb); memcpy(g_,saveg,sizeof saveg); memcpy(A,saveA,sizeof saveA); memcpy(Ai,saveAi,sizeof saveAi); }
        else { int u=Ai[a][x], v=Ai[a][y]; Ai[a][x]=v; Ai[a][y]=u; A[a][u]=y; A[a][v]=x; }
      }
      if (it % (iters/10+1) == 0 && getenv("VERBOSE")) { printf("  it %ld T %.2f cur %.1f\n", it, T, cur); fflush(stdout); }
    }
    /* final greedy polish: steepest single swaps until no improvement (free mode only) */
    cur = total();
    double secs = (double)(clock()-c0)/CLOCKS_PER_SEC;
    double acc = accuracy();
    printf("RESTART %d score %.1f (truth %.1f) acc %.4f  moves/s %.0f  secs %.1f\n", r, cur, tsc, acc, secs>0? iters/secs:0, secs); fflush(stdout);
    if (cur > gbest && outp){ gbest = cur; char fn[512]; snprintf(fn,sizeof fn,"%s.dec",outp); FILE *o=fopen(fn,"w"); int buf[64];
      for (int w=0;w<nw;w++){ int ph; score_word(w,&ph,buf); fprintf(o,"%d:",ph); for (int j=0;j<len_[w];j++) fprintf(o," %d",buf[j]); fprintf(o,"\n"); }
      fclose(o); snprintf(fn,sizeof fn,"%s.key",outp); o=fopen(fn,"w"); for (int k=0;k<K;k++){ for(int p=0;p<29;p++) fprintf(o,"%d ",A[k][p]); fprintf(o,"\n"); } fclose(o); }
  }
  return 0;
}
