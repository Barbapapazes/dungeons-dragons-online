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
#define MAX_USER_INPUT 216

/**
 * @brief Stops the program printing an error message
 * 
 * @param msg the message to print
 */
void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}


int main(int argc, char ** argv){

    //UDP socket
    int sockfd = socket(PF_INET,SOCK_DGRAM,0);
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

    char buff[1024];
    int receipt;
    int serv_len = sizeof(serv_addr);

    if (sendto(sockfd, "PING\n", 5, 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ==-1)
    {
        close(sockfd);
        stop("Error when sending\n");
    }


    return 0;   
}

