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

int main(int argc, char *argv[])
{

    char buffer[BUFSIZ];                          //Buffer of 8192 char
    int sockfd = socket(PF_INET, SOCK_STREAM, 0); //create a new tcp socket
    if (sockfd < 0)
        stop("socket()");
    if (argc != 4)
        stop("arg");
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));             //initialize the serv_addr
    serv_addr.sin_family = AF_INET;                   //server address : ipv4
    if (inet_aton(argv[1], &serv_addr.sin_addr) == 0) // puts the ipv4 address in binary and stores it in serv_addr.sin_addr
        stop("inet_aton()");
    serv_addr.sin_port = htons(atoi(argv[2]));                                         // atoi : cast argv[2] in int htons() : puts the port in binary and saves it in serv_addr.sin_port
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(struct sockaddr)) == -1) // tries to connect to the server
        stop("connect()");
    sprintf(buffer, "%s\n", argv[3]);                  // add a \n at the end of the message
    if (send(sockfd, buffer, strlen(buffer), 0) == -1) // send the message
        stop("send()");
    if (close(sockfd) == -1) // close file descriptor
        stop("close");

    exit(EXIT_SUCCESS);
}