#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <errno.h>
#include <fcntl.h>
#include "serialization.h"

/**
 * @brief stop the process if an error occurs and print the error
 * 
 */
void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}
/**
 * @brief end the process
 * 
 */
void end(int signum)
{
    exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[])
{
    signal(SIGUSR1, &end); // signal handler : catch SIGUSR1 and execute end function

    /* Buffer */
    char *stdin_read = NULL;
    char buffer[80];

    /* Socket */
    int sockfd = socket(PF_INET, SOCK_STREAM, 0); //create a new tcp socket
    size_t size;
    int res, opt;

    /* Ping */
    struct timeval timeout;
    struct timeval ping_in, ping_out;
    timeout.tv_sec = 0.1;
    timeout.tv_usec = 0;

    /* Packet */
    unsigned char *s_packet;
    game_packet game_data = {0, -1, ""}; // initialize a game_packet structure that will contain all the needed information
    int packet_length = 0;
    char *end; //pointer use in string to int conversion

    if (sockfd < 0)
        stop("socket()");

    if (argc != 3)
        stop("arg");

    // prepare the server struct
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET; //server address : ipv4

    // set server adress
    if (inet_aton(argv[1], &serv_addr.sin_addr) == 0)
        stop("inet_aton()");

    // set server port
    serv_addr.sin_port = htons(atoi(argv[2]));

    // get socket flags
    if ((opt = fcntl(sockfd, F_GETFL, NULL)) < 0)
        stop("flag");

    // set socket non-blocking
    if (fcntl(sockfd, F_SETFL, opt | O_NONBLOCK) < 0)
        stop("socket");

    if ((res = connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(struct sockaddr))) < 0)
    {
        if (errno == EINPROGRESS)
        {
            fd_set wait_set;

            // make file descriptor set with socket
            FD_ZERO(&wait_set);
            FD_SET(sockfd, &wait_set);

            // wait for socket to be writable; return after given timeout
            res = select(sockfd + 1, NULL, &wait_set, NULL, &timeout);
        }
    }
    else
        res = 1;

    // reset socket flags
    if (fcntl(sockfd, F_SETFL, opt) < 0)
        stop("connect");

    // if error occured in connect or select
    if (res < 0)
        stop("connect");

    // if timed out
    else if (res == 0)
    {
        errno = ETIMEDOUT;
        stop("connect");
    }
    else
    {
        socklen_t len = sizeof(opt);

        // check for errors in socket layer
        if (getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &opt, &len) < 0)
            stop("connect");

        // if error
        if (opt)
        {
            errno = opt;
            stop("connect");
        }
    }

    while (1)
    {
        // stdin read
        // the python program will send data by line block
        if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
            stop("getline()");

        game_data.player_id = strtol(stdin_read, &end, 10);

        if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
            stop("getline()");

        game_data.action = strtol(stdin_read, &end, 10);

        if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
            stop("getline()");

        game_data.data = strdup(stdin_read); //duplicate so the data won't have the same adress as stdin_read and we can modify it

        // format packet
        s_packet = serialize_packet(game_data);
        packet_length = 3 * sizeof(int) + strlen(game_data.data); // check serialization for more details

        if (send(sockfd, s_packet, packet_length, 0) == -1) // send the message
            stop("send()");

        gettimeofday(&ping_in, NULL); // get time in s and µs when the packet has been sent

        if (recv(sockfd, buffer, 2, 0) == -1) //wait for a server response
            stop("send()");

        // get time in s and µs when the packet has been received
        gettimeofday(&ping_out, NULL);
        sprintf(buffer, "ping : %lu us\n", (ping_out.tv_sec - ping_in.tv_sec) * 1000000 + ping_out.tv_usec - ping_in.tv_usec);
        write(STDOUT_FILENO, buffer, strlen(buffer));
    }

    if (close(sockfd) == -1) // close file descriptor
        stop("close");

    exit(EXIT_SUCCESS);
}