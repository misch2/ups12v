#include <stdio.h>
#include <stdlib.h>
#include "esp_crt_bundle.h"
const unsigned char _binary_x509_crt_bundle_start[]={0};
const unsigned char _binary_x509_crt_bundle_end[]={0};
extern int esp_crt_verify_callback(void*,mbedtls_x509_crt*,int,uint32_t*);
int main(int argc,char**argv){
    unsigned char bundle[4096]; uint32_t flags; mbedtls_x509_crt chain;
    if(argc!=3)return 2;
    FILE*f=fopen(argv[1],"rb"); if(!f)return 3; size_t n=fread(bundle,1,sizeof(bundle),f);fclose(f);
    if(esp_crt_bundle_set(bundle,n)!=0)return 4;
    mbedtls_x509_crt_init(&chain); if(mbedtls_x509_crt_parse_file(&chain,argv[2])!=0)return 5;
    int good=mbedtls_x509_crt_verify(&chain,NULL,NULL,"misch2.github.io",&flags,esp_crt_verify_callback,NULL);
    printf("SDK compact bundle, real Pages chain: result=%d flags=0x%x\n",good,(unsigned)flags);
    int bad=mbedtls_x509_crt_verify(&chain,NULL,NULL,"unrelated.invalid",&flags,esp_crt_verify_callback,NULL);
    printf("Wrong hostname rejection: result=%d flags=0x%x\n",bad,(unsigned)flags);
    mbedtls_x509_crt_free(&chain); return good!=0 || bad==0;
}
