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

    if (argc != 2)
        stop("incorrect number of arg");

    int tmp_port=atoi(argv[1]);
    char buffer[BUFSIZ];
    //Socket
    int sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd == -1)
        stop("socket()");
        
    //Server
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    //Setting up
    serv_addr.sin_family = AF_INET;
    if (inet_aton("127.0.0.1", &serv_addr.sin_addr) == 0)
    {

        close(sockfd);
        stop("inet_aton()");
    }
    serv_addr.sin_port = htons(tmp_port);

    //Binding
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
    {
        close(sockfd);
        stop("Error when binding\n");
    }

    int receipt;
    struct sockaddr_in client_addr;
    bzero(&client_addr, sizeof(client_addr));
    int client_len = sizeof(client_addr);
    while (1)
    {

        if ((receipt = recvfrom(sockfd, &buffer, sizeof(buffer), 0, (struct sockaddr *)&client_addr, (socklen_t *)&client_len)) == -1)
        {
            close(sockfd);
            stop("Error when receiving packet\n");
        }

        if (receipt != 0)
        {
            buffer[receipt] = '\0';
            write(STDOUT_FILENO, buffer, receipt);

            receipt = 0;
        }
    }

    return 0;
}