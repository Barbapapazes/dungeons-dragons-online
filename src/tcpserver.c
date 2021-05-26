#include <stdio.h>
#include <string.h> //strlen
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>    //close
#include <arpa/inet.h> //close
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/time.h> //FD_SET, FD_ISSET, FD_ZERO macros
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/sendfile.h>
#include <strings.h>
#include <signal.h>
#include "serialization.h"

#define TRUE 1
#define FALSE 0
#define BUFSIZE 1025

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

void activation(int signum)
{
    return;
}

/**
 * @brief return the first index available to store a socket
 * @return int : -1 if socket array is full
 */
int first_available_socket(int *socket, int size)
{
    for (int i = 0; i < size; i++)
        if (socket[i] == 0)
            return i;
    return -1;
}

int main(int argc, char *argv[])
{
    signal(SIGUSR2, &activation);
    int opt = TRUE;
    int master_socket, addrlen, new_socket, client_socket[2000], max_clients = 2000, activity, i, valread, sd;
    int max_sd;
    bzero(client_socket, max_clients * sizeof(int)); // initialize socket array to 0

    struct sockaddr_in serv_addr;
    char buffer[BUFSIZE]; //data buffer of 1K
    fd_set readfds;
    game_packet game_data = {0, -1, ""};                      // initialize a game_packet structure that will contain all the needed information
    static const game_packet empty_game_packet = {0, -1, ""}; // initialize a game_packet structure that will be used to reset the first one

    if ((master_socket = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        stop("socket");
    }

        serv_addr.sin_family = AF_INET;
    if (inet_aton(argv[2], &serv_addr.sin_addr) == 0)
        stop("inet_aton()");
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(master_socket, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        stop("bind");
    }
    // wait for an activation
    pause();

    if (setsockopt(master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0)
    {
        stop("setsockopt");
    }
    if (listen(master_socket, 30) < 0)
    {
        stop("listen");
    }

    //accept the incoming connection
    addrlen = sizeof(serv_addr);

    while (TRUE)
    {
        //clear the socket set
        FD_ZERO(&readfds);

        //add master socket to set
        FD_SET(master_socket, &readfds);
        max_sd = master_socket;

        //add child sockets to set
        for (i = 0; i < max_clients; i++)
        {
            //socket descriptor
            sd = client_socket[i];

            //if valid socket descriptor then add to read list
            if (sd > 0)
                FD_SET(sd, &readfds);

            //highest file descriptor number, need it for the select function
            if (sd > max_sd)
                max_sd = sd;
        }

        //wait for an activity on one of the sockets , timeout is NULL , so wait indefinitely
        activity = select(max_sd + 1, &readfds, NULL, NULL, NULL);

        if ((activity < 0) && (errno != EINTR))
        {
            stop("select");
        }

        if (FD_ISSET(master_socket, &readfds))
        {
            if ((new_socket = accept(master_socket, (struct sockaddr *)&serv_addr, (socklen_t *)&addrlen)) < 0) // FIX lorsque il y a 3 connexions (dont une qui s'est remove)
            {
                stop("accept");
            }

            if (new_socket != 0)
                client_socket[first_available_socket(client_socket, max_clients)] = new_socket;
        }
        for (i = 0; i < max_clients; i++)
        {
            sd = client_socket[i];

            if (FD_ISSET(sd, &readfds))
            {
                if ((valread = recv(sd, buffer, 1024, 0)) == 0)
                {
                    close(sd);
                    client_socket[i] = 0;
                }
                else
                {

                    buffer[valread] = '\0'; // -1 to remove le \n
                    if (strcmp(buffer, "") == 0)
                        break;

                    // format the packet received
                    game_data = deserialize_packet((unsigned char *)buffer);
                    sprintf(buffer, "%d %d %s", game_data.player_id, game_data.action, game_data.data);
                    write(STDOUT_FILENO, buffer, strlen(buffer));
                    game_data = empty_game_packet;
                }
            }
        }
    }
    return 0;
}
