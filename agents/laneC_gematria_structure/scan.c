#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static int inv29[29];
static int8_t TADD_M[29][29], TADD_P[29][29], TMUL_I[29][29], TMUL[29][29], TRAW_M[29][29], TRAW_P[29][29];
static int inited=0;
static void init(void){
  if(inited) return; inited=1;
  for(int a=1;a<29;a++) for(int b=1;b<29;b++) if((a*b)%29==1) inv29[a]=b;
  for(int x=0;x<29;x++) for(int k=0;k<29;k++){
    if(x==0){TADD_M[x][k]=28;TADD_P[x][k]=28;}
    else{ TADD_M[x][k]=(((x-1-k)%28)+28)%28; TADD_P[x][k]=(((x-1+k)%28)+28)%28; }
    if(k==0){TMUL_I[x][k]=-1;TMUL[x][k]=-1;} else {TMUL_I[x][k]=(x*inv29[k])%29; TMUL[x][k]=(x*k)%29;}
    TRAW_M[x][k]=(((x-k)%29)+29)%29; TRAW_P[x][k]=(x+k)%29;
  }
}
/* X: n values 0..28 (increments or raw runes); idx: n int32 key index (-1: skip); K: L values 0..28.
   form: 0 add-minus,1 add-plus,2 mul-inv,3 mul,4 raw-minus,5 raw-plus
   cyc: wrap idx+o modulo L; else skip if out of range.
   For o in [omin,omax]: ioc[o-omin], nv[o-omin] */
void scan(const uint8_t*X,const int32_t*idx,int n,const uint8_t*K,int L,int cyc,int omin,int omax,int form,int rm,double*ioc,int*nv){
  init();
  const int8_t (*T)[29];
  switch(form){case 0:T=TADD_M;break;case 1:T=TADD_P;break;case 2:T=TMUL_I;break;case 3:T=TMUL;break;case 4:T=TRAW_M;break;default:T=TRAW_P;}
  for(int o=omin;o<=omax;o++){
    int cnt[29]; memset(cnt,0,sizeof(cnt)); int m=0;
    int base=0; if(rm){ int jb=o-1; if(cyc){jb%=L; if(jb<0) jb+=L;} if(jb>=0&&jb<L) base=K[jb]; }
    for(int i=0;i<n;i++){
      int j=idx[i]; if(j<0) continue; j+=o;
      if(cyc){ j%=L; if(j<0) j+=L; } else if(j<0||j>=L) continue;
      int kv=K[j]; if(rm){ kv=(kv-base)%rm; if(kv<0) kv+=rm; } int s=T[X[i]][kv]; if(s<0) continue;
      cnt[s]++; m++;
    }
    double sum=0; for(int s=0;s<29;s++) sum+=(double)cnt[s]*(cnt[s]-1);
    ioc[o-omin]= m>1 ? 29.0*sum/((double)m*(m-1)) : 0.0;
    nv[o-omin]=m;
  }
}
/* conditional coincidence: group by V (int32 >=0, -1 skip), X values 0..28 excluding zeros handled by caller (skip x==0).
   returns coincidences and pairs in groups; also number of groups */
void condcoinc(const uint8_t*X,const int32_t*V,int n,int maxv,double*coinc,double*pairs){
  int *cnt=(int*)calloc((size_t)(maxv+1)*29,sizeof(int)); 
  double c=0,p=0;
  for(int i=0;i<n;i++){ if(V[i]<0||X[i]==0) continue; cnt[(size_t)V[i]*29+X[i]]++; }
  for(int v=0;v<=maxv;v++){ int t=0; double cc=0; for(int s=1;s<29;s++){int a=cnt[(size_t)v*29+s]; t+=a; cc+=(double)a*(a-1);} c+=cc; p+=(double)t*(t-1); }
  free(cnt); *coinc=c; *pairs=p;
}
