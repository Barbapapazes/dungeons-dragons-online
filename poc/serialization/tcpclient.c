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

int main(int argc, char**argv){

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
    int serv_len = sizeof(serv_addr);

    //Binding
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ==-1) {
        close(sockfd);
        stop("Error when binding\n");
    }
    
    //Creating a game packet 
    game_packet packet;
    packet.player_id = 1;
    packet.action = 2;
    packet.data = malloc(sizeof(char)*6);
    strcpy(packet.data, "1;3;6");
    printf("Before serialization :\t%i %i %s\n", packet.player_id, packet.action, packet.data);

    //Serialization of the packet     
    unsigned char* s_packet = serialize_packet(packet);
    /* Use this part if you want to explore the serialized data in bytes
    for (int i=0; i<20; i++) {
    printf("s_packet[%d] = %02X\n", i, (unsigned char)s_packet[i]);
    }
    */

    //Deserialization of the packet 
    game_packet base_packet = deserialize_packet(s_packet);
    printf("After deserialization :\t%i %i %s\n", base_packet.player_id, base_packet.action, base_packet.data);

    //Sending the packet [IMPORTANT : sizeof(packet) is *4]
    if (send(sockfd, s_packet, sizeof(s_packet)*4, 0) ==-1)
    {
        close(sockfd);
        stop("Error when sending\n");
    }
        

    close(sockfd);
    return 0;
}