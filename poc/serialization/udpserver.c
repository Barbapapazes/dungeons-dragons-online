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

void stop(char* msg);

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
    char * buffer = malloc(sizeof(char)*(size+1));

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

    //UDP Socket
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

    //Binding
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ==-1) {
        close(sockfd);
        stop("Error when binding\n");
    }

    char buff[1000];
    int receipt;
    struct sockaddr_in client_addr;
    bzero(&client_addr, sizeof(client_addr));
    int client_len = sizeof(client_addr);
    
    //Sending/Receiving requests
    while(1) {

        //If the server receives something
        if ((receipt = recvfrom(sockfd, &buff, sizeof(buff), 0, (struct sockaddr *)&client_addr, &client_len))==-1)
        {
            close(sockfd);
            stop("Error when receiving packet\n");
        }

        //If the information received is not empty
        if (receipt != 0) {
            printf("Raw packet : %i\n", buff);
            //Deserialization
            game_struct received_packet = deserialize(buff);

            //Printing what we received 
            printf("Received packet :\n");
            printf("Player id : %i\n", received_packet.player_id);
            printf("Action : %i\n", received_packet.action);
            printf("User input : %s\n", received_packet.user_input);
            

            receipt = 0;
        }

    }

    return 0;   
}

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