#include <stdio.h>
#include <stdlib.h>
int main(int argc,char**argv){ unsigned s=(unsigned)strtoul(argv[1],0,10); int n=atoi(argv[2]); int i;
 srand(s); for(i=0;i<n;i++) printf("%d ", rand()%29); printf("\n");
 srand(s); for(i=0;i<n;i++) printf("%d ", (int)(29*(rand()/(RAND_MAX+1.0)))); printf("\n");
 srand(s); for(i=0;i<n;i++) printf("%d ", rand()/(RAND_MAX/29+1)); printf("\n");
 srand48((long)s); for(i=0;i<n;i++) printf("%d ", (int)(drand48()*29)); printf("\n");
 srand(s); for(i=0;i<n;i++) printf("%d ", rand()); printf("\n");
 return 0;}
