#include <stdlib.h>
#include <string.h>
#include <stdint.h>
/* Chain-model plaintext autokey decoders. D: increments (0..28), aligned with runes 1..n-1.
   seg_start: array of segment starts (page restarts) of length nseg+1 (last = n).
   wstart: word-start flags per position (1 if this position begins a new word), used by mode 1/2.
   mode 0: letter autokey lag L: k_i = sgn*gt[p_{i-L}]  (seed = L initial plaintext values, brute force 29^L)
   mode 1: previous-word-sum autokey: k for all positions of word w = sgn*ht[min(sum of decoded plaintext primes of word w-1, HMAX)] ; seed = initial k in 0..28
   mode 2: running-total autokey: k_i = sgn*ht[cum_{i-1} mod HMAX] where cum = sum primes of decoded plaintext since segment start + seed; seed in 0..28
   form 0 additive (mod 28), x=(D-1-k) mod 28, p=x (map 0) or 27-x (map 1); D==0 -> p=28
   form 1 multiplicative: x=D*inv(kk) mod 29 where kk=k mod 29 ; if kk==0 -> skip symbol (count nothing) and p=0 ; p = x-1 (x>=1), EA when x==0
   Return for each seed: counts-based IoC*29 (normalised) and nvalid. */
static int inv29[29]; static int init=0;
static void ini(void){ if(init) return; init=1; for(int a=1;a<29;a++) for(int b=1;b<29;b++) if((a*b)%29==1) inv29[a]=b; }
static const int PR[29]={2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109};
#define HMAX 812000
static inline int mod(int a,int m){ int r=a%m; return r<0?r+m:r; }
/* decode one segment [a,b), return counts */
static void dec_seg(const uint8_t*D,const uint8_t*wstart,int a,int b,int mode,int lag,const int*gt,const int*ht,int sgn,int map,int form,const int*seed,int nseed,int*cnt,int*nv){
  int hist[8]; /* last plaintext values, hist[0]=most recent */
  int k=0; int wsum=0; int curk=0; int cum=0;
  if(mode==0){ for(int t=0;t<lag;t++) hist[t]=seed[t]; }
  else if(mode==1){ curk=seed[0]; wsum=0; }
  else { cum=seed[0]; }
  for(int i=a;i<b;i++){
    if(mode==0){ k=sgn*gt[hist[lag-1]]; }
    else if(mode==1){ if(wstart[i] && i>a){ int s=wsum>=HMAX?HMAX-1:wsum; curk=sgn*ht[s]; wsum=0; } k=curk; }
    else { k=sgn*ht[cum%HMAX]; }
    int x,p,sym;
    if(form==0){
      if(D[i]==0){ p=28; sym=28; }
      else { x=mod(D[i]-1-k,28); p= map? 27-x : x; sym=x; }
      cnt[sym]++; (*nv)++;
    } else {
      int kk=mod(k,29);
      if(kk==0){ p=0; }
      else { x=(D[i]*inv29[kk])%29; sym=x; p= x==0?28:(map? 28-x : x-1); cnt[sym]++; (*nv)++; }
    }
    if(mode==0){ for(int t=lag-1;t>0;t--) hist[t]=hist[t-1]; hist[0]=p; }
    else if(mode==1){ wsum+=PR[p]; }
    else { cum+=PR[p]; if(cum>=100000000) cum%=HMAX; }
  }
}
/* enumerate seeds for a segment, return best normalised IoC (and seed index) */
void best_seed(const uint8_t*D,const uint8_t*wstart,int a,int b,int mode,int lag,const int*gt,const int*ht,int sgn,int map,int form,double*best_ioc,long*best_seed_id,int*best_nv){
  ini();
  int nseed_total = mode==0 ? 1 : 29; if(mode==0) for(int t=0;t<lag;t++) nseed_total*=29;
  double bi=-1; long bs=-1; int bn=0;
  for(long sid=0;sid<nseed_total;sid++){
    int seed[8]; long s=sid; if(mode==0){ for(int t=0;t<lag;t++){ seed[t]=s%29; s/=29; } } else seed[0]=(int)sid;
    int cnt[29]; memset(cnt,0,sizeof(cnt)); int nv=0;
    dec_seg(D,wstart,a,b,mode,lag,gt,ht,sgn,map,form,seed,1,cnt,&nv);
    if(nv<2) continue;
    double sum=0; for(int t=0;t<29;t++) sum+=(double)cnt[t]*(cnt[t]-1);
    double ioc=29.0*sum/((double)nv*(nv-1));
    if(ioc>bi){bi=ioc;bs=sid;bn=nv;}
  }
  *best_ioc=bi; *best_seed_id=bs; *best_nv=bn;
}
/* decode with given seed id into output arrays (plaintext symbols) for inspection */
void decode_out(const uint8_t*D,const uint8_t*wstart,int a,int b,int mode,int lag,const int*gt,const int*ht,int sgn,int map,int form,long sid,uint8_t*out){
  ini();
  int seed[8]; long s=sid; if(mode==0){ for(int t=0;t<lag;t++){ seed[t]=s%29; s/=29; } } else seed[0]=(int)sid;
  /* reimplement quickly via dec_seg-like loop storing p */
  int hist[8]; int k=0,wsum=0,curk=0,cum=0;
  if(mode==0){ for(int t=0;t<lag;t++) hist[t]=seed[t]; } else if(mode==1){ curk=seed[0]; } else cum=seed[0];
  for(int i=a;i<b;i++){
    if(mode==0) k=sgn*gt[hist[lag-1]];
    else if(mode==1){ if(wstart[i]&&i>a){ int s2=wsum>=HMAX?HMAX-1:wsum; curk=sgn*ht[s2]; wsum=0;} k=curk; }
    else k=sgn*ht[cum%HMAX];
    int x,p;
    if(form==0){ if(D[i]==0) p=28; else { x=mod(D[i]-1-k,28); p= map?27-x:x; } }
    else { int kk=mod(k,29); if(kk==0) p=0; else { x=(D[i]*inv29[kk])%29; p= x==0?28:(map?28-x:x-1);} }
    out[i]=p;
    if(mode==0){ for(int t=lag-1;t>0;t--) hist[t]=hist[t-1]; hist[0]=p; } else if(mode==1) wsum+=PR[p]; else { cum+=PR[p]; if(cum>=100000000) cum%=HMAX; }
  }
}
