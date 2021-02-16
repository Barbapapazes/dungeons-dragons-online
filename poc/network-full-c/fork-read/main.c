#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#define CHILDNBR 30

int main(int argc, char *argv[])
{
    int pipefd[CHILDNBR * 2]; //create an array that for each child will contain 2 file descriptor. It allows the parent to communicate with child
    char *stdin_read;
    FILE *flux; //stream that will be used to getline
    size_t size;
    pid_t pid;

    pipe(pipefd); // create two fd at 0 and 1 index
    for (int i = 0; i < CHILDNBR; i++)
    {
        if ((pid = fork()) == 0)
        {
            flux = fdopen(pipefd[2 * i], "r");     //  create a stream from the read-end fd
            close(pipefd[2 * i + 1]);              // close the write-end of the pipe
            getline(&stdin_read, &size, flux);     //wait to get a line on the stream
            printf("child%d : %s", i, stdin_read); //print the line
            close(pipefd[2 * i]);                  // close the read-end of the pipe
            exit(EXIT_SUCCESS);                    // end the child proc
        }
        else if (i < CHILDNBR - 1)
        {
            pipe(pipefd + (i + 1) * 2); // create two fd at 2*i and 2*i+1 index
        }
    }

    close(pipefd[0]);                   // close the read-end of the pipe, I'm not going to use it
    getline(&stdin_read, &size, stdin); //get the line that will be sent to child
    printf("parent : %s\n", stdin_read);
    for (int i = 0; i < CHILDNBR; i++)
    {
        write(pipefd[2 * i + 1], stdin_read, strlen(stdin_read)); // send the content of stdin to the reader
        close(pipefd[2 * i + 1]);                                 // close the write-end of the pipe sending EOF to the reader
    }
    wait(NULL); // wait for the child process to exit before I do the same
    exit(EXIT_SUCCESS);
}
