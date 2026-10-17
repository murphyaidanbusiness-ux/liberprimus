// Smith-Waterman (match +1, mismatch -2, linear gap -2) of 32 independent integer targets
// (int16 lanes, AVX-512BW) against one long library sequence.
// Library symbol 0 = text separator: DP is reset and per-text maxima are emitted.
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <immintrin.h>
void sw32(const uint8_t* L, int64_t n, const int16_t* T, int m, int ntext,
          int16_t* best, int32_t* bestj){
    __m512i* Tv=(__m512i*)aligned_alloc(64,64*(size_t)m);
    __m512i* H=(__m512i*)aligned_alloc(64,64*(size_t)m);
    memcpy(Tv,T,64*(size_t)m);
    const __m512i zero=_mm512_setzero_si512(), two=_mm512_set1_epi16(2), m2=_mm512_set1_epi16(-2), one=_mm512_set1_epi16(1);
    for(int i=0;i<m;i++) H[i]=zero;
    __m512i bst=zero; int32_t bj[32]; for(int l=0;l<32;l++) bj[l]=-1;
    int t=0;
    for(int64_t j=0;j<n;j++){
        int c=L[j];
        if(c==0){
            if(t<ntext){ int16_t b[32]; _mm512_storeu_si512(b,bst); for(int l=0;l<32;l++){best[t*32+l]=b[l]; bestj[t*32+l]=bj[l];} }
            t++; bst=zero; for(int l=0;l<32;l++) bj[l]=-1;
            for(int i=0;i<m;i++) H[i]=zero;
            continue;
        }
        __m512i cv=_mm512_set1_epi16((int16_t)c);
        __m512i diag=zero, up=zero, cm=zero;
        for(int i=0;i<m;i++){
            __mmask32 eq=_mm512_cmpeq_epi16_mask(Tv[i],cv);
            __m512i s=_mm512_mask_blend_epi16(eq,m2,one);
            __m512i left=H[i];
            __m512i h=_mm512_add_epi16(diag,s);
            h=_mm512_max_epi16(h,_mm512_sub_epi16(left,two));
            h=_mm512_max_epi16(h,_mm512_sub_epi16(up,two));
            h=_mm512_max_epi16(h,zero);
            diag=left; H[i]=h; up=h;
            cm=_mm512_max_epi16(cm,h);
        }
        __mmask32 gt=_mm512_cmpgt_epi16_mask(cm,bst);
        if(gt){ for(int l=0;l<32;l++) if(gt>>l&1) bj[l]=(int32_t)j; bst=_mm512_max_epi16(cm,bst); }
    }
    if(t<ntext){ int16_t b[32]; _mm512_storeu_si512(b,bst); for(int l=0;l<32;l++){best[t*32+l]=b[l]; bestj[t*32+l]=bj[l];} }
    free(Tv); free(H);
}
// scalar SW with traceback-free score matrix for a small window: returns full H (m+1)x(w+1) int16
void swmat(const uint8_t* W, int w, const int16_t* T, int m, int16_t* Hm){
    memset(Hm,0,sizeof(int16_t)*(m+1)*(w+1));
    for(int i=1;i<=m;i++) for(int j=1;j<=w;j++){
        int s=(T[i-1]==W[j-1])?1:-2;
        int h=Hm[(i-1)*(w+1)+j-1]+s, a=Hm[(i-1)*(w+1)+j]-2, b=Hm[i*(w+1)+j-1]-2;
        if(a>h)h=a; if(b>h)h=b; if(h<0)h=0; Hm[i*(w+1)+j]=h;
    }
}
