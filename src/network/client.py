"""Client class"""
import os
import signal
import time
from src.utils.network import check_message


class Client:
    def __init__(self, game):
        self.game = game

    def send(self, msg=None, chat=False):
        """Create a subprocess that will send the position to the local server with client_ip_port


        Args:
            game (object)
            msg (str, optional): Message to send. Defaults to None.
        """
        self.game.send = False

        if msg is None:
            # If no message is specified then we send the position of the client
            msg = "0 0 0"
        if not chat:
            try:
                check_message(msg)
            except ValueError:
                print("message error")
                return

        print("client send : ", msg)

        for ip in self.game.network.client_ip_port:
            # write the encoded message on the right tcpclient stdin then flush it to avoid conflict
            try:

                self.game.network.send_message(msg, ip, chat)
            except BrokenPipeError:
                pass

    def disconnect(self):
        """handle the disconnection of the player and end all the subprocess"""
        # sends to all other players that the client has disconnected
        self.send(str(str(self.game.own_id) + " 3 "
                      + self.game.network.get_socket()))
        # ensure that the disconnect message has been sent
        time.sleep(0.5)
        # end the serv process (look for tcpserver to get more details)
        os.kill(self.game.network._server.pid, signal.SIGUSR1)
        for connections in self.game.network.connections.values():
            # end all the tcpclient process that are in connections dictionnary
            os.kill(connections.pid, signal.SIGUSR1)
