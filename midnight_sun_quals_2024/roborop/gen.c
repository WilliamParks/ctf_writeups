#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/mman.h>
#include <fcntl.h> 

int main(int argc, char *argv[]) {
    if(argc != 2) {
        printf("Usage: %s <number>\n", argv[0]);
        return 1;
    }

    uint32_t n = strtol(argv[1], NULL, 16);
    printf("n = 0x%x\n", n);
    srand(n);

    int * foo = mmap(0, 0x10000000, 2, 0x22, -1, 0);

    for(int i = 0; i < 0x3ffffff; i++) {
        foo[i] = rand();
    }

    // Validate against binary
    // for(int i = 0; i < 10; i++) {
    //     printf("foo[%d] = %x\n", i, foo[i]);
    // }

    FILE* f = fopen("gen.bin", "wb");
    fwrite(foo, 1, 0x10000000, f);

    return 0;
}