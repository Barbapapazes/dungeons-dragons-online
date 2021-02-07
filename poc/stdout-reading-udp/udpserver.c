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

/**
 * @brief Stops the program with a message
 * 
 * @param msg the message to print
 */
void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{

    //UDP Socket
    int sockfd = socket(PF_INET, SOCK_DGRAM, 0);
    if (sockfd == -1)
        stop("socket()");

    //Host name
    char *hostname = "127.0.0.1";
    //Server
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    //Setting up
    serv_addr.sin_family = AF_INET;
    inet_aton(hostname, &serv_addr.sin_addr);
    serv_addr.sin_port = htons(1234);

    //Binding
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
    {
        close(sockfd);
        stop("Error when binding\n");
    }

    char buff[1000];
    int receipt;
    struct sockaddr_in client_addr;
    bzero(&client_addr, sizeof(client_addr));
    int client_len = sizeof(client_addr);

    //Sending/Receiving requests
    while (1)
    {

        //If the server receives something
        if ((receipt = recvfrom(sockfd, &buff, sizeof(buff), 0, (struct sockaddr *)&client_addr, &client_len)) == -1)
        {
            close(sockfd);
            stop("Error when receiving packet\n");
        }

        //If the information received is not empty
        if (receipt != 0)
        {
            buff[receipt] = '\0';

            //Writing on STDOUT the received message
            write(STDOUT_FILENO, buff, strlen(buff));

            receipt = 0;
            return 0;
        }
    }

    return 0;
}
