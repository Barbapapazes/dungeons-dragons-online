#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <signal.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <netdb.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include "serialization.h"

#define BUFFSIZE 1500

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
 * @brief Does nothing, used to unpause
 * 
 */
void activation(int signum)
{
    return;
}

/**
 * @brief end the program and avoid orphans children
 * 
 */
void end(int signum)
{
    pid_t pid = getpid();         //get pid of the current process
    killpg(getpgid(pid), SIGINT); //kill all process that have the same group id as the current process (here kill all child and the current process)
    exit(EXIT_SUCCESS);           //end the process if SIGINT hasn't already done it
}

int main(int argc, char *argv[])
{
    signal(SIGUSR1, &end); // if SIGUSR1 is received execute end function
    signal(SIGUSR2, &activation);

    char buffer[BUFFSIZE]; //Buffer of 8192 char
    int n;                 //counter of char received
    pid_t childpid, pid;   //pid used for fork, pid used for group id

    /* Packet */
    game_packet game_data = {0, -1, ""};                      // initialize a game_packet structure that will contain all the needed information
    static const game_packet empty_game_packet = {0, -1, ""}; // initialize a game_packet structure that will be used to reset the first one

    /* Socket */
    int newsockfd;                                //file descriptor that will contains the client socket
    int sockfd = socket(PF_INET, SOCK_STREAM, 0); //server socket where client connects.
    int true = 1;                                 // var used in setsockopt

    // handle error
    if (sockfd < 0)
        stop("socket()");

    if (argc != 3)
        stop("argc");

    /* Server */
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr)); //initialize the serv_addr
    serv_addr.sin_family = AF_INET;       //server address : ipv4

    // set server adress
    if (inet_aton(argv[2], &serv_addr.sin_addr) == 0)
        stop("inet_aton()");

    // set server port
    serv_addr.sin_port = htons(atoi(argv[1]));

    // associate to sockfd serv_addr
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
        stop("bind()");

    // wait for an activation
    pause();

    // avoid the bind error by allowing re-use of the same port for the socket
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &true, sizeof(int));

    // allows to queue up to 2000 connexions to the server
    if (listen(sockfd, 2000) == -1)
        stop("listen()");

    int size = sizeof(serv_addr);

    // wait for a connection to arrive on sockfd
    if ((newsockfd = accept(sockfd, (struct sockaddr *)&serv_addr, (socklen_t *)&size)) == -1)
        stop("accept()");

    // set a group id to the process id
    pid = getpid();
    setpgid(pid, 0);

    while (1)
    {
        //the father waits that a new connection occurs to fork again
        // the child will stay alive while a connection is maintained and write on stdout.
        if ((childpid = fork()) == 0) //fork the program so we can handle multiple tcp connection
        {
            close(sockfd); //if we are in child the sockfd is no more needed so we close it
            n = recv(newsockfd, buffer, BUFFSIZE, 0);

            do
            {
                // handle error
                if ((n == -1))
                    stop("recv()");

                // ensure that buffer has a final character
                buffer[n] = '\0';

                // format the packet received
                game_data = deserialize_packet((unsigned char *)buffer);
                sprintf(buffer, "%d %d %s", game_data.player_id, game_data.action, game_data.data);
                write(STDOUT_FILENO, buffer, strlen(buffer));

                // send acknowledgement to the client (used for ping)
                send(newsockfd, "1", 2, 0);
                game_data = empty_game_packet;

            } while ((n = recv(newsockfd, buffer, BUFFSIZE, 0)) > 0); //write the message in STDOUT_FILENO

            if ((close(newsockfd))) //close the attributed socket to avoid bind error
                stop("close");

            return 0; // if the message has not been fully received reiterate the process
        }
        else
        {
            if ((newsockfd = accept(sockfd, (struct sockaddr *)&serv_addr, (socklen_t *)&size)) == -1) //accept a new connection
                stop("accept()");
        }
    }
    close(newsockfd);
    close(sockfd);
    exit(EXIT_SUCCESS);
}