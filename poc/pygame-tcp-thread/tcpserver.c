#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <netdb.h>
#include <fcntl.h>
#include <arpa/inet.h>

#define RETURN_CHILD 256

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{

    char buffer[BUFSIZ];                          //Buffer of 8192 char
    int n, childreturn, childpid;                 //counter of char received, return value of the child, pid used for fork
    int newsockfd;                                //file descriptor that will contains the client socket
    int sockfd = socket(PF_INET, SOCK_STREAM, 0); //server socket where client connects.
    if (sockfd < 0)
        stop("socket()");
    if (argc != 3)
        stop("argc");
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr)); //initialize the serv_addr

    serv_addr.sin_family = AF_INET;                   //server address : ipv4
    if (inet_aton(argv[2], &serv_addr.sin_addr) == 0) // puts the ipv4 address in binary and stores it in serv_addr.sin_addr
        stop("inet_aton()");
    serv_addr.sin_port = htons(atoi(argv[1])); // atoi : cast argv[2] in int htons() : puts the port in binary and saves it in serv_addr.sin_port
    int true = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &true, sizeof(int));         // avoid the bind error by allowing the reuse of port for socket
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) // associate to sockfd serv_addr
        stop("bind()");
    if (listen(sockfd, 20000) == -1) //allows to queue up to 20000 connexions to the server
        stop("listen()");
    int size = sizeof(serv_addr);
    while (1)
    {
        if ((newsockfd = accept(sockfd, (struct sockaddr *)&serv_addr, (socklen_t *)&size)) == -1) //accept a new connection
            stop("accept()");
        if ((childpid = fork()) == 0) //fork the program so we can handle multiple tcp connection
        {
            close(sockfd); //if we are in child the sockfd is no more needed so we close it

            while ((n = recv(newsockfd, buffer, BUFSIZ, 0)) > 0) //Wait to receive a message
            {
                if ((n == -1))
                    stop("recv()");
                if (strcmp(buffer, "!server_end\n") == 0) //if the message received is the end close the socket and return a special value that can only be return in this case
                {
                    if ((close(newsockfd))) //close the attributed socket to avoid bind error
                        stop("close");
                    return 1;
                }
                buffer[n] = '\0';
                write(STDOUT_FILENO, buffer, strlen(buffer)); //write the message in STDOUT_FILENO
            }
            if ((close(newsockfd))) //close the attributed socket to avoid bind error
                stop("close");
            return 0; // if the message has not been fully received reiterate the process
        }
        else
        {
            wait(&childreturn); //wait for child and put it's return value in childreturn then test if return value is equal to 1
            if (childreturn == RETURN_CHILD)
            {
                break;
            }
        }
    }
    if ((close(newsockfd))) //close the attributed socket to avoid bind error
        stop("close");

    exit(EXIT_SUCCESS);
}