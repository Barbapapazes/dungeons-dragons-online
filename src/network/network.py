
import subprocess
import os
import queue
import signal
import time
import threading
from src.config.network import CLIENT_PATH, SERVER_PATH
from src.utils.network import enqueue_output, get_ip, check_message
from os import path
import traceback


class Network:
    def __init__(self, game):
        self.game = game
        self.ip = get_ip()
        self.port = 8000
        self._server = self.create_serveur()
        print(self.get_socket())

        self.client_ip_port = set()  # is a set to avoid duplicate
        self.connections = dict()  # contains subprocess with ip:port as a key
        self.ping = dict()  # contains multiple thread to read tcpclient
        # contains all player_id associated to their ip

        self.q = queue.Queue()
        self.t = self.create_pipeline()
        self.start_pipeline()

    def start_pipeline(self):
        """Start the thread"""
        # the thread will die with the end of the main procuss
        self.t.daemon = True
        # thread is launched
        self.t.start()

    def create_pipeline(self):
        """Create a thread to read stdout in a non-blocking way

        Returns:
            Thread
        """
        return threading.Thread(
            target=enqueue_output, args=(self._server.stdout, self.q)
        )

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
        for key in self.ping:
            try:
                line = self.ping[key][1].get(timeout=0.001)
            except queue.Empty:
                pass
            else:
                line = line.decode("ascii")
                line = line[:-1]
                print(key + " " + line)

        try:
            # try to pop something from the queue if there is nothing at the end of the timeout raise queue.Empty
            line = self.q.get(timeout=0.001)
        except queue.Empty:
            return
        else:
            print(line)
            # if no exception is raised it means that line contains something
            line = line.decode("ascii")  # binary flux that we need to decode
            line = line[:-1]  # delete the final `\n`
            split_line = line.split(" ")  # separate the line string by word

            # first connection of a client
            if split_line[1] == "0":
                self.new_connexion(line)

            # ip data received
            elif split_line[1] == "2":
                self.new_ip(line)

            # a client has diconnected
            elif split_line[1] == "3":
                self.disconnect(line)

            # change the id of the current user (used at the first connexion)
            elif split_line[1] == "4":
                self.change_id(line)

            # if a movement is sent
            elif split_line[1] == "5":
                self.move(line)

    def create_connection(self, line):
        # if line[1] not in self.players:
        #     self.players[line[1]] = Player()
        line = self.get_data_from(line)
        tmp = line.split(":")
        line = tmp[0] + ":" + tmp[1]
        if len(tmp) not in [2, 3]:
            return
        self.connections[line] = subprocess.Popen(
            [CLIENT_PATH, tmp[0], tmp[1]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # queue.Queue() is a queue FIFO (First In First Out) with an unlimited size
        tmp_queue = queue.Queue()
        tmp_thread = threading.Thread(
            target=enqueue_output,
            args=(self.connections[line].stdout, tmp_queue),
        )

        # the thread will die with the end of the main procuss
        tmp_thread.daemon = True
        # thread is launched
        tmp_thread.start()
        self.ping[line] = (tmp_thread, tmp_queue)

    def first_connection(self, line):
        """Define what the program does when a new connection occurres

        Args:
            target_ip (str): string that contains the ip:port of the new connection
        """

        target_ip = self.get_data_from(line)
        if len(self.game.player_id) > 0:
            # get last id and add 1 to it
            new_id = str(int(list(self.game.player_id.values())[-1]) + 1)
        else:
            new_id = str(self.game.own_id + 1)
        for ip in self.client_ip_port:
            # this loop sends to all other client the information (<ip>:<port>) of the new player
            msg = str(str(self.game.own_id) + " 2 "
                      + target_ip + ":" + new_id)
            print("ip message : ", msg)
            try:
                check_message(msg)
            except ValueError:
                print("message error")
                break
            self.send_message(msg, ip)

        for ip in self.client_ip_port:
            # this loop sends to the new user all the ip contained in self.client_ip_port and all the relative position of the players
            # block that sends the ip
            msg = str(str(self.game.own_id) + " 2 "
                      + ip + ":" + self.game.player_id[ip])
            try:
                check_message(msg)
            except ValueError:
                print("message error")
                return
            self.send_message(msg, target_ip)

        msg = str(str(self.game.own_id) + " 4 "
                  + self.ip + ":" + str(self.port) + ":" + new_id)
        self.send_message(msg, target_ip)
        self.game.player_id[target_ip] = new_id

    def new_connexion(self, line):
        """Handle a new connexion on the network

        Args:
            line (str)
        """
        # self.players[line[1]] = Player()
        self.create_connection(line)
        self.first_connection(line)

        try:
            client = self.get_data_from(line)
            self.add_to_clients(client)
        except Exception as e:
            print(e)
        # add the new ip to the client_ip_port set

    def new_ip(self, line):
        """Add a new ip to the set


        Args:
            line (str)
        """
        self.create_connection(line)
        tmp = self.get_data_from(line).split(":")
        id = tmp[2]
        ip = tmp[0] + ":" + tmp[1]
        self.game.player_id[ip] = id
        print(self.game.player_id)
        try:
            self.add_to_clients(ip)
        except Exception as e:
            print(e)

    def disconnect(self, line):
        """handle a client disconnection :
        remove the client ip from all the relative list and set
        kill the associated processus (tcpclient)


        Args:
            line (str) : string that contains information
        """
        try:
            client = self.get_data_from(line)
            self.remove_from_client(client)
            self.kill(client)
            self.remove_connexion(client)
        except Exception as e:
            print(e)
        # delete the player so it is not blit anymore

    def add_to_clients(self, client):
        """add the client to the set client_ip_port

        Args:
            client (string): ip:port
        """
        self.client_ip_port.add(client)

    def remove_from_client(self, client):
        """remofe the client from the set client_ip_port

        Args:
            client (string): ip:port
        """
        self.client_ip_port.remove(client)

    def remove_connexion(self, client):
        """Delete the two threads associated to the client from the connections and ping dictionnary

        Args:
            client (string): ip:port
        """
        del self.connections[client]
        del self.ping[client]

    def kill(self, client):
        """send SIGINT signal to all tcpclient processus associated to the client

        Args:
            client (string): ip:port
        """
        pid = self.connections[client].pid
        os.kill(pid, signal.SIGINT)

    @staticmethod
    def get_data_from(line):
        """get data part of the packet

        Args:
            line (string): string of the packet

        Raises:
            Exception: if the packet is not normative

        Returns:
            string : data
        """
        line = line.split(" ")
        if len(line) == 1:
            raise Exception("Can't split the line")
        return line[2]

    def change_id(self, line):
        """Change current client id by the one given in the packet

        Args:
            line (string) : packet
        """
        tmp = self.get_data_from(line).split(":")
        ip = tmp[0] + ":" + tmp[1]
        host_id = tmp[2]
        self.game.player_id[ip] = line.split(" ")[0]
        self.game.own_id = int(host_id)

    def send_message(self, msg: str, ip: str):
        """format message and send it to the ip

        Args:
            msg (string): packet
            ip (string): recipient
        """
        try:
            check_message(msg)
        except ValueError:
            return
        msg = msg.replace("\n", "")
        msg = msg.split(" ")
        print("message :", msg, ip)
        for word in msg:
            word += '\n'
            word = str.encode(word)
            self.connections[ip].stdin.write(word)
            self.connections[ip].stdin.flush()
