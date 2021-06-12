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
#define HASHSIZE 2003

struct nlist
{                       /* table entry: */
    struct nlist *next; /* next entry in chain */
    char *name;         /* defined name */
    int value;          /* replacement text */
};

static struct nlist *hashtab[HASHSIZE]; /* pointer table */

/* hash: form hash value for string s */
unsigned hash(char *s)
{
    unsigned hashval;
    for (hashval = 0; *s != '\0'; s++)
        hashval = *s + 101 * hashval;
    return hashval % HASHSIZE;
}

/* lookup: look for s in hashtab */
struct nlist *lookup(char *s)
{
    struct nlist *np;
    for (np = hashtab[hash(s)]; np != NULL; np = np->next)
    {
        if (strcmp(s, np->name) == 0)
            return np; /* found */
    }
    return NULL; /* not found */
}

char *hash_strdup(char *);
// add_hash: put (name, defn) in hashtab
void add_hash(char *name, int value)
{
    struct nlist *np;
    unsigned hashval;
    if ((np = lookup(name)) == NULL)
    { /* not found */
        np = (struct nlist *)malloc(sizeof(*np));
        if (np == NULL || (np->name = hash_strdup(name)) == NULL)
            return;
        hashval = hash(name);
        np->next = hashtab[hashval];
        hashtab[hashval] = np;
    }
    np->value = value;
    return;
}

// remove (name,value) from hashtab handle link between linked list
int remove_hash(char *name, int value)
{
    struct nlist *np, *prev;
    prev = NULL;
    unsigned hashval;
    if (lookup(name) == NULL)
    { /* not found */
        printf("not found\n");
        return -1;
    }
    hashval = hash(name);
    np = hashtab[hashval];

    do
    {
        if (strcmp(np->name, name) == 0)
        {

            if ((np->next != NULL) && (prev == NULL))

                hashtab[hashval] = np->next;

            else if (np->next)

                prev->next = np->next;

            else if (prev)

                prev->next = NULL;

            else
                hashtab[hashval] = NULL;
            free(np);
            return 0;
        }
        prev = np;

    } while ((np = np->next) != NULL);
    return -1;
}

char *hash_strdup(char *s) /* make a duplicate of s */
{
    char *p;
    p = (char *)malloc(strlen(s) + 1); /* +1 for ’\0’ */
    if (p != NULL)
        strcpy(p, s);
    return p;
}

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

/**
 * @brief create a new connection to the ip + port specified. It checks the socket's layer to detect any error.
 * @return int : socket_fd 
 */
int connection(char *ip, char *port)
{
    int sockfd = socket(PF_INET, SOCK_STREAM, 0); //create a new tcp socket

    // set a timeout in case the connection takes to long
    struct timeval timeout;
    timeout.tv_sec = 0.1;
    timeout.tv_usec = 0;

    // vars that will contains errors if one occures
    int res, opt;

    // prepare the server struct
    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET; //server address : ipv4

    // set server adress
    if (inet_aton(ip, &serv_addr.sin_addr) == 0)
        stop("inet_aton()");

    // set server port
    serv_addr.sin_port = htons(atoi(port));

    // get socket flags
    if ((opt = fcntl(sockfd, F_GETFL, NULL)) < 0)
        stop("flag");

    // set socket non-blocking
    if (fcntl(sockfd, F_SETFL, opt | O_NONBLOCK) < 0)
        stop("socket");

    // try to connect to the server
    if ((res = connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(struct sockaddr))) < 0)
    {

        // if the socket is not yet writable
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
        stop("socket flags");

    // if error occured in connect or select
    if (res < 0)
        stop("connect or select");

    // if timed out
    else if (res == 0)
    {
        errno = ETIMEDOUT;
        stop("timedout");
    }
    else
    {
        socklen_t len = sizeof(opt);

        // check for errors in socket layer
        if (getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &opt, &len) < 0)
            stop("socket layer");

        // if error
        if (opt)
        {
            errno = opt;
            stop("opt");
        }
    }
    return sockfd;
}

/**
 * @brief seach for the key given in the client array
 * @return int : index of the key or -1 if the key is not present
 */

/**
 * @brief return the first available index to store a new connection
 * @return int : index
 */

/**
 * @brief print all current connections that are saved in the client array mostly used to debug
 * 
 */
