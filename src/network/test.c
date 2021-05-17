#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    char msg[] = "test abcd efgh";
    char delim[] = " ";
    printf("%s\n", strtok(msg, delim));
    printf("%s\n", strtok(NULL, delim));
    return 0;
}