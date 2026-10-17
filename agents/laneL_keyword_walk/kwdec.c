/* kwdec: full decryption of given walk keys with a word-level beam over the skip ambiguities.
   Usage: kwdec TEXT KEYS OUT [beam] [nwords]
   KEYS: lines "mode b g s ..." (indices into A.bin / G.bin; s=-1 for mode 2). OUT: per key one line
   "mode b g s lmscore nsym : p0 p1 ... | wordlens"  (plaintext rune indices, -1 never). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define M 29
#define V 30
#define BND 29
#define MAXW 4000
#define MAXN 20000
static int nw, lens[MAXW], st[MAXW], N, cip[MAXN];
static uint8_t *Aall, *Ainv; static int NA, NG; static uint8_t *G;
static int16_t *LM;
static int lmword(const int *p, int L){ int a=BND,b=BND,c=BND,s=0; for(int i=0;i<L;i++){ s+=LM[((a*V+b)*V+c)*V+p[i]]; a=b;b=c;c=p[i]; } s+=LM[((a*V+b)*V+c)*V+BND]; return s; }
typedef struct { int t; uint8_t binv[M]; long score; int parent; int pw[64]; } St;
static int B = 16;
static St *cur, *nxt; static int ncur, nnxt;
static int gi[5][M], gf[5][M], si[M]; static int mode;
static St **hist; static int *nhist;
static void push(St *s){
  for (int i=0;i<nnxt;i++) if (nxt[i].t==s->t && !memcmp(nxt[i].binv,s->binv,M)){ if (s->score>nxt[i].score) nxt[i]=*s; return; }
  if (nnxt < B){ nxt[nnxt++]=*s; return; }
  int w=0; for(int i=1;i<nnxt;i++) if(nxt[i].score<nxt[w].score) w=i;
  if (s->score > nxt[w].score) nxt[w]=*s;
}
static void dfs(int w, int pi, const St *ps, int j, int t, int *p){
  int L=lens[w];
  if (j==L){
    St s; s.score = ps->score + lmword(p,L); s.parent=pi; memcpy(s.pw,p,sizeof(int)*L);
    if (mode==2){ memcpy(s.binv,ps->binv,M); s.t=t; }
    else { int e=(t+4)%5; for(int x=0;x<M;x++) s.binv[x]=si[gi[e][ps->binv[x]]]; s.t = (mode==1)?0:t; }
    push(&s); return;
  }
  int i=st[w]+j, c=cip[i], x=ps->binv[c], prevc = i>0?cip[i-1]:-1;
  if (c!=prevc){ p[j]=gi[t][x]; dfs(w,pi,ps,j+1,(t+1)%5,p); }
  if (prevc>=0){ int t1=(t+1)%5; int pd=gi[t1][x]; if (gf[t][pd]==ps->binv[prevc]){ p[j]=pd; dfs(w,pi,ps,j+1,(t+2)%5,p); } }
}
int main(int argc, char **argv){
  const char *dir = getenv("KWDIR") ? getenv("KWDIR") : ".";
  char fn[1024]; FILE *f=fopen(argv[1],"r");
  if (fscanf(f,"%d",&nw)!=1) return 1; N=0; for(int w=0;w<nw;w++){ if(fscanf(f,"%d",&lens[w])!=1) return 1; st[w]=N; N+=lens[w]; }
  for(int i=0;i<N;i++) if(fscanf(f,"%d",&cip[i])!=1) return 1; fclose(f);
  if (argc>4) B=atoi(argv[4]); int nwu = nw; if (argc>5 && atoi(argv[5])>0 && atoi(argv[5])<nw) nwu=atoi(argv[5]);
  sprintf(fn,"%s/A.bin",dir); f=fopen(fn,"rb"); fseek(f,0,SEEK_END); NA=ftell(f)/M; rewind(f); Aall=malloc((size_t)NA*M); if(fread(Aall,1,(size_t)NA*M,f)!=(size_t)NA*M) return 1; fclose(f);
  Ainv=malloc((size_t)NA*M); for(long a=0;a<NA;a++) for(int x=0;x<M;x++) Ainv[a*M+Aall[a*M+x]]=x;
  sprintf(fn,"%s/G.bin",dir); f=fopen(fn,"rb"); fseek(f,0,SEEK_END); NG=ftell(f)/M; rewind(f); G=malloc((size_t)NG*M); if(fread(G,1,(size_t)NG*M,f)!=(size_t)NG*M) return 1; fclose(f);
  LM=malloc(sizeof(int16_t)*V*V*V*V); sprintf(fn,"%s/lm16.bin",dir); f=fopen(fn,"rb"); if(fread(LM,2,V*V*V*V,f)!=V*V*V*V) return 1; fclose(f);
  cur=malloc(B*sizeof(St)); nxt=malloc(B*sizeof(St)); hist=malloc(nwu*sizeof(St*)); nhist=malloc(nwu*sizeof(int));
  for (int w=0;w<nwu;w++) hist[w]=malloc(B*sizeof(St));
  FILE *fk=fopen(argv[2],"r"), *fo=fopen(argv[3],"w"); char line[4096];
  while (fgets(line,sizeof line,fk)){
    if (line[0]=='#') continue; int b,g,s; if (sscanf(line,"%d %d %d %d",&mode,&b,&g,&s)!=4) continue;
    for(int x=0;x<M;x++) gf[0][x]=x; for(int k=1;k<5;k++) for(int x=0;x<M;x++) gf[k][x]=G[(size_t)g*M+gf[k-1][x]];
    for(int k=0;k<5;k++) for(int x=0;x<M;x++) gi[k][gf[k][x]]=x;
    if (mode!=2) for(int x=0;x<M;x++) si[x]=Ainv[(size_t)s*M+x];
    St s0; s0.t=0; memcpy(s0.binv, Ainv+(size_t)b*M, M); s0.score=0; s0.parent=-1;
    ncur=1; cur[0]=s0; int p[64]; int dead=0;
    for (int w=0; w<nwu; w++){
      nnxt=0; for (int k=0;k<ncur;k++) dfs(w,k,&cur[k],0,cur[k].t,p);
      if (!nnxt){ dead=w+1; break; }
      memcpy(hist[w],nxt,nnxt*sizeof(St)); nhist[w]=nnxt; St *tmp=cur; cur=nxt; nxt=tmp; ncur=nnxt;
    }
    if (dead){ fprintf(fo,"%d %d %d %d DEAD at word %d rune %d\n",mode,b,g,s,dead-1,st[dead-1]); continue; }
    int bw=0; for(int k=1;k<ncur;k++) if(cur[k].score>cur[bw].score) bw=k;
    static int out[MAXN]; int nsym=0; for(int w=0;w<nwu;w++) nsym+=lens[w]+1;
    int idx=bw; for (int w=nwu-1; w>=0; w--){ St *h=&hist[w][idx]; memcpy(out+st[w],h->pw,sizeof(int)*lens[w]); idx=h->parent; }
    fprintf(fo,"%d %d %d %d %ld %d :", mode,b,g,s,cur[bw].score,nsym);
    for (int i=0;i<st[nwu-1]+lens[nwu-1];i++) fprintf(fo," %d",out[i]); fprintf(fo,"\n");
  }
  fclose(fo); return 0;
}
