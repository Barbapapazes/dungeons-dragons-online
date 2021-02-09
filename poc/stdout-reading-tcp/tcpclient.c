#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <strings.h>
#include <arpa/inet.h>

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{
    int sockfd = socket(PF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        stop("socket()");

    struct sockaddr_in cli_addr;
    bzero(&cli_addr, sizeof(cli_addr));

    cli_addr.sin_family = AF_INET;
    if (inet_aton("127.0.0.1", &cli_addr.sin_addr) == 0)
        stop("inet_aton()");
    cli_addr.sin_port = htons(1234);
    if (connect(sockfd, (struct sockaddr *)&cli_addr, sizeof(struct sockaddr)) == -1)
        stop("connect()");
    if (send(sockfd, "PING\n", 5, 0) == -1)
        stop("send()");
    if (close(sockfd) == -1)
        stop("close");

    exit(EXIT_SUCCESS);
}