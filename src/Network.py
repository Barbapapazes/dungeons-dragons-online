import subprocess
import os
import queue
import signal
import time
import socket
import threading


def server(game):
    """interprets the server's output"""
    # try to get something from each tcpclient process
    for key in game.ping:
        try:
            line = game.ping[key][1].get(timeout=0.001)
        except queue.Empty:
            pass
        else:
            line = line.decode("ascii")
            print(line)

    try:
        # try to pop something from the queue if there is nothing at the end of the timeout raise queue.Empty
        line = game.q.get(timeout=0.001)
    except queue.Empty:
        return
    else:
        # if no exception is raised then line contains something
        line = line.decode("ascii")  # binary flux that we need to decode
        line = line[:-1]  # delete the final `\n`

        # first connection of a client
        if line.startswith("first"):
            # get the line split by word
            line = line.split(" ")
            # self.players[line[1]] = Player()
            # split the ip and the port
            add_connection(game, line)
            first_connection(game, line[1])
            # add the new ip to the client_ip_port set
            game.client_ip_port.add(line[1])

        # if an ip is sent, add it to the set
        elif line.startswith("ip"):
            line = line.split(" ")
            add_connection(game, line)

        # if a movement is sent
        elif line.startswith("move"):
            # split the line with ` `
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
            game.players[line[1]].pos = list_pos

        elif line.startswith("disconnect"):
            line = line.split(" ")
            # delete the player so it is not blit anymore
            # del self.players[line[1]]
            # delete his ip
            game.client_ip_port.remove(line[1])
            pid = game.connections[line[1]].pid
            os.kill(pid, signal.SIGINT)
            del game.connections[line[1]]
            del game.ping[line[1]]


def add_connection(game, line):
    game.client_ip_port.add(line[1])
    # if line[1] not in self.players:
    #     self.players[line[1]] = Player()
    tmp = line[1].split(":")
    game.connections[line[1]] = subprocess.Popen(
        ["./src/tcpclient", tmp[0], tmp[1]],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # queue.Queue() is a queue FIFO (First In First Out) with an unlimied size
    tmp_queue = queue.Queue()
    tmp_thread = threading.Thread(
        target=enqueue_output,
        args=(game.connections[line[1]].stdout, tmp_queue),
    )

    # the thread will die with the end of the main procus
    tmp_thread.daemon = True
    # thread is launched
    tmp_thread.start()
    game.ping[line[1]] = (tmp_thread, tmp_queue)


def get_ip():
    """Get default ip used by the computer to establish a LAN Network

    Returns:
        `str` : Default IP or '127.0.0.1' if an error occurs
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # try to connect but no need to establish a connection (works in LAN)
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def disconnect(game):
    """handle the disconnection of the player and end all the subprocess"""
    # sends to all other players that the client has disconnected
    client(game, str("disconnect " + game.my_ip + "\n"))
    # ensure that the disconnect message has been sent
    time.sleep(0.5)
    # end the serv process (look for tcpserver to get more details)
    os.kill(game.serv.pid, signal.SIGUSR1)
    for ip in game.connections:
        # end all the tcpclient process that are in connections dictionnary
        os.kill(game.connections[ip].pid, signal.SIGUSR1)


def client(game, msg=None):
    """create a subprocess that will send the position to the local server with client_ip_port"""
    game.send = False

    if msg is None:
        # If no message is specified then we send the position of the client
        msg = (
            "move "
            + game.my_ip
            + " "
            + str(game.players[game.my_ip].pos)
            + "\n"
        )
    msg = str.encode(msg)

    for ip in game.client_ip_port:
        # write the encoded message on the right tcpclient stdin then flush it to avoid conflict
        game.connections[ip].stdin.write(msg)
        game.connections[ip].stdin.flush()


def first_connection(game, target_ip):
    """Define what the program does when a new connection occures

    Args:
        target_ip (str): string that contains the ip:port of the new connection
    """
    for ip in game.client_ip_port:
        # this loop sends to all other client the information (<ip>:<port>) of the new player
        msg = str("ip " + target_ip + "\n")
        msg = str.encode(msg)
        game.connections[ip].stdin.write(msg)
        game.connections[ip].stdin.flush()

    for ip in game.client_ip_port:
        # this loop sends to the new user all the ip contained in self.client_ip_port and all the relative position of the players
        # block that sends the ip
        msg = str("ip " + ip + "\n")
        msg = str.encode(msg)
        game.connections[target_ip].stdin.write(msg)
        game.connections[target_ip].stdin.flush()

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


def enqueue_output(out, queue_line):
    """Queued the first line from stdout in the queue passed in parameter

    Args:
        out (int): file descriptor where the function will read
        queue_line (queue.Queue()): FIFO queue
    """
    for line in iter(out.readline, b""):
        queue_line.put(line)
