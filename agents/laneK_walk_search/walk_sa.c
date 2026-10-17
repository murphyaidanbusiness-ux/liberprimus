/* walk_sa: SA over sigma for Oosterhof's doublet-dodge walk, GENEROUS ORACLE setting:
   g and base0 known; the true clock (incl. every skip) is given to the solver, so decryption under a
   candidate sigma is deterministic: p_j = g^{-k_j}( base_w^{-1}(c_j) ),
   base_{w+1} = base_w o g^{e_w} o sigma, e_w = (clock at end of word w - 1) mod 5 (true values given).
   Score = word-internal 4-gram log-prob of the first `pref` words (pref=0: all).
   Usage: walk_sa inst lm.bin iters restarts seed T0 pref init_dist(-1 random | m transpositions from truth)
   inst: nw / lens / cipher / plain / k_j (clock mod 5 per rune) / e_w per word / base0 / g / sigma */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
#define V 30
#define B 29
static float *LM; static int nw, N, len_[4000], st_[4000], ciph[20000], plain[20000], kk[20000], ew[4000];
static int base0[29], g[29], sig[29], tsig[29], gp[5][29], gpi[5][29];
static uint64_t rs; static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static inline double urand(void){ return (rnd()>>11)*(1.0/9007199254740992.0); }
static int dec[20000];
static double score(int pref, int *nok){
  int base[29], bi[29], t[29]; memcpy(base, base0, sizeof base); double s=0; int ok=0;
  int W = pref>0 && pref<nw ? pref : nw;
  for (int w=0; w<W; w++){
    for (int i=0;i<29;i++) bi[base[i]]=i;
    int a=B,b=B,c=B;
    for (int j=0;j<len_[w];j++){ int i=st_[w]+j; int p = gpi[kk[i]][bi[ciph[i]]]; dec[i]=p; ok += (p==plain[i]);
      s += LM[((a*V+b)*V+c)*V+p]; a=b; b=c; c=p; }
    s += LM[((a*V+b)*V+c)*V+B];
    for (int i=0;i<29;i++) t[i] = base[gp[ew[w]][sig[i]]];   /* base o g^e o sigma */
    memcpy(base, t, sizeof t);
  }
  if (nok) *nok = ok; return s;
}
int main(int argc, char **argv){
  FILE *f=fopen(argv[1],"r"); long iters=atol(argv[3]); int restarts=atoi(argv[4]); rs=0x9E3779B97F4A7C15ULL^((uint64_t)atoll(argv[5])*2654435761ULL);
  double T0=atof(argv[6]); int pref=atoi(argv[7]); int idist=atoi(argv[8]);
  fscanf(f,"%d",&nw); N=0; for(int w=0;w<nw;w++){ fscanf(f,"%d",&len_[w]); st_[w]=N; N+=len_[w]; }
  for(int i=0;i<N;i++) fscanf(f,"%d",&ciph[i]); for(int i=0;i<N;i++) fscanf(f,"%d",&plain[i]);
  for(int i=0;i<N;i++) fscanf(f,"%d",&kk[i]); for(int w=0;w<nw;w++) fscanf(f,"%d",&ew[w]);
  for(int i=0;i<29;i++) fscanf(f,"%d",&base0[i]); for(int i=0;i<29;i++) fscanf(f,"%d",&g[i]); for(int i=0;i<29;i++) fscanf(f,"%d",&tsig[i]);
  fclose(f);
  LM=malloc(sizeof(float)*V*V*V*V); f=fopen(argv[2],"rb"); fread(LM,sizeof(float),V*V*V*V,f); fclose(f);
  for(int i=0;i<29;i++) gp[0][i]=i; for(int k=1;k<5;k++) for(int i=0;i<29;i++) gp[k][i]=g[gp[k-1][i]];
  for(int k=0;k<5;k++) for(int i=0;i<29;i++) gpi[k][gp[k][i]]=i;
  int W = pref>0 && pref<nw ? pref : nw; int nr=0; for(int w=0;w<W;w++) nr+=len_[w];
  memcpy(sig,tsig,sizeof sig); int ok; double ts=score(pref,&ok);
  printf("TRUTH score %.1f acc %.4f (prefix words %d runes %d)\n", ts, (double)ok/nr, W, nr);
  for(int r=0;r<restarts;r++){
    clock_t c0=clock();
    if (idist<0){ for(int i=0;i<29;i++) sig[i]=i; for(int i=28;i>0;i--){int j=rnd()%(i+1);int t=sig[i];sig[i]=sig[j];sig[j]=t;} }
    else { memcpy(sig,tsig,sizeof sig); for(int m=0;m<idist;m++){ int i=rnd()%29,j=rnd()%29; int t=sig[i];sig[i]=sig[j];sig[j]=t; } }
    double cur=score(pref,NULL), best=cur; int bs[29]; memcpy(bs,sig,sizeof bs);
    for(long it=0;it<iters;it++){
      double T=T0*(1.0-(double)it/iters)+1e-3; int i,j; do{i=rnd()%29;j=rnd()%29;}while(i==j);
      int t=sig[i];sig[i]=sig[j];sig[j]=t; double s=score(pref,NULL); double d=s-cur;
      if (d>=0 || urand()<exp(d/T)){ cur=s; if(cur>best){best=cur;memcpy(bs,sig,sizeof bs);} }
      else { t=sig[i];sig[i]=sig[j];sig[j]=t; }
    }
    memcpy(sig,bs,sizeof sig); double s=score(pref,&ok); int nsig=0; for(int i=0;i<29;i++) nsig+=(sig[i]==tsig[i]);
    int okall; memcpy(sig,bs,sizeof sig); score(0,&okall);
    double secs=(double)(clock()-c0)/CLOCKS_PER_SEC;
    printf("RESTART %d init %d best %.1f (truth %.1f) prefix-acc %.4f full-acc %.4f sigma-correct %d/29 evals/s %.0f\n", r, idist, s, ts, (double)ok/nr, (double)okall/N, nsig, iters/secs);
    fflush(stdout);
  }
  return 0;
}
