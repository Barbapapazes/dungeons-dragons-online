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
#include <sys/epoll.h>
#include "serialization.h"

#define TRUE 1
#define FALSE 0
#define BUFSIZE 1025
#define MAXCLIENT 2000

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
    //master socket is the server socket that will receive new connection curfds is current file descriptors (number of connection)
    //epollfd is the file descriptor that will be used to controll the epoll
    int master_socket, addrlen, new_socket, activity, client_socket[MAXCLIENT], valread, curfds, epollfd, current_packet = 0;
    bzero(client_socket, MAXCLIENT);
    struct epoll_event ev;      // struct used to initialize the epoll
    struct epoll_event *events; // array that will contains fd with an activity
    struct sockaddr_in serv_addr;
    char buffer[BUFSIZE]; //data buffer of 1K
    char stdout_buffer[BUFSIZE];
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

    // setup epoll add the master socket to the wait list
    epollfd = epoll_create(MAXCLIENT);
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = master_socket;

    if (epoll_ctl(epollfd, EPOLL_CTL_ADD, master_socket, &ev) < 0)
    {
        stop("epoll_ctl_add_master");
    }
    events = calloc(MAXCLIENT, sizeof ev);
    curfds = 1;

    while (TRUE)
    {
        // wait for an activity
        activity = epoll_wait(epollfd, events, curfds, -1);
        if (activity == -1)
        {
            stop("epoll_wait");
        }

        for (int n = 0; n < activity; ++n)
        {
            if (events[n].data.fd == master_socket)
            {

                if ((new_socket = accept(master_socket, (struct sockaddr *)&serv_addr, (socklen_t *)&addrlen)) < 0)
                {
                    stop("accept");
                }

                if (new_socket != 0)
                {
                    if (fcntl(new_socket, F_SETFL, opt | O_NONBLOCK) < 0)
                        stop("socket");

                    client_socket[first_available_socket(client_socket, MAXCLIENT)] = new_socket;
                    ev.events = EPOLLIN | EPOLLET;
                    ev.data.fd = new_socket;
                    if (epoll_ctl(epollfd, EPOLL_CTL_ADD, new_socket, &ev) < 0)
                    {
                        stop("epoll_ctl_add");
                    }
                    curfds++;
                }
            }
            else
            {
                while ((valread = recv(events[n].data.fd, buffer, 2048, 0)) > 0)
                    if (valread == 0)
                    {
                        // disconnection
                        epoll_ctl(epollfd, EPOLL_CTL_DEL, events[n].data.fd, &ev);
                        curfds--;
                        close(events[n].data.fd);
                        client_socket[n] = 0;
                    }
                    else
                    {

                        if (strcmp(buffer, "") == 0)
                            break;
                        while (TRUE)
                        {
                            // format the packet received
                            game_data = deserialize_packet((unsigned char *)buffer + current_packet);
                            sprintf(stdout_buffer, "%d %d %s", game_data.player_id, game_data.action, game_data.data);
                            write(STDOUT_FILENO, stdout_buffer, strlen(stdout_buffer));
                            if ((current_packet = (current_packet + get_size_of_packet((unsigned char *)buffer + current_packet))) >= valread)
                                break;
                        }
                        game_data = empty_game_packet;
                        current_packet = 0;
                    }
            }
        }
    }
    return 0;
}
