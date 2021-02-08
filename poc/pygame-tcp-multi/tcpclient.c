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

    char buffer[BUFSIZ];
    int tmp_port;
    int sockfd = socket(PF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        stop("socket()");
    if (argc != 3)
        stop("arg");
    struct sockaddr_in cli_addr;
    bzero(&cli_addr, sizeof(cli_addr));

    cli_addr.sin_family = AF_INET;
    if (inet_aton("127.0.0.1", &cli_addr.sin_addr) == 0)
        stop("inet_aton()");
    tmp_port = atoi(argv[1]);
    cli_addr.sin_port = htons(tmp_port);
    if (connect(sockfd, (struct sockaddr *)&cli_addr, sizeof(struct sockaddr)) == -1)
        stop("connect()");
    sprintf(buffer, "%s\n", argv[2]);
    if (send(sockfd, buffer, strlen(buffer), 0) == -1)
        stop("send()");
    if (close(sockfd) == -1)
        stop("close");

    exit(EXIT_SUCCESS);
}