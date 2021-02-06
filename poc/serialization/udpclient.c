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

void stop(char *msg); 

/**
 * @brief The structure used as a packet to send to the server
 * 
 */
typedef struct  {
    int player_id;
    int action;
    char *user_input;
} game_struct;

/**
 * @brief Serializes our structure (which means transforms it into a char)
 * 
 * @param g the game structure we want to serialize
 * @return char* the serialized char *
 */
char* serialize(game_struct g)
{
    int ui_len = strlen(g.user_input); //ui stands for "user_input"
    
    //Global size of the structure
    int size = 3*sizeof(int)+ui_len;
    char * buffer = malloc(sizeof(char) * (size+1));

    //Copy the first two attributes
    memcpy(buffer, &g.player_id, sizeof(int));
   
    memcpy(buffer+sizeof(int), &g.action, sizeof(int));
    //Copying size and string
    memcpy(buffer+2*sizeof(int), &ui_len, sizeof(int));
    memcpy(buffer+3*sizeof(int), g.user_input, ui_len);

    buffer[size] = '\0';

    return buffer;
}

/**
 * @brief This functions is used to deserialize the char* we sent in order to 
 *  transform it in a structure which is the same as before
 * @param buffer the received char buffer
 * @return game_struct* 
 */
game_struct deserialize(char * buffer)
{
    game_struct g;

    //Getting back the first two attributes
    memcpy(&g.player_id, buffer, sizeof(int));
    memcpy(&g.action, buffer+sizeof(int), sizeof(int));

    //Getting string size and string
    int ui_len;
    memcpy(&ui_len, buffer+2*sizeof(int), sizeof(int));
    g.user_input = malloc(sizeof(char)*(ui_len+1));
    memcpy(g.user_input, buffer+3*sizeof(int), ui_len);

    g.user_input[ui_len]='\0';

    return g;
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

    game_struct packet;
    packet.player_id = 1;
    packet.action = 4;
    char str[5] = "1;2;9";
    packet.user_input = malloc(strlen(str)+1);
    strcpy(packet.user_input, str);

    printf("Original : %i%i%s\n", packet.player_id, packet.action, packet.user_input);
    char* s_packet = serialize(packet);
    printf("Serialized : %i\n", s_packet); //apparently not printable as a %s
    game_struct d_packet = deserialize(s_packet);
    printf("Deserialized : %i%i%s\n", d_packet.player_id, d_packet.action, d_packet.user_input);

    if (sendto(sockfd, s_packet, sizeof(s_packet), 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ==-1)
    {
        close(sockfd);
        stop("Error when sending\n");
    }

    return 0;   
}

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