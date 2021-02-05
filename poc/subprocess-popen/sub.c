#include <stdio.h> 
#include<stdlib.h>
#include <unistd.h>

int main() 
{ 
  printf("hello\n");
  fflush(stdout);

  sleep(2);

  printf("world");

  return 0; 
}  