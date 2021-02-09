#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{

    if (argc != 4)
        stop("incorrect number of arg");

    char buffer[BUFSIZ];
    int tmp_port = atoi(argv[2]);
    //Socket
    int sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd == -1)
        stop("socket()");

    //Server
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    //Setting up serv_addr
    serv_addr.sin_family = AF_INET;
    if (inet_aton(argv[1], &serv_addr.sin_addr) == 0){
        close(sockfd);
        stop("inet_aton()");}
    serv_addr.sin_port = htons(tmp_port);

    //Binding
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
    {
        close(sockfd);
        stop("Error when binding\n");
    }
    
    sprintf(buffer, "%s\n", argv[3]);
    if (sendto(sockfd, buffer, strlen(buffer), 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
    {
        close(sockfd);
        stop("Error when sending\n");
    }

    return 0;
}