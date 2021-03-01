import os
import signal
import time


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
    tmp = game.client_ip_port.copy()
    for ip in tmp:
        # write the encoded message on the right tcpclient stdin then flush it to avoid conflict
        try:
            game.connections[ip].stdin.write(msg)
            game.connections[ip].stdin.flush()
        except BrokenPipeError:
            pass