void print_all_connection()
{

    struct nlist *np;
    for (int i = 0; i < HASHSIZE; i++)
        if (((np = hashtab[i]) && (np->name)))
            do
            {
                if (strcmp(np->name, ""))
                    printf("%d _%s_ : _%d_ :: _%d_ \n", strcmp(np->name, ""), np->name, np->value, hash(np->name));
            } while ((np = np->next) != NULL);
}

void send_to_all_connection(unsigned char *s_packet, int packet_length)
{
    struct nlist *np;
    for (int i = 0; i < HASHSIZE; i++)
        if (((np = hashtab[i]) && (np->name)))
            do
            {
                if (send(hashtab[i]->value, s_packet, packet_length, 0) == -1) // send the message
                    stop("send()");
            } while ((np = np->next) != NULL);
}

int main(int argc, char *argv[])
{
    signal(SIGUSR1, &end); // signal handler : catch SIGUSR1 and execute end function

    /* Buffer */
    char *stdin_read = NULL;
    char buffer[80];

    /* Socket */
    struct nlist *socket;
    size_t size;
    char *ip;
    char *port;
    int send_all = 0; // boolean if == 1 send data to each client

    /* Ping */
    // struct timeval ping_in, ping_out;

    /* Packet */
    unsigned char *s_packet;
    game_packet game_data = {0, -1, ""}; // initialize a game_packet structure that will contain all the needed information
    int packet_length = 0;
    char *end; //pointer use in string to int conversion

    while (1)
    {
        // stdin read
        // the python program will send data by line block
        if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
            stop("getline()");

        // New connection
        if (stdin_read[0] == '!')
        {
            ip = strtok(stdin_read + 1, ":");
            port = strtok(NULL, ":");
            memset(buffer, 0, 80);
            port[strlen(port) - 1] = '\0'; // remove the \n from the string
            sprintf(buffer, "%s:%s", ip, port);
            add_hash(buffer, connection(ip, port));
            memset(stdin_read, 0, size);
        }

        // remove connection
        else if (stdin_read[0] == '-')
        {
            if (strlen(stdin_read) > 0)
                stdin_read[strlen(stdin_read) - 1] = '\0'; // remove the \n from the string
            if ((socket = lookup(stdin_read + 1)) == NULL) // stdin_read + 1 to remove the fist char without affecting the string
                return -1;
            if (close(socket->value) == -1)
                stop("close socket");
            if (remove_hash(socket->name, socket->value) == -1)
                stop("remove_hash");
            memset(buffer, 0, 80);

            memset(stdin_read, 0, size);
            print_all_connection();
        }

        // send data
        else
        {
            // get ip to send to
            if (strlen(stdin_read) > 0)
                stdin_read[strlen(stdin_read) - 1] = '\0'; // remove the \n from the string
            if (strcmp(stdin_read, "all") == 0)
                send_all = 1;
            else if ((socket = lookup(stdin_read)) == NULL) // stdin_read + 1 to remove the fist char without affecting the string
                return -1;

            // get id
            if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
                stop("getline()");

            game_data.player_id = strtol(stdin_read, &end, 10);

            //get action
            if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
                stop("getline()");

            game_data.action = strtol(stdin_read, &end, 10);

            // get data
            if (getline(&stdin_read, &size, stdin) == -1) //get a line on stdin (BLOCKING function)
                stop("getline()");

            game_data.data = strdup(stdin_read); //duplicate so the data won't have the same adress as stdin_read and we can modify it

            // format packet
            s_packet = serialize_packet(game_data);
            packet_length = 3 * sizeof(int) + strlen(game_data.data); // check serialization for more details
            if (send_all)
            {
                send_to_all_connection(s_packet, packet_length);
            }
            else if (send(socket->value, s_packet, packet_length, 0) == -1) // send the message
                stop("send()");
            send_all = 0;
            // gettimeofday(&ping_in, NULL); // get time in s and µs when the packet has been sent

            // if (recv(client[client_index].socket_fd, buffer, 2, 0) == -1) //wait for a server response
            //     stop("send()");

            // // get time in s and µs when the packet has been received
            // gettimeofday(&ping_out, NULL);
            // sprintf(buffer, "ping : %lu us\n", (ping_out.tv_sec - ping_in.tv_sec) * 1000000 + ping_out.tv_usec - ping_in.tv_usec);
            // write(STDOUT_FILENO, buffer, strlen(buffer));
        }
    }

    exit(EXIT_SUCCESS);
}