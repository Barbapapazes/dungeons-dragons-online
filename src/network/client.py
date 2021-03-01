"""Client class"""
import os
import signal
import time


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
                "move " +
                self.game.n.ip +
                " " +
                str(self.game.players[self.game.n.ip].pos) +
                "\n"
            )
        msg = str.encode(msg)
        tmp = self.game.client_ip_port.copy()
        for ip in tmp:
            # write the encoded message on the right tcpclient stdin then flush it to avoid conflict
            try:
                self.game.connections[ip].stdin.write(msg)
                self.game.connections[ip].stdin.flush()
            except BrokenPipeError:
                pass

    def disconnect(self):
        """handle the disconnection of the player and end all the subprocess"""
        # sends to all other players that the client has disconnected
        self.send(str("disconnect " + self.game.n.get_socket() + "\n"))
        # ensure that the disconnect message has been sent
        time.sleep(0.5)
        # end the serv process (look for tcpserver to get more details)
        os.kill(self.game.n._server.pid, signal.SIGUSR1)
        for ip in self.game.connections:
            # end all the tcpclient process that are in connections dictionnary
            os.kill(self.game.connections[ip].pid, signal.SIGUSR1)
