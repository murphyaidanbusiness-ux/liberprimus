// Full-position crib drag: running-text / keyword / periodicity signatures of key fragments.
// usage: drag stream.bin cribs.txt out.txt Fdelete(0/1) zdump ddump pdump [dumpfile] [nostreamcribfilter]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>
#include <immintrin.h>
#define LMAX 128
#define WMAX 126
#define NMODEL 4
#define NCLS 3
typedef struct { float Z,key; int crib,pos,mt,var,shift,orient,W,al,cls,dict,per,L; int8_t k[LMAX]; } Hit;
static float *Q; static float T3[2][29*29*29];
static uint8_t *bm6[2], *bm8[2];
static const int MOD[2]={29,28};
static float mu[2][WMAX+1], sd_[2][WMAX+1], pft[2][WMAX+1];
static int8_t TLET[2][2][29][29];   // [mi][o][s][v]
static int8_t DIF[2][29][29], NEG[2][29];
static int8_t GFT[112][29][29]; static int8_t ZT[2][29][29]; static int8_t RT[2][29][29];
static uint64_t pw[2][8];
static int n; static uint8_t *c; static int16_t *pg; static int32_t *wd;
static int nwords; static int *wstart,*wlen;
typedef struct { int id,cls,alonly,nw,wl[40],L; uint8_t r[LMAX]; } Crib;
static Crib *cr; static int ncr;
static uint64_t splitmix(uint64_t *x){ uint64_t z=(*x+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31);}
static inline int hbit(const uint8_t *b,uint64_t i){ return (b[i>>3]>>(i&7))&1; }

static void build_tabs(){
  for(int mi=0;mi<2;mi++){ int m=MOD[mi];
    for(int o=0;o<2;o++)for(int s=0;s<29;s++)for(int v=0;v<29;v++){ int a=o?((m-v)%m):v; TLET[mi][o][s][v]=(a+s)%m; }
    for(int a=0;a<29;a++){ NEG[mi][a]=(m-a)%m; for(int b=0;b<29;b++) DIF[mi][a][b]=((b-a)%m+m)%m; }
    pw[mi][0]=1; for(int i=1;i<8;i++) pw[mi][i]=pw[mi][i-1]*m;
  }
  int inv[29]; for(int a=1;a<29;a++) for(int b=1;b<29;b++) if((a*b)%29==1) inv[a]=b;
  for(int v=0;v<2;v++)for(int p=0;p<29;p++)for(int d=0;d<29;d++){
    int8_t z=-1,rr=0;
    if(p<28&&d>=1){ z=v==0?((d-p)%28+28)%28:(d+p)%28; }
    ZT[v][p][d]=z;
    RT[v][p][d]=v==0?(((d-p)%29)+29)%29:(d+p)%29;   // here d plays role of c
  }
  for(int var=0;var<112;var++){ int inv_=var/56, sg=(var/28)%2, o=var%28;
    for(int p=0;p<29;p++)for(int d=0;d<29;d++){ int8_t z=-1;
      if(p<28&&d>=1){ int x=sg? (((o-p)%28)+28)%28+1 : ((p+o)%28)+1; z= inv_? (x*inv[d])%29 : (d*inv[x])%29; }
      GFT[var][p][d]=z; } }
}
// exact: best over orient/shift of sum of quadgram logprobs over valid windows
static float exact_best(const int8_t *k,int L,int mi,int *bs,int *bo,int *Wout){
  int wj[LMAX],W=0; for(int j=0;j+3<L;j++) if(k[j]>=0&&k[j+1]>=0&&k[j+2]>=0&&k[j+3]>=0) wj[W++]=j;
  *Wout=W; if(!W) return -1e9f;
  int m=MOD[mi]; float best=-1e30f; int s_b=0,o_b=0;
  for(int o=0;o<2;o++)for(int s=0;s<m;s++){ const int8_t *tl=TLET[mi][o][s]; float sum=0;
    for(int t=0;t<W;t++){ int j=wj[t]; sum+=Q[((tl[k[j]]*29+tl[k[j+1]])*29+tl[k[j+2]])*29+tl[k[j+3]]]; }
    if(sum>best){best=sum;s_b=s;o_b=o;} }
  *bs=s_b;*bo=o_b; return best;
}

