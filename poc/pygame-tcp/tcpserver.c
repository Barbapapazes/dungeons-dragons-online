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
#define BUFSIZE 5

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{

    char buffer[BUFSIZE + 1];
    int n;
    int newsockfd;
    int sockfd = socket(PF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        stop("socket()");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));

    serv_addr.sin_family = AF_INET;
    if (inet_aton("127.0.0.1", &serv_addr.sin_addr) == 0)
        stop("inet_aton()");
    serv_addr.sin_port = htons(1234);
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
        stop("bind()");
    if (listen(sockfd, 20000) == -1)
        stop("listen()");
    int size = sizeof(serv_addr);
    while (1)
    {
        if ((newsockfd = accept(sockfd, (struct sockaddr *)&serv_addr, (socklen_t *)&size)) == -1)
            stop("accept()");
        if ((n = recv(newsockfd, buffer, BUFSIZE, 0)) == -1)
            stop("recv()");
        do
        {
            if ((n == -1))
                stop("recv()");
            buffer[n] = '\0';
            write(STDOUT_FILENO, buffer, strlen(buffer));
        } while ((n = recv(newsockfd, buffer, BUFSIZE, 0)));
    }
    if ((close(newsockfd)))
        stop("close");
    if ((close(sockfd)))
        stop("close");
    exit(EXIT_SUCCESS);
}