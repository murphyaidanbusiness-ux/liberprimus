#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

/* big-endian block -> base-B digits, LSD first, ndig digits per block (+ number of significant digits) */
void digits_blocks(const uint8_t* data, int blocklen, int nblocks, int base, int ndig, uint8_t* out, uint8_t* nsig){
    uint8_t* b = (uint8_t*)malloc(blocklen);
    for(int k=0;k<nblocks;k++){
        memcpy(b, data+(size_t)k*blocklen, blocklen);
        int start=0; /* first nonzero byte */
        int sig=0;
        for(int d=0; d<ndig; d++){
            unsigned rem=0;
            while(start<blocklen && b[start]==0) start++;
            for(int x=start;x<blocklen;x++){
                unsigned cur = rem*256u + b[x];
                b[x] = (uint8_t)(cur/base);
                rem = cur % base;
            }
            out[(size_t)k*ndig+d]=(uint8_t)rem;
            if(rem) sig=d+1;
        }
        nsig[k]=(uint8_t)sig;
    }
    free(b);
}

/* modes bitmask: 1 = continuous, 2 = restart(koff each page), 4 = per-page key offsets pkoff[page].
   trial index t = (m*napps + a)*3 + modeidx(0,1,2)
*/
void sweep(const uint8_t* c, const uint8_t* pstart, const int16_t* pid, int n, int npages,
           const uint8_t* keys, int KL, int nmaps, const uint8_t* mapq,
           const uint8_t* tabs, int napps, const uint8_t* appq, const uint8_t* appprev, const uint8_t* appconv,
           int koff, int prefix_len, int modes, const int32_t* pkoff,
           float* out_whole, float* out_prefix, float* pmax, int64_t* pmaxcfg, int64_t cfg_base, uint32_t* hist, float hist_lo, float hist_step, int hist_n)
{
    /* page boundaries */
    int* pb = (int*)malloc(sizeof(int)*(npages+1)); int np_=0;
    for(int i=0;i<n;i++) if(pstart[i]) pb[np_++]=i;
    pb[np_]=n;
    uint8_t* Dp = (uint8_t*)malloc(n); /* chain increments */
    for(int pg=0;pg<np_;pg++){ int prev=0; for(int i=pb[pg];i<pb[pg+1];i++){ int d=c[i]-prev; if(d<0) d+=29; Dp[i]=(uint8_t)d; prev=c[i]; } }
    uint8_t* Dr = (uint8_t*)malloc(n); memcpy(Dr,c,n);
    for(int m=0;m<nmaps;m++){
        const uint8_t* key = keys + (size_t)m*KL;
        for(int a=0;a<napps;a++){
            for(int md=0; md<3; md++){
                int64_t t = ((int64_t)m*napps + a)*3 + md;
                if(!((modes>>md)&1) || mapq[m]!=appq[a]){ out_whole[t]=-1; out_prefix[t]=-1; continue; }
                const uint8_t* T = tabs + (size_t)a*841;
                int useprev = appprev[a], conv = appconv[a];
                const uint8_t* D = useprev? Dp : Dr;
                int j = koff;
                uint32_t cw[29]; uint32_t cpf[29];
                memset(cw,0,sizeof cw); memset(cpf,0,sizeof cpf);
                int got_pf=0;
                for(int pg=0;pg<np_;pg++){
                    int s0=pb[pg], s1=pb[pg+1];
                    if(md==1) j=koff; else if(md==2) j=pkoff[pg]+koff;
                    uint32_t cp[29]; memset(cp,0,sizeof cp);
                    int plen=s1-s0;
                    if(conv && useprev){
                        for(int i=s0;i<s1;i++){
                            int d=D[i]; int jj= j<KL? j : j-KL;
                            cp[T[d*29+key[jj]]]++;
                            j += (d!=0);
                        }
                    } else {
                        for(int i=s0;i<s1;i++){
                            int d=D[i]; int jj= j<KL? j : j-KL;
                            cp[T[d*29+key[jj]]]++;
                            j++;
                        }
                    }
                    double s=0; for(int q=0;q<29;q++){ s+= (double)cp[q]*((double)cp[q]-1.0); cw[q]+=cp[q]; }
                    if(plen>1){
                        float ioc=(float)(29.0*s/((double)plen*(plen-1.0)));
                        if(ioc>pmax[pg]){pmax[pg]=ioc; pmaxcfg[pg]=cfg_base+t;}
                    }
                    if(!got_pf && s1>=prefix_len){ memcpy(cpf,cw,sizeof cw); got_pf=1; }
                }
                if(!got_pf) memcpy(cpf,cw,sizeof cw);
                double s=0; for(int q=0;q<29;q++) s+=(double)cw[q]*((double)cw[q]-1.0);
                float iw=(float)(29.0*s/((double)n*(n-1.0)));
                double s2=0; double npf=0; for(int q=0;q<29;q++){ s2+=(double)cpf[q]*((double)cpf[q]-1.0); npf+=cpf[q]; }
                float ipf=(float)(29.0*s2/(npf*(npf-1.0)));
                out_whole[t]=iw; out_prefix[t]=ipf;
                if(hist){ int bi=(int)((iw-hist_lo)/hist_step); if(bi<0)bi=0; if(bi>=hist_n)bi=hist_n-1; hist[bi]++; }
            }
        }
    }
    free(pb); free(Dp); free(Dr);
}

/* decode one config, output p stream */
void decode_one(const uint8_t* c, const uint8_t* pstart, const int16_t* pid, int n,
                const uint8_t* key, int KL, const uint8_t* T, int useprev, int conv, int koff, int mode, const int32_t* pkoff, uint8_t* out){
    int j=koff, prev=0;
    for(int i=0;i<n;i++){
        if(pstart[i]){ prev=0; if(mode==1) j=koff; else if(mode==2) j=pkoff[pid[i]]+koff; }
        int cc=c[i]; int D;
        if(useprev){ D=cc-prev; if(D<0) D+=29; prev=cc;} else D=cc;
        int jj=j<KL?j:j-KL;
        out[i]=T[D*29+key[jj]];
        if(!(conv==1 && useprev && D==0)) j++;
    }
}