static inline void make_diffs(const int8_t *k,int L,int mi,int8_t *d,int8_t *nd,int *anyinv){
  int inv=0;
  for(int i=0;i+1<L;i++){ if(k[i]<0||k[i+1]<0){ d[i]=-1; nd[i]=-1; inv=1; } else { int x=DIF[mi][k[i]][k[i+1]]; d[i]=x; nd[i]=NEG[mi][x]; } }
  *anyinv=inv;
}
// prefilter from diffs: returns max over orientation of sum of T3 over valid windows; W = number of valid windows
static float pf_d(const int8_t *d,const int8_t *nd,int L,int mi,int *Wout){
  float s0=0,s1=0; int W=0; const float *T=T3[mi];
  for(int j=0;j+3<L;j++){ if((d[j]|d[j+1]|d[j+2])<0) continue; W++;
    s0+=T[(d[j]*29+d[j+1])*29+d[j+2]]; s1+=T[(nd[j]*29+nd[j+1])*29+nd[j+2]]; }
  *Wout=W; return s0>s1?s0:s1;
}
static float pf_val(const int8_t *k,int L,int mi,int *Wout){
  int8_t d[LMAX+48],nd[LMAX+48]; int inv; make_diffs(k,L,mi,d,nd,&inv); return pf_d(d,nd,L,mi,Wout);
}
// longest run of consecutive equal positions k[i]==k[i+p] (both valid); SSE: sentinel breaks runs
static int per_len(const int8_t *k,int L,int *pbest){
  int best=0,bp=0; int pm=L-4; if(pm>12) pm=12;
  __m128i m1=_mm_set1_epi8(-1);
  for(int p=1;p<=pm;p++){
    unsigned __int128 mask=0; int nb=L-p;
    for(int c0=0;c0<nb;c0+=16){
      __m128i a=_mm_loadu_si128((const __m128i*)(k+c0)), b=_mm_loadu_si128((const __m128i*)(k+c0+p));
      __m128i e=_mm_and_si128(_mm_cmpeq_epi8(a,b),_mm_cmpgt_epi8(a,m1));
      unsigned int mm=(unsigned int)_mm_movemask_epi8(e); mask|=((unsigned __int128)mm)<<c0; }
    if(nb<128) mask&=(((unsigned __int128)1)<<nb)-1;
    if(!mask) continue;
    int r=0; unsigned __int128 x=mask; while(x){ r++; x&=x>>1; }
    if(r>best){best=r;bp=p;}
  }
  *pbest=bp; return best;
}
// per_len with wildcard-neutral semantics (slow path, used for rawskip bridging)
static int per_len_wild(const int8_t *k,int L,int *pbest){
  int best=0,bp=0; int pm=L-4; if(pm>12) pm=12;
  for(int p=1;p<=pm;p++){ int run=0; for(int i=0;i+p<L;i++){ int a=k[i],b=k[i+p]; if(a<0||b<0) continue; if(a==b){ run++; if(run>best){best=run;bp=p;} } else run=0; } }
  *pbest=bp; return best;
}
static int dict_d(const int8_t *d,const int8_t *nd,int L,int mi,int anyinv){
  if(L<8) return 0; int m=MOD[mi]; int nw=L-7;
  uint32_t sg[2][LMAX]; unsigned char b6[2][LMAX]; int n6=L-5;  // 6-letter windows j=0..L-6 (5 diffs d[j..j+4])
  for(int o=0;o<2;o++){ const int8_t *dd=o?nd:d; uint32_t cur=0; int okprev=0;
    for(int j=0;j<n6;j++){
      int ok=1;
      if(anyinv){ for(int t=0;t<5;t++) if(dd[j+t]<0){ok=0;break;} }
      if(!ok){ b6[o][j]=0; okprev=0; continue; }
      if(okprev){ cur=(cur-dd[j-1])/m+dd[j+4]*(uint32_t)pw[mi][4]; }
      else { cur=0; for(int t=0;t<5;t++) cur+=dd[j+t]*(uint32_t)pw[mi][t]; }
      okprev=1; sg[o][j]=cur; b6[o][j]=hbit(bm6[mi],cur); } }
  int best=0;
  for(int o=0;o<2;o++){ const int8_t *dd=o?nd:d; int run=0;
    for(int j=0;j<nw;j++){ int hit=0;
      if(b6[o][j]&&b6[o][j+2]){ if(!anyinv||(dd[j+5]>=0&&dd[j+6]>=0)){
          uint64_t s7=sg[o][j]+(uint64_t)dd[j+5]*pw[mi][5]+(uint64_t)dd[j+6]*pw[mi][6];
          hit=hbit(bm8[mi],(s7*0x9E3779B97F4A7C15ULL)>>34); } }
      if(hit){ run++; if(run>best) best=run; } else run=0; } }
  return best?best+7:0;
}
static int dict_len(const int8_t *k,int L,int mi){
  int8_t d[LMAX+48],nd[LMAX+48]; int inv; make_diffs(k,L,mi,d,nd,&inv); return dict_d(d,nd,L,mi,inv);
}
static int fcmp(const void*x,const void*y){ float u=*(const float*)x,v=*(const float*)y; return (u>v)-(u<v);}
static void calibrate(){
  #pragma omp parallel for schedule(dynamic,1) collapse(2)
  for(int mi=0;mi<2;mi++) for(int W=1;W<=WMAX-3;W++){
    int m=MOD[mi]; int L=W+3; int N=W<=30?4000:(W<=60?2000:1000);
    uint64_t rng=0x1234567ULL*(mi+1)+W*7919ULL; float *ex=malloc(N*4),*pf=malloc(N*4); int8_t k[LMAX];
    for(int t=0;t<N;t++){ for(int j=0;j<L;j++) k[j]=splitmix(&rng)%m; int s,o,Wd; ex[t]=exact_best(k,L,mi,&s,&o,&Wd); pf[t]=pf_val(k,L,mi,&Wd); }
    double a=0,b=0; for(int t=0;t<N;t++){a+=ex[t];b+=ex[t]*ex[t];} a/=N; b=sqrt(b/N-a*a); mu[mi][W]=a; sd_[mi][W]=b;
    float *tmp=malloc(N*4); memcpy(tmp,pf,N*4);
    // 96th percentile via partial sort (simple qsort)
    qsort(tmp,N,4,fcmp);
    pft[mi][W]=tmp[(int)(0.96*N)];
    // recall for Z>=3
    int nz=0,nr=0; for(int t=0;t<N;t++) if((ex[t]-a)/b>=3.0){ nz++; if(pf[t]>=pft[mi][W]) nr++; }
    if(W==4||W==8||W==20) fprintf(stderr,"calib mi=%d W=%d mu=%.3f sd=%.3f pfthr=%.3f recall(Z>=3)=%d/%d\n",mi,W,a,b,pft[mi][W],nr,nz);
    free(ex);free(pf);free(tmp);
  }
}
// ---------- hit lists
typedef struct { Hit *a; int n,K; float minkey; } HList;
static void hl_init(HList *h,int K){ h->a=malloc(sizeof(Hit)*K); h->n=0; h->K=K; h->minkey=-1e30f; }
static void hl_push(HList *h,const Hit *x){
  if(h->n<h->K){ h->a[h->n++]=*x; if(h->n==h->K){ float m=1e30f; for(int i=0;i<h->K;i++) if(h->a[i].key<m) m=h->a[i].key; h->minkey=m; } return; }
  if(x->key<=h->minkey) return; int mi=0; for(int i=1;i<h->K;i++) if(h->a[i].key<h->a[mi].key) mi=i; h->a[mi]=*x;
  float m=1e30f; for(int i=0;i<h->K;i++) if(h->a[i].key<m) m=h->a[i].key; h->minkey=m;
}
typedef struct { double nfrag; float maxZ,maxD,maxP; long nZ3,nZ4,nZ5,nD9,nD10,nD12,nP5,nP6,nP8; } Cell;
int main(int argc,char**argv){
  if(argc<8){fprintf(stderr,"usage\n");return 1;}
  int Fdel=atoi(argv[4]); float zdump=atof(argv[5]); int ddump=atoi(argv[6]); int pdump=atoi(argv[7]); const char *dumpf=argc>8?argv[8]:NULL;
  // load tables
  char path[512]; const char *base=getenv("DRAGDIR"); if(!base) base=".";
  #define LOAD(var,name,sz) { snprintf(path,512,"%s/%s",base,name); FILE*f=fopen(path,"rb"); if(!f){perror(path);return 2;} var=malloc(sz); if(fread(var,1,sz,f)!=(size_t)(sz)){fprintf(stderr,"short %s\n",path);return 2;} fclose(f); }
  LOAD(Q,"quad.f32",29*29*29*29*4);
  { float *t; LOAD(t,"t3_29.f32",29*29*29*4); memcpy(T3[0],t,29*29*29*4); LOAD(t,"t3_28.f32",29*29*29*4); memcpy(T3[1],t,29*29*29*4); }
  LOAD(bm6[0],"bm6_29.bin",(20511149+7)/8+8); LOAD(bm6[1],"bm6_28.bin",(17210368+7)/8+8);
  LOAD(bm8[0],"bm8_29.bin",(1<<30)/8); LOAD(bm8[1],"bm8_28.bin",(1<<30)/8);
  build_tabs();
  // stream
  { FILE*f=fopen(argv[1],"rb"); int32_t n0; fread(&n0,4,1,f); uint8_t*c0=malloc(n0); int16_t*p0=malloc(2*n0); int32_t*w0=malloc(4*n0);
    fread(c0,1,n0,f); fread(p0,2,n0,f); fread(w0,4,n0,f); fclose(f);
    c=malloc(n0);pg=malloc(2*n0);wd=malloc(4*n0); n=0;
    for(int i=0;i<n0;i++){ if(Fdel&&c0[i]==0) continue; c[n]=c0[i];pg[n]=p0[i];wd[n]=w0[i];n++; }
    free(c0);free(p0);free(w0); }
  // words
  wstart=malloc(4*n);wlen=malloc(4*n); nwords=0; for(int i=0;i<n;i++){ if(i==0||wd[i]!=wd[i-1]){ wstart[nwords]=i; wlen[nwords]=1; nwords++; } else wlen[nwords-1]++; }
  // D
  uint8_t *D=malloc(n); D[0]=0; for(int i=1;i<n;i++) D[i]=(c[i]-c[i-1]+29)%29;
  // cribs
  { FILE*f=fopen(argv[2],"r"); fscanf(f,"%d",&ncr); cr=calloc(ncr,sizeof(Crib));
    for(int i=0;i<ncr;i++){ Crib*x=&cr[i]; fscanf(f,"%d %d %d %d",&x->id,&x->cls,&x->alonly,&x->nw); for(int t=0;t<x->nw;t++) fscanf(f,"%d",&x->wl[t]); fscanf(f,"%d",&x->L); if(x->L>LMAX){fprintf(stderr,"L too big\n");return 3;} for(int t=0;t<x->L;t++){int v; fscanf(f,"%d",&v); x->r[t]=v;} } fclose(f); }
  fprintf(stderr,"n=%d words=%d cribs=%d Fdel=%d\n",n,nwords,ncr,Fdel);
  calibrate();
  int NT=omp_get_max_threads();
  Cell *cells=calloc((size_t)NT*NMODEL*NCLS*2,sizeof(Cell)); for(size_t q=0;q<(size_t)NT*NMODEL*NCLS*2;q++) cells[q].maxZ=-1e9f;
  HList *hz=malloc(sizeof(HList)*NT*NMODEL),*hd=malloc(sizeof(HList)*NT*NMODEL),*hp=malloc(sizeof(HList)*NT*NMODEL);
  for(int i=0;i<NT*NMODEL;i++){ hl_init(&hz[i],100); hl_init(&hd[i],30); hl_init(&hp[i],30); }
  FILE *df=dumpf?fopen(dumpf,"w"):NULL;
  // crib order: longest first
  int *ord=malloc(4*ncr); for(int i=0;i<ncr;i++) ord[i]=i;
  for(int i=0;i<ncr;i++)for(int j=i+1;j<ncr;j++) if(cr[ord[j]].L>cr[ord[i]].L){int t=ord[i];ord[i]=ord[j];ord[j]=t;}
  #pragma omp parallel
  {
    int tid=omp_get_thread_num(); int *pos=malloc(4*(n+1));
    #pragma omp for schedule(dynamic,1)
    for(int ci=0;ci<ncr;ci++){ Crib *cb=&cr[ord[ci]]; int L=cb->L;
      for(int al=0;al<2;al++){
        if(al==0&&cb->alonly) continue;
        int np=0;
        if(al==0){ for(int i=1;i+L<=n;i++) if(pg[i-1]==pg[i+L-1]) pos[np++]=i; }
        else { for(int q=0;q+cb->nw<=nwords;q++){ int ok=1; for(int t=0;t<cb->nw;t++) if(wlen[q+t]!=cb->wl[t]){ok=0;break;}
                 if(!ok) continue; int i=wstart[q]; if(i<1||i+L>n) continue; if(pg[i-1]!=pg[i+L-1]) continue; pos[np++]=i; } }
        for(int pi=0;pi<np;pi++){ int i=pos[pi];
          int8_t kk[LMAX+48],kp[LMAX+48];
          // enumerate variants
          for(int mt=0;mt<NMODEL;mt++){
            int nvar= mt==0?2: mt==1?28: 2;
            Cell *cell=&cells[(((size_t)tid*NMODEL+mt)*NCLS+cb->cls)*2+al];
            for(int var=0;var<nvar;var++){
              int mi= mt==0?1:0;
              if(mt==0) for(int j=0;j<L;j++) kk[j]=ZT[var][cb->r[j]][D[i+j]];
              else if(mt==1) for(int j=0;j<L;j++) kk[j]=GFT[var][cb->r[j]][D[i+j]];
              else for(int j=0;j<L;j++) kk[j]=RT[var][cb->r[j]][c[i+j]];
              float Z=-1e9f; int bs=0,bo=0,W=0,dl=0,pl=0,pper=0; int gbest=0;
              if(mt<3){
                int8_t d_[LMAX+48],nd_[LMAX+48]; int inv_; make_diffs(kk,L,mi,d_,nd_,&inv_);
                int Wp; float pf=pf_d(d_,nd_,L,mi,&Wp);
                if(Wp>0 && pf>=pft[mi][Wp]){ float ex=exact_best(kk,L,mi,&bs,&bo,&W); Z=(ex-mu[mi][W])/sd_[mi][W]; } else W=Wp;
                if(!(mt==1&&al==0)) dl=dict_d(d_,nd_,L,mi,inv_);
                pl=per_len(kk,L,&pper);
              } else {
                // rawskip: <=1 skip: gap before letter g (g=0 none). PF by prefix sums
                int mi2=0; int Wn=L-3; float w0[LMAX],w1[LMAX]; const float *T=T3[0];
                float P0[LMAX+1],P1[LMAX+1]; P0[0]=P1[0]=0;
                for(int j=0;j<Wn;j++){ int d1=DIF[0][kk[j]][kk[j+1]],d2=DIF[0][kk[j+1]][kk[j+2]],d3=DIF[0][kk[j+2]][kk[j+3]];
                  w0[j]=T[(d1*29+d2)*29+d3]; w1[j]=T[(NEG[0][d1]*29+NEG[0][d2])*29+NEG[0][d3]]; P0[j+1]=P0[j]+w0[j]; P1[j+1]=P1[j]+w1[j]; }
                Z=-1e9f;
                for(int g=0;g<L;g++){
                  int lw= g>=4? g-3:0; int rs= g<Wn? g:Wn; if(g==0){lw=0;rs=0;}
                  int Wg= (g==0)? Wn : lw+(Wn-rs); if(Wg<=0) continue;
                  float l0= g==0?0:P0[lw], r0=P0[Wn]-P0[rs], l1= g==0?0:P1[lw], r1=P1[Wn]-P1[rs];
                  float pf=(l0+r0>l1+r1)?(l0+r0):(l1+r1);
                  if(pf<pft[0][Wg]) continue;
                  int m_=0; for(int t=0;t<g;t++) kp[m_++]=kk[t]; if(g>0) kp[m_++]=-1; for(int t=g;t<L;t++) kp[m_++]=kk[t];
                  int s_,o_,Wd; float ex=exact_best(kp,m_,0,&s_,&o_,&Wd); float z=(ex-mu[0][Wd])/sd_[0][Wd];
                  if(z>Z){Z=z;bs=s_;bo=o_;W=Wd;gbest=g;}
                }
                pl=per_len(kk,L,&pper);
                if(pl>=3){ for(int g=1;g<L;g++){ int m_=0; for(int t=0;t<g;t++) kp[m_++]=kk[t]; kp[m_++]=-1; for(int t=g;t<L;t++) kp[m_++]=kk[t];
                    int pp; int r=per_len_wild(kp,m_,&pp); if(r>pl){pl=r;pper=pp;} } }
                dl=0;
              }
              cell->nfrag+=1;
              if(Z>cell->maxZ) cell->maxZ=Z;
              if(Z>=3) cell->nZ3++; if(Z>=4) cell->nZ4++; if(Z>=5) cell->nZ5++;
              if(dl>cell->maxD) cell->maxD=dl; if(pl>cell->maxP) cell->maxP=pl;
              if(dl>=9) cell->nD9++; if(dl>=10) cell->nD10++; if(dl>=12) cell->nD12++;
              if(pl>=5) cell->nP5++; if(pl>=6) cell->nP6++; if(pl>=8) cell->nP8++;
              int interesting = (Z>=zdump)||(dl>=ddump)||(pl>=pdump);
              HList *Hz=&hz[tid*NMODEL+mt],*Hd=&hd[tid*NMODEL+mt],*Hp=&hp[tid*NMODEL+mt];
              if(interesting||Z>Hz->minkey||dl>Hd->minkey||pl>Hp->minkey){
                Hit h; h.Z=Z;h.crib=cb->id;h.pos=i;h.mt=mt;h.var=var;h.shift=bs;h.orient=bo;h.W=W;h.al=al;h.cls=cb->cls;h.dict=dl;h.per=pl;h.L=L;
                memcpy(h.k,kk,L);
                if(Z>Hz->minkey){h.key=Z;hl_push(Hz,&h);} if(dl>Hd->minkey){h.key=dl+(Z<-50?-50:Z)*1e-4f;hl_push(Hd,&h);} if(pl>Hp->minkey){h.key=pl+(Z<-50?-50:Z)*1e-4f;hl_push(Hp,&h);}
                if(interesting&&df){
                  #pragma omp critical
                  { fprintf(df,"%d %d %d %d %d %d %d %d %d %d %.3f %d %d %d ",cb->id,i,mt,var,bs,bo,W,al,cb->cls,L,Z,dl,pl,gbest);
                    for(int j=0;j<L;j++) fprintf(df,"%d,",kk[j]); fprintf(df,"\n"); }
                }
              }
            }
          }
        }
      }
    }
    free(pos);
  }
  if(df) fclose(df);
  // merge + output
  FILE *fo=fopen(argv[3],"w");
  for(int mt=0;mt<NMODEL;mt++)for(int cls=0;cls<NCLS;cls++)for(int al=0;al<2;al++){
    Cell t; memset(&t,0,sizeof t); t.maxZ=-1e9f;
    for(int th=0;th<NT;th++){ Cell *x=&cells[(((size_t)th*NMODEL+mt)*NCLS+cls)*2+al]; if(x->nfrag==0) continue;
      t.nfrag+=x->nfrag; if(x->maxZ>t.maxZ)t.maxZ=x->maxZ; if(x->maxD>t.maxD)t.maxD=x->maxD; if(x->maxP>t.maxP)t.maxP=x->maxP;
      t.nZ3+=x->nZ3;t.nZ4+=x->nZ4;t.nZ5+=x->nZ5;t.nD9+=x->nD9;t.nD10+=x->nD10;t.nD12+=x->nD12;t.nP5+=x->nP5;t.nP6+=x->nP6;t.nP8+=x->nP8; }
    fprintf(fo,"CELL %d %d %d %.0f %.3f %.0f %.0f %ld %ld %ld %ld %ld %ld %ld %ld %ld\n",mt,cls,al,t.nfrag,t.maxZ,t.maxD,t.maxP,t.nZ3,t.nZ4,t.nZ5,t.nD9,t.nD10,t.nD12,t.nP5,t.nP6,t.nP8);
  }
  const char *nm[3]={"TOPZ","TOPD","TOPP"};
  for(int mt=0;mt<NMODEL;mt++)for(int w=0;w<3;w++){ HList *src= w==0?hz:(w==1?hd:hp);
    for(int th=0;th<NT;th++){ HList *h=&src[th*NMODEL+mt]; for(int a=0;a<h->n;a++){ Hit *x=&h->a[a];
      fprintf(fo,"%s %d %.3f %d %d %d %d %d %d %d %d %d %d %d ",nm[w],mt,x->Z,x->crib,x->pos,x->var,x->shift,x->orient,x->W,x->al,x->cls,x->dict,x->per,x->L);
      for(int j=0;j<x->L;j++) fprintf(fo,"%d,",x->k[j]); fprintf(fo,"\n"); } } }
  fclose(fo); return 0;
}
