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
#include <netinet/tcp.h>
#include "serialization.h"

/**
 * @brief Stops the program with a message
 * 
 * @param msg the message printed when program stops
 */
void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}


int main(int argc, int argv){

    //TCP Socket 
    int sockfd = socket(AF_INET,SOCK_STREAM,0);
    if (sockfd == -1)
        stop("socket()");

    //Hostname
    char * hostname = "127.0.0.1";
    //Sockadd_in struct
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    //Setting up
    serv_addr.sin_family = AF_INET; 
    inet_aton(hostname, &serv_addr.sin_addr); 
    serv_addr.sin_port = htons(1234);

    //Binding
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ==-1) {
        close(sockfd);
        stop("Error when binding\n");
    }

    //Maximum 5 clients
    if (listen(sockfd, 5)==-1) {
        close(sockfd);
        stop("Error when listening\n");
    }

    //Client structure
    struct sockaddr_in client_addr;
    bzero(&client_addr, sizeof(client_addr));
    int client_len = sizeof(client_addr);
    int new_sockfd = 0;

    //Accepting
    if ((new_sockfd = accept(sockfd, (struct sockaddr *)&client_addr, (socklen_t *)&client_len))==-1) {
        close(sockfd); 
        stop("Error when accepting\n");
    }

    //Receiving packets
    int receipt=0;
    char buff[1000];
    while(1) {

        //Error when receiving
        if ((receipt = recv(new_sockfd, &buff, sizeof(buff) * 2, 0))==-1)
        {
            close(new_sockfd);
            stop("Error when receiving packet\n");
        }
        //Client disconnects
        else if (receipt==0){
            printf("Disconnected client\n");
            close(sockfd);
            close(new_sockfd);
            break;
        }
        //Else let's read the message
        else {
            buff[receipt]='\0';
            /* Use these lines if you want to explore received bytes only 
            for (int i=0; i<20; i++) {
                printf("buff[%d] = %02X\n", i, (unsigned char)buff[i]);
            }*/
            game_packet g = deserialize_packet(buff);
            printf("Received packet : %i %i %s\n", g.player_id, g.action, g.data);        
            receipt=0;
        }
    }

    close(sockfd);
    close(new_sockfd);
    return 0;
}