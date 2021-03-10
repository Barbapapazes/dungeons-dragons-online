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


char* serialize_packet(game_packet g)
{
    //Calculating data length to define our packet size
    int data_len = strlen(g.data);
    int packet_size = 3*sizeof(int) + data_len*sizeof(char);

    char* s_packet;
    s_packet = malloc(sizeof(char)*(packet_size+1));

    //First two integers
    memcpy(s_packet, &g.player_id, sizeof(int));
    memcpy(s_packet+sizeof(int), &g.action, sizeof(int));

    //String + size of the string 
    memcpy(s_packet+2*sizeof(int), &data_len, sizeof(int));
    memcpy(s_packet+3*sizeof(int), g.data, data_len);


    s_packet[packet_size] = '\0'; 

    return s_packet;
}



game_packet deserialize_packet(unsigned char *s_packet) 
{
    game_packet g;

    //Getting back the first attributes
    memcpy(&g.player_id, s_packet, sizeof(int));
    memcpy(&g.action, s_packet+sizeof(int), sizeof(int));

    //Getting back the string size and string
    int data_len;
    memcpy(&data_len, s_packet+2*sizeof(int), sizeof(int));
    g.data = malloc(sizeof(char)*(data_len+1));
    memcpy(g.data, s_packet+3*sizeof(int), data_len);

    g.data[data_len]='\0';

    return g;
}