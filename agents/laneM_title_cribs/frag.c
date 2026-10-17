// laneM: key-fragment extraction under all decryptable models + fragment structure tests (a),(b),(c),(e).
// usage: frag lm.bin htab.bin job.txt out_prefix
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define NF 6          // families: 0 chainAdd(Z28) 1 gfRaw(Z29) 2 gfDlog(Z28) 3 vig(Z29) 4 vigSkip(Z29) 5 Fint(any)
#define LM 48         // max fragment length tracked
#define NB 400        // eng score bins: -8..0 step 0.02
#define TOPK 25
#define HMAX 24
#define HITMIN 8
static int16_t *Q,*T3,*B2,*U1;
static uint64_t *H; static uint32_t *TG; static int64_t NH; static int64_t *BIDX; // bucket index on top 24 bits
static int BT[14][29], SG[30][29], DL2[29], INV[29];
static long hist[NF][LM][NB]; static long cnt[NF][LM]; static long hits[NF][LM][4];
typedef struct {int sc; int cid; int model; int n; unsigned char f[LM];} Top;
static Top top[NF][LM][TOPK]; static int ntop[NF][LM];
static FILE *fh; static int OID, POS;
static int mod(int a,int m){a%=m; return a<0?a+m:a;}
static int engscore(const unsigned char *f,int n,int m){
  // max over shifts s and atbash of mean log10 prob (x1000) ; returns per-rune mean*1000
  int best=-1000000000; unsigned char g[LM];
  for(int at=0;at<2;at++) for(int s=0;s<m;s++){
    for(int j=0;j<n;j++){int v= at? (m-1-f[j]+s):(f[j]+s); g[j]=v%m;}
    int sum=U1[g[0]];
    if(n>1) sum+=B2[g[0]*29+g[1]];
    if(n>2) sum+=T3[(g[0]*29+g[1])*29+g[2]];
    for(int j=3;j<n;j++) sum+=Q[((g[j-3]*29+g[j-2])*29+g[j-1])*29+g[j]];
    int sc=sum/n; if(sc>best)best=sc;
  }
  return best;
}
static uint64_t fnv(int m,const int *d,int l){
  uint64_t h=0xcbf29ce484222325ULL; const uint64_t P=0x100000001b3ULL;
  h^=(uint64_t)m; h*=P; h^=(uint64_t)l; h*=P;
  for(int j=0;j<l;j++){h^=(uint64_t)d[j]; h*=P;}
  return h;
}
static int lookup(uint64_t h, uint32_t *out, int maxo){
  int64_t b=h>>40; int k=0;
  for(int64_t i=BIDX[b];i<BIDX[b+1];i++) if(H[i]==h){ if(k<maxo) out[k]=TG[i]; k++; }
  return k;
}
static void record(const unsigned char *f,int n,int m,int fam,int cid,int model){
  if(n<1) return; if(n>=LM) n=LM-1;
  int sc=engscore(f,n,m);
  int bin=(sc+8000)/20; if(bin<0)bin=0; if(bin>=NB)bin=NB-1;
  hist[fam][n][bin]++; cnt[fam][n]++;
  // top-K
  Top *tp=top[fam][n]; int nt=ntop[fam][n];
  if(nt<TOPK || sc>tp[nt-1].sc){
    int i= nt<TOPK? nt : TOPK-1; if(nt<TOPK) ntop[fam][n]++;
    while(i>0 && tp[i-1].sc<sc){tp[i]=tp[i-1]; i--;}
    tp[i].sc=sc; tp[i].cid=cid; tp[i].model=model; tp[i].n=n; memcpy(tp[i].f,f,n);
  }
  if(n>=4){
    int l=(n<HMAX?n:HMAX)-1; int d[LM], dn[LM];
    for(int j=0;j<l;j++){d[j]=mod(f[j+1]-f[j],m); dn[j]=mod(-d[j],m);}
    uint32_t tg[16]; int k=lookup(fnv(m,d,l),tg,8); k= k>8?8:k;
    int k2=lookup(fnv(m,dn,l),tg+k,8); k+= k2>8?8:k2;
    int got[4]={0,0,0,0}; uint32_t keep[16]; int nk=0;
    for(int i=0;i<k;i++){int t=tg[i]>>30; int off=tg[i]&16383;
      if(t==3){ if(abs(off-POS)<=n+2) continue; }
      got[t]=1; keep[nk++]=tg[i];}
    for(int t=1;t<4;t++) if(got[t]) hits[fam][n][t]++;
    if(nk && n>=HITMIN){
      fprintf(fh,"H %d %d %d %d %d %d",OID,cid,model,fam,n,sc);
      fprintf(fh," f=");for(int j=0;j<n;j++)fprintf(fh,"%d,",f[j]);
      for(int i=0;i<nk;i++) fprintf(fh," %u:%u:%u",keep[i]>>30,(keep[i]>>14)&65535,keep[i]&16383);
      fprintf(fh,"\n");
    }
  }
}
static int c[256], prevr, clen;
static void do_crib(int cid,const int *p,int L){
  unsigned char f[LM]; int n;
  if(L>clen) return;
  int intr[LM]; int ni=0; for(int j=0;j<L;j++){intr[j]=(p[j]==0&&c[j]==0); ni+=intr[j];}
  for(int fv=0; fv<=(ni>0); fv++){
    // previous-rune for each position (F-int variant skips interrupted runes)
    int pr[LM]; int last=prevr;
    for(int j=0;j<L;j++){ pr[j]=last; if(!(fv&&intr[j])) last=c[j]; }
    int Dv[LM];
    for(int j=0;j<L;j++){ if(fv&&intr[j]) {Dv[j]=-2; continue;} Dv[j]= pr[j]<0? -1 : mod(c[j]-pr[j],29); }
    int fam5=fv?5:-1;
    // chain additive Z28
    for(int b=0;b<14;b++) for(int s=0;s<30;s++) for(int fo=0;fo<2;fo++){
      n=0; for(int j=0;j<L;j++){ if(Dv[j]<=0) continue; int u=BT[b][Dv[j]], sv=SG[s][p[j]];
        f[n++]= fo? (u+sv)%28 : mod(u-sv,28);}
      record(f,n,28,fv?5:0,cid,(fv<<28)|(0<<24)|(b<<16)|(s<<8)|fo);
    }
    // GF(29) multiplicative
    for(int off=0;off<28;off++) for(int orr=0;orr<2;orr++) for(int iv=0;iv<2;iv++){
      n=0; int bad=0; unsigned char g2[LM];
      for(int j=0;j<L;j++){ if(Dv[j]<=0) continue; int x= p[j]==28?0: 1+ (orr? mod(off-p[j],28) : (p[j]+off)%28);
        if(x==0){bad=1;break;}
        int k= iv? (x*INV[Dv[j]])%29 : (Dv[j]*INV[x])%29; f[n]=k; g2[n]=DL2[k]; n++; }
      if(bad) continue;
      int mdl=(fv<<28)|(1<<24)|(off<<16)|(orr<<8)|iv;
      record(f,n,29,fv?5:1,cid,mdl);
      record(g2,n,28,fv?5:2,cid,mdl|(1<<27));
    }
    // Vigenere / Beaufort (variant Beaufort = negation of Vigenere: covered by the negation-invariant tests)
    for(int fo=0;fo<2;fo++){
      n=0; for(int j=0;j<L;j++){ if(fv&&intr[j]) continue; f[n++]= fo? (c[j]+p[j])%29 : mod(c[j]-p[j],29);} 
      record(f,n,29,fv?5:3,cid,(fv<<28)|(3<<24)|(fo<<16));
      if(fv) continue;
      for(int j0=0;j0<L;j0++){ int pv= j0==0? prevr : c[j0-1]; if(pv<0) continue;
        n=0; for(int j=0;j<L;j++){ if(j==j0) f[n++]= fo? (pv+p[j])%29 : mod(pv-p[j],29);
          f[n++]= fo? (c[j]+p[j])%29 : mod(c[j]-p[j],29);} 
        record(f,n,29,4,cid,(4<<24)|(fo<<16)|((j0+1)<<8));
      }
    }
  }
}
static void dump(const char *pre){
  char fn[512]; sprintf(fn,"%s.agg",pre); FILE *fa=fopen(fn,"a");
  for(int fam=0;fam<NF;fam++) for(int n=1;n<LM;n++){ if(!cnt[fam][n]) continue;
    fprintf(fa,"A %d %d %d %ld %ld %ld %ld |",OID,fam,n,cnt[fam][n],hits[fam][n][1],hits[fam][n][2],hits[fam][n][3]);
    for(int b=0;b<NB;b++) if(hist[fam][n][b]) fprintf(fa," %d:%ld",b,hist[fam][n][b]);
    fprintf(fa,"\n");
    for(int i=0;i<ntop[fam][n];i++){Top *t=&top[fam][n][i];
      fprintf(fa,"T %d %d %d %d %d %d f=",OID,fam,n,t->sc,t->cid,t->model); for(int j=0;j<t->n;j++)fprintf(fa,"%d,",t->f[j]); fprintf(fa,"\n");}
  }
  fclose(fa);
  memset(hist,0,sizeof hist); memset(cnt,0,sizeof cnt); memset(hits,0,sizeof hits); memset(ntop,0,sizeof ntop);
}
int main(int argc,char**argv){
  FILE *f=fopen(argv[1],"rb"); int nq=29*29*29*29;
  Q=malloc(2*nq); T3=malloc(2*29*29*29); B2=malloc(2*29*29); U1=malloc(2*29);
  fread(Q,2,nq,f); fread(T3,2,29*29*29,f); fread(B2,2,29*29,f); fread(U1,2,29,f); fclose(f);
  f=fopen(argv[2],"rb"); fread(&NH,8,1,f); H=malloc(8*NH); TG=malloc(4*NH); fread(H,8,NH,f); fread(TG,4,NH,f); fclose(f);
  int64_t NBK=1LL<<24; BIDX=malloc(8*(NBK+1)); int64_t i=0;
  for(int64_t b=0;b<=NBK;b++){ while(i<NH && (int64_t)(H[i]>>40)<b) i++; BIDX[b]=i; }
  // tables
  int prim[12]={2,3,8,10,11,14,15,18,19,21,26,27};
  for(int x=1;x<29;x++){ for(int y=1;y<29;y++) if(x*y%29==1) INV[x]=y; }
  for(int gi=0;gi<12;gi++){ int v=1; for(int e=0;e<28;e++){ BT[2+gi][v]=e; v=v*prim[gi]%29; } }
  for(int s=1;s<29;s++){BT[0][s]=s-1; BT[1][s]=28-s;}
  { int v=1; for(int e=0;e<28;e++){ DL2[v]=e; v=v*2%29; } DL2[0]=0; }
  for(int s=0;s<29;s++) for(int p=0;p<29;p++) SG[s][p]=((p+s)%29)%28;
  for(int p=0;p<29;p++) SG[29][p]=(28-p)%28;
  char fn[512]; sprintf(fn,"%s.hits",argv[4]); fh=fopen(fn,"w");
  sprintf(fn,"%s.agg",argv[4]); fclose(fopen(fn,"w"));
  FILE *jf=fopen(argv[3],"r"); char tag[16]; int open=0;
  while(fscanf(jf,"%15s",tag)==1){
    if(!strcmp(tag,"OPEN")){ if(open) dump(argv[4]); open=1;
      fscanf(jf,"%d %d %d %d",&OID,&POS,&prevr,&clen); for(int j=0;j<clen;j++) fscanf(jf,"%d",&c[j]); }
    else { int cid=atoi(tag), L; int p[LM]; fscanf(jf,"%d",&L); for(int j=0;j<L;j++) fscanf(jf,"%d",&p[j]); if(L<LM-2) do_crib(cid,p,L); }
  }
  if(open) dump(argv[4]);
  fclose(fh); return 0;
}
