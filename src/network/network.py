
import subprocess
import os
import queue
import signal
import time
import threading
from src.config.network import CLIENT_PATH, SERVER_PATH
from src.utils.network import enqueue_output, get_ip
from os import path


class Network:
    def __init__(self, game):
        self.game = game
        self.ip = get_ip()
        self.port = 8000
        self._server = self.create_serveur()
        print(self.get_socket())

    def create_serveur(self):
        """Create the server

        Returns:
            Popen: the server
        """
        # create a subprocess that will execute a new process. list is equivalent to argv[].
        # Pipe (new file-descriptor) are used to allow us to communicate with the process.
        # If we don't precise them the subprocess inherite from the main process and so will use default fd.
        server = subprocess.Popen(
            [SERVER_PATH, str(self.port), str(self.ip)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # we make the process wait to ensure that the subprocess above has started or ended if an error occured
        time.sleep(0.1)
        # poll check if the process has ended or not. If the process is running the None is returned
        return self.check_server(server)

    def check_server(self, server):
        """Check is the server is created

        Args:
            server (Popen)

        Returns:
            Popen
        """
        poll = server.poll()
        while poll is not None:
            self.port += 1
            server = subprocess.Popen(
                [SERVER_PATH, str(self.port), str(self.ip)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(0.1)
            poll = server.poll()
        return server

    def get_socket(self):
        return str(self.ip) + ":" + str(self.port)

    def server(self):
        """interprets the server's output"""
        # try to get something from each tcpclient process
        for key in self.game.ping:
            try:
                line = self.game.ping[key][1].get(timeout=0.001)
            except queue.Empty:
                pass
            else:
                line = line.decode("ascii")
                line = line[:-1]
                print(key + " " + line)

        try:
            # try to pop something from the queue if there is nothing at the end of the timeout raise queue.Empty
            line = self.game.q.get(timeout=0.001)
        except queue.Empty:
            return
        else:
            # if no exception is raised then line contains something
            line = line.decode("ascii")  # binary flux that we need to decode
            line = line[:-1]  # delete the final `\n`

            # first connection of a client
            if line.startswith("first"):
                self.new_connexion(line)

            elif line.startswith("ip"):
                self.new_ip(line)

            # if a movement is sent
            elif line.startswith("move"):
                self.move(line)

            elif line.startswith("disconnect"):
                self.disconnect(line)

    def create_connection(self, line):
        # if line[1] not in self.players:
        #     self.players[line[1]] = Player()
        line = line.split(" ")
        tmp = line[1].split(":")

        self.game.connections[line[1]] = subprocess.Popen(
            [CLIENT_PATH, tmp[0], tmp[1]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # queue.Queue() is a queue FIFO (First In First Out) with an unlimited size
        tmp_queue = queue.Queue()
        tmp_thread = threading.Thread(
            target=enqueue_output,
            args=(self.game.connections[line[1]].stdout, tmp_queue),
        )

        # the thread will die with the end of the main procuss
        tmp_thread.daemon = True
        # thread is launched
        tmp_thread.start()
        self.game.ping[line[1]] = (tmp_thread, tmp_queue)

    def first_connection(self, line):
        """Define what the program does when a new connection occurres

        Args:
            target_ip (str): string that contains the ip:port of the new connection
        """
        line = line.split(" ")
        target_ip = line[1]
        for ip in self.game.client_ip_port:
            # this loop sends to all other client the information (<ip>:<port>) of the new player
            msg = str("ip " + target_ip + "\n")
            msg = str.encode(msg)
            self.game.connections[ip].stdin.write(msg)
            self.game.connections[ip].stdin.flush()

        for ip in self.game.client_ip_port:
            # this loop sends to the new user all the ip contained in self.client_ip_port and all the relative position of the players
            # block that sends the ip
            msg = str("ip " + ip + "\n")
            msg = str.encode(msg)
            self.game.connections[target_ip].stdin.write(msg)
            self.game.connections[target_ip].stdin.flush()

            # block that sends the position
            # msg = str("move " + ip + " " + str(self.players[ip].pos) + "\n")
            # msg = str.encode(msg)
            # self.connections[target_ip].stdin.write(msg)
            # self.connections[target_ip].stdin.flush()

        # send the position of the main player
        # msg = str(
        #     "move "
        #     + self.my_ip
        #     + " "
        #     + str(self.players[self.my_ip].pos)
        #     + "\n"
        # )
        # msg = str.encode(msg)
        # self.connections[target_ip].stdin.write(msg)
        # self.connections[target_ip].stdin.flush()

    def new_connexion(self, line):
        """Handle a new connexion on the network

        Args:
            line (str)
        """
        # self.players[line[1]] = Player()
        self.create_connection(line)
        self.first_connection(line)
        self.add_to_clients(self.get_client_from(line))
        # add the new ip to the client_ip_port set

    def new_ip(self, line):
        """Add a new ip to the set


        Args:
            line (str)
        """
        self.create_connection(line)
        self.add_to_clients(self.get_client_from(line))

    def move(self, line):
        line = line.split(" ")
        # position is separate in two different index so we concatenate them
        tmp = line[2] + " " + line[3]
        # transform the string into list of string
        list_pos = tmp.strip("][").split(", ")
        # transform the list of string into list of int
        for cmpt in range(len(list_pos)):
            list_pos[cmpt] = int(list_pos[cmpt])
        # if players doesn't exist create it
        #  if line[1] not in self.players:
        # self.players[line[1]] = Player()
        # add to the right player the associate position
        self.game.players[line[1]].pos = list_pos

    def disconnect(self, line):
        client = self.get_client_from(line)
        self.remove_from_client(client)
        self.kill(client)
        self.remove_connexion(client)
        # delete the player so it is not blit anymore
        # del self.players[line[1]]
        # delete his ip

    def add_to_clients(self, client):
        self.game.client_ip_port.add(client)

    def remove_from_client(self, client):
        self.game.client_ip_port.remove(client)

    def remove_connexion(self, client):
        del self.game.connections[client]
        del self.game.ping[client]

    def kill(self, client):
        pid = self.game.connections[client].pid
        os.kill(pid, signal.SIGINT)

    @staticmethod
    def get_client_from(line):
        line = line.split(" ")
        return line[1]
