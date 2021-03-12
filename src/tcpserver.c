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

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
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

    char buffer[BUFFSIZE];                                    //Buffer of 8192 char
    int n;                                                    //counter of char received
    pid_t childpid, pid;                                      //pid used for fork, pid used for group id
    game_packet game_data = {0, -1, ""};                      // initialize a game_packet structure that will contain all the needed information
    static const game_packet empty_game_packet = {0, -1, ""}; // initialize a game_packet structure that will be used to reset the first one

    int newsockfd;                                //file descriptor that will contains the client socket
    int sockfd = socket(PF_INET, SOCK_STREAM, 0); //server socket where client connects.
    if (sockfd < 0)
        stop("socket()");
    if (argc != 3)
        stop("argc");
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr)); //initialize the serv_addr

    serv_addr.sin_family = AF_INET;                   //server address : ipv4
    if (inet_aton(argv[2], &serv_addr.sin_addr) == 0) // puts the ipv4 address in binary and stores it in serv_addr.sin_addr
        stop("inet_aton()");
    serv_addr.sin_port = htons(atoi(argv[1])); // atoi : cast argv[2] in int htons() : puts the port in binary and saves it in serv_addr.sin_port
    int true = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &true, sizeof(int));         // avoid the bind error by allowing the reuse of port for socket
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) // associate to sockfd serv_addr
        stop("bind()");
    if (listen(sockfd, 2000) == -1) //allows to queue up to 20000 connexions to the server
        stop("listen()");
    int size = sizeof(serv_addr);
    if ((newsockfd = accept(sockfd, (struct sockaddr *)&serv_addr, (socklen_t *)&size)) == -1) //accept a new connection
        stop("accept()");
    pid = getpid();
    setpgid(pid, 0); //set a group id to the process id and so all the child because the fork occurs after
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
                if ((n == -1))
                    stop("recv()");
                buffer[n] = '\0';
                game_data = deserialize_packet((unsigned char *)buffer);
                printf("%s\n", game_data.data);
                sprintf(buffer, "%d %d %s", game_data.player_id, game_data.action, game_data.data);

                write(STDOUT_FILENO, buffer, strlen(buffer));
                send(newsockfd, "1", 12, 0);
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