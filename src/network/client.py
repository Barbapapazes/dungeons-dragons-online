"""Client class"""
import os
import signal
import time
from src.utils.network import check_message


class Client:
    def __init__(self, game):
        self.game = game

    def send(self, msg=None):
        """Create a subprocess that will send the position to the local server with client_ip_port


        Args:
            game (object)
            msg (str, optional): Message to send. Defaults to None.
        """
        self.game.send = False

        if msg is None:
            # If no message is specified then we send the position of the client
            msg = (
                "move "
                + self.game.network.ip
                + " "
                + str(self.game.players[self.game.network.ip].pos)
                + "\n"
            )

        try:
            check_message(msg)
        except ValueError:
            print("message error")
            return
        msg = msg.split(" ")

        tmp = self.game.network.client_ip_port.copy()
        for ip in tmp:
            # write the encoded message on the right tcpclient stdin then flush it to avoid conflict
            try:

                for word in msg:
                    word += '\n'
                    word = str.encode(word)
                    print(word)
                    self.game.network.connections[ip].stdin.write(word)
                    self.game.network.connections[ip].stdin.flush()
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
        for ip in self.game.network.connections:
            # end all the tcpclient process that are in connections dictionnary
            os.kill(self.game.network.connections[ip].pid, signal.SIGUSR1)
