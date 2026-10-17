// Keyword attack on chain-cipher families. See RESULTS.md for the model definitions.
// usage: kc FAMILY units.txt keys.txt out.tsv [topK]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>
#define MAXN 4096
#define MAXU 4096
#define MAXK 400000
#define NLEN 18
typedef struct { int n, prev, id, nz[2]; unsigned char c[MAXN]; unsigned char D[MAXN]; unsigned char T[14][MAXN]; } Unit;
typedef struct { float q, ioc; int key, var; } Hit;
typedef struct { Hit *topq, *topi; float lenq[NLEN], leni[NLEN]; double sq, sq2, si, si2; long cnt; } Res;
static Unit *U; static int NU;
static int NK; static unsigned char *KL; static unsigned char KV[MAXK][40]; static int KSRC[MAXK];
static float *QT; static short *QS; static double UNI[29];
static int TOPK=30, FAM;
static int tau[14][29]; // tau[t][D] for D=1..28 -> 0..27
static int inv29[29]; static unsigned char MT[29][29];
static int NVAR;

static inline void push(Hit *a, Hit h, int byq){ // keep sorted descending, size TOPK
  float v = byq? h.q : h.ioc;
  if(v <= (byq? a[TOPK-1].q : a[TOPK-1].ioc)) return;
  int i=TOPK-1;
  while(i>0 && v > (byq? a[i-1].q : a[i-1].ioc)){ a[i]=a[i-1]; i--; }
  a[i]=h;
}
static inline void score(const unsigned char *o, int m, float *q, float *ioc){
  int h[29]={0}; double s=0; int a=o[0],b=o[1],c=o[2];
  h[a]++;h[b]++;h[c]++;
  for(int i=3;i<m;i++){ int p=o[i]; h[p]++; s+=QT[((a*29+b)*29+c)*29+p]; a=b;b=c;c=p; }
  long t=0; for(int r=0;r<29;r++) t+= (long)h[r]*(h[r]-1);
  *q = s/(m-3); *ioc = 29.0*t/((double)m*(m-1));
}
static void record(Res *R, float q, float ioc, int key, int var){
  Hit h={q,ioc,key,var}; push(R->topq,h,1); push(R->topi,h,0);
  int L=KL[key]; if(L>NLEN-1) L=NLEN-1;
  if(q>R->lenq[L]) R->lenq[L]=q; if(ioc>R->leni[L]) R->leni[L]=ioc;
  R->sq+=q; R->sq2+=(double)q*q; R->si+=ioc; R->si2+=(double)ioc*ioc; R->cnt++;
}
int main(int argc,char**argv){
  FAM=atoi(argv[1]); if(argc>5) TOPK=atoi(argv[5]);
  // tables
  for(int a=1;a<29;a++) for(int b=1;b<29;b++) if(a*b%29==1) inv29[a]=b;
  for(int a=0;a<29;a++) for(int b=0;b<29;b++) MT[a][b]=(a*b+28)%29;
  for(int D=1;D<29;D++){ tau[0][D]=D-1; tau[1][D]=28-D; }
  int t=2; for(int g=2;g<29;g++){ int x=1,ord=0; do{ x=x*g%29; ord++; }while(x!=1); if(ord!=28) continue;
    x=1; for(int e=0;e<28;e++){ tau[t][x]=e; x=x*g%29; } t++; }
  if(t!=14){fprintf(stderr,"roots %d\n",t);return 1;}
  QT=malloc(sizeof(float)*707281); FILE*f=fopen("quad29.f32","rb"); fread(QT,4,707281,f); fclose(f);
  QS=malloc(2*707281); for(int i=0;i<707281;i++) QS[i]=(short)lrintf(QT[i]*1000.f);
  f=fopen("uni29.f64","rb"); fread(UNI,8,29,f); fclose(f);
  // units
  U=malloc(sizeof(Unit)*MAXU); f=fopen(argv[2],"r"); NU=0;
  while(fscanf(f,"%d %d %d",&U[NU].id,&U[NU].prev,&U[NU].n)==3){ Unit*u=&U[NU];
    for(int i=0;i<u->n;i++){int v; fscanf(f,"%d",&v); u->c[i]=v;}
    for(int i=0;i<u->n;i++){ int pv = i? u->c[i-1] : u->prev; u->D[i]=((int)u->c[i]-pv+29)%29;
      for(int tt=0;tt<14;tt++) u->T[tt][i]= u->D[i]? tau[tt][u->D[i]] : 255; }
    u->nz[0]=u->nz[1]=0; for(int i=0;i<u->n;i++) if(!u->D[i]){ u->nz[1]+= (i>0); u->nz[0]++; }
    NU++; }
  fclose(f);
  KL=malloc(MAXK); f=fopen(argv[3],"r"); NK=0; int src,L;
  while(fscanf(f,"%d %d",&src,&L)==2){ KSRC[NK]=src; KL[NK]=L; for(int i=0;i<L;i++){int v;fscanf(f,"%d",&v); KV[NK][i]=v;} NK++; }
  fclose(f);
  NVAR = FAM==1?112: FAM==2?16: 5;
  fprintf(stderr,"fam %d units %d keys %d variants %d\n",FAM,NU,NK,NVAR);
  int NT=omp_get_max_threads();
  Res *RR=calloc((size_t)NT*NU,sizeof(Res));
  for(int i=0;i<NT*NU;i++){ RR[i].topq=calloc(TOPK,sizeof(Hit)); RR[i].topi=calloc(TOPK,sizeof(Hit));
     for(int k=0;k<TOPK;k++){RR[i].topq[k].q=-1e9;RR[i].topq[k].ioc=-1e9;RR[i].topi[k].q=-1e9;RR[i].topi[k].ioc=-1e9;}
     for(int l=0;l<NLEN;l++){RR[i].lenq[l]=-1e9;RR[i].leni[l]=-1e9;} }
  double t0=omp_get_wtime(); long steps=0;
  #pragma omp parallel reduction(+:steps)
  {
    int tid=omp_get_thread_num(); unsigned char o[MAXN]; 
    #pragma omp for schedule(dynamic,64)
    for(int key=0;key<NK;key++){
      int L=KL[key]; unsigned char *kv=KV[key];
      for(int ui=0;ui<NU;ui++){ Unit*u=&U[ui]; Res*R=&RR[tid*NU+ui]; int n=u->n;
        if(FAM==1){
          int k28[40]; for(int j=0;j<L;j++) k28[j]=kv[j]%28;
          for(int tt=0;tt<14;tt++) for(int sg=0;sg<2;sg++){
            int sub[28][40]; for(int v=0;v<28;v++) for(int j=0;j<L;j++) sub[v][j]= sg? (v+k28[j])%28 : (v-k28[j]+28)%28;
            for(int conv=0;conv<2;conv++) for(int al=0;al<2;al++){
              if(conv && u->nz[al]==0) continue;
              const unsigned char*T=u->T[tt]; int j=0,m=0; int h[29]={0}; long qs=0; int a=0,b=0,cc=0;
              for(int i=al;i<n;i++){ int tv=T[i], p; if(tv==255){ p=28; if(conv){ if(++j==L)j=0; } } else { p=sub[tv][j]; if(++j==L)j=0; }
                h[p]++; if(m>=3) qs+=QS[((a*29+b)*29+cc)*29+p]; a=b;b=cc;cc=p; m++; }
              long tt2=0; for(int r=0;r<29;r++) tt2+=(long)h[r]*(h[r]-1);
              float q=qs/1000.0/(m-3), ioc=29.0*tt2/((double)m*(m-1)); record(R,q,ioc,key,((tt*2+sg)*2+conv)*2+al); steps+=m;
            }
          }
        } else if(FAM==2){
          for(int kvm=0;kvm<2;kvm++){
            int kk[40],LL=0; for(int j=0;j<L;j++){ int v= kvm? ( (int[]){2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109} )[kv[j]]%29 : (kv[j]+1)%29; if(v) kk[LL++]=v; }
            if(!LL) continue;
            for(int dir=0;dir<2;dir++){ int mul[40]; for(int j=0;j<LL;j++) mul[j]= dir? kk[j] : inv29[kk[j]];
              for(int conv=0;conv<2;conv++) for(int al=0;al<2;al++){
                if(conv && u->nz[al]==0) continue;
                int j=0,m=0; int h[29]={0}; long qs=0; int a=0,b=0,cc=0;
                for(int i=al;i<n;i++){ int D=u->D[i],p; if(!D){ p=28; if(conv){ if(++j==LL)j=0; } } else { p=MT[D][mul[j]]; if(++j==LL)j=0; }
                  h[p]++; if(m>=3) qs+=QS[((a*29+b)*29+cc)*29+p]; a=b;b=cc;cc=p; m++; }
                long tt2=0; for(int r=0;r<29;r++) tt2+=(long)h[r]*(h[r]-1);
                float q=qs/1000.0/(m-3), ioc=29.0*tt2/((double)m*(m-1)); record(R,q,ioc,key,((kvm*2+dir)*2+conv)*2+al); steps+=m;
              }
            }
          }
        } else {
          for(int var=0;var<5;var++){
            int j=0,m=0; const unsigned char*c=u->c;
            if(var<3){ for(int i=0;i<n;i++){ int k=kv[j]; int p= var==0? (c[i]-k+29)%29 : var==1? (k-c[i]+29)%29 : (c[i]+k)%29; o[m++]=p; if(++j==L)j=0; } }
            else { int bea=(var==4);
              for(int i=0;i<n;i++){
                int k=kv[j]; int p= bea? (k-c[i]+29)%29 : (c[i]-k+29)%29;
                if(i>0 && c[i]==c[i-1]){ if(++j==L)j=0; k=kv[j]; p= bea? (k-c[i]+29)%29 : (c[i]-k+29)%29; o[m++]=p; if(++j==L)j=0; continue; }
                if(i>0){ int j1=(j+1)%L; if( ((c[i]-c[i-1]+29)%29) == ((kv[j1]-kv[j]+29)%29) ){
                    int ps= bea? (k-c[i-1]+29)%29 : (c[i-1]-k+29)%29;
                    // lookahead: score last 3 outputs + candidate + next 5 plain decrypts under each hypothesis
                    double sc[2]; int cand[2]={p,ps}, jn[2]={(j+1)%L,(j+2)%L};
                    for(int h=0;h<2;h++){ int w[12],wm=0; for(int b=3;b>=1;b--) w[wm++]= m-b>=0? o[m-b] : 18; w[wm++]=cand[h];
                      int jj=jn[h]; for(int a=1;a<=5 && i+a<n;a++){ int kk=kv[jj]; w[wm++]= bea? (kk-c[i+a]+29)%29 : (c[i+a]-kk+29)%29; jj=(jj+1)%L; }
                      double ss=0; for(int b=0;b+3<wm;b++) ss+=QT[((w[b]*29+w[b+1])*29+w[b+2])*29+w[b+3]]; sc[h]=ss; }
                    if(sc[1]>sc[0]){ o[m++]=ps; j=(j+2)%L; continue; } } }
                o[m++]=p; if(++j==L)j=0;
              } }
            float q,ioc; score(o,m,&q,&ioc); record(R,q,ioc,key,var); steps+=m;
          }
        }
      }
      if(tid==0 && key%20000==0) fprintf(stderr,"key %d %.1fs\n",key,omp_get_wtime()-t0);
    }
  }
  double el=omp_get_wtime()-t0;
  fprintf(stderr,"done %.1fs, %.3g rune-steps, %.3g steps/s\n",el,(double)steps,steps/el);
  // merge
  FILE*o=fopen(argv[4],"w");
  fprintf(o,"#fam %d units %d keys %d variants %d seconds %.1f steps %.4g\n",FAM,NU,NK,NVAR,el,(double)steps);
  for(int ui=0;ui<NU;ui++){
    Res M; M.topq=calloc(TOPK,sizeof(Hit)); M.topi=calloc(TOPK,sizeof(Hit));
    for(int k=0;k<TOPK;k++){M.topq[k].q=-1e9;M.topq[k].ioc=-1e9;M.topi[k].q=-1e9;M.topi[k].ioc=-1e9;}
    for(int l=0;l<NLEN;l++){M.lenq[l]=-1e9;M.leni[l]=-1e9;} M.sq=M.sq2=M.si=M.si2=0;M.cnt=0;
    for(int t2=0;t2<NT;t2++){ Res*R=&RR[t2*NU+ui];
      for(int k=0;k<TOPK;k++){ if(R->topq[k].q>-1e8) push(M.topq,R->topq[k],1); if(R->topi[k].ioc>-1e8) push(M.topi,R->topi[k],0); }
      for(int l=0;l<NLEN;l++){ if(R->lenq[l]>M.lenq[l])M.lenq[l]=R->lenq[l]; if(R->leni[l]>M.leni[l])M.leni[l]=R->leni[l]; }
      M.sq+=R->sq;M.sq2+=R->sq2;M.si+=R->si;M.si2+=R->si2;M.cnt+=R->cnt; }
    int id=U[ui].id; double mq=M.sq/M.cnt, mi=M.si/M.cnt;
    fprintf(o,"STAT\t%d\t%ld\t%.5f\t%.5f\t%.5f\t%.5f\n",id,M.cnt,mq,sqrt(M.sq2/M.cnt-mq*mq),mi,sqrt(M.si2/M.cnt-mi*mi));
    for(int k=0;k<TOPK;k++) fprintf(o,"TOPQ\t%d\t%d\t%.5f\t%.5f\t%d\t%d\n",id,k,M.topq[k].q,M.topq[k].ioc,M.topq[k].key,M.topq[k].var);
    for(int k=0;k<TOPK;k++) fprintf(o,"TOPI\t%d\t%d\t%.5f\t%.5f\t%d\t%d\n",id,k,M.topi[k].ioc,M.topi[k].q,M.topi[k].key,M.topi[k].var);
    for(int l=1;l<NLEN;l++) fprintf(o,"LEN\t%d\t%d\t%.5f\t%.5f\n",id,l,M.lenq[l],M.leni[l]);
  }
  fclose(o); return 0;
}
