import subprocess
import os
import queue
import signal
import time
import random
import threading
from src.Player import DistantPlayer
from src.Enemy import distant_Enemy, local_Enemy, find_enemy_by_id
from src.Map import dict_img_obj, Chest, DistantChest
from src.config.network import (
    CLIENT_PATH,
    SERVER_PATH,
    FIRST_CONNECTION,
    NEW_IP,
    DISCONNECT,
    CHANGE_ID,
    MOVE,
    CHAT,
    ENEMY,
    CHEST,
)
from src.utils.network import (
    enqueue_output,
    get_ip,
    check_message,
    get_id_from_packet,
    get_ip_from_packet,
    get_id_from_all_packet,
)
from os import path
import traceback


class Network:
    def __init__(self, game):
        self.game = game
        self.player_id = game.player_id
        self.ip = get_ip()
        self.port = 8000
        self._server = self.create_serveur()
        self._client = self.create_client()
        # queue.Queue() is a queue FIFO (First In First Out) with an unlimited size
        tmp_queue = queue.Queue()
        tmp_thread = threading.Thread(
            target=enqueue_output,
            args=(self._client.stdout, tmp_queue),
        )

        # the thread will die with the end of the main procuss
        tmp_thread.daemon = True
        # thread is launched
        tmp_thread.start()
        self.ping = (tmp_thread, tmp_queue)
        print(self.get_socket())

        self.client_ip_port = set()  # is a set to avoid duplicate
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

    def create_client(self):
        client = subprocess.Popen(
            [CLIENT_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return client

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

        try:
            line = self.ping[1].get(timeout=0.001)
        except queue.Empty:
            pass
        else:
            # binary flux that we need to decode before manipulate it
            line = line.decode("ascii")
            line = line[:-1]  # delete the final `\n`

        try:
            # try to pop something from the queue if there is nothing at the end of the timeout raise queue.Empty
            # queue.get() method is BLOCKING if timeout arg is not specified or is 0
            line = self.q.get(timeout=0.001)
        except queue.Empty:
            return
        else:
            # if no exception is raised it means that line contains something
            # binary flux that we need to decode before manipulate it
            line = line.decode("utf8")
            line = line[:-1]  # delete the final `\n`
            action = self.get_action_from(line)  # get action from packet

            # first connection of a client
            if action == FIRST_CONNECTION:
                self.new_connexion(line)

            # ip data received
            elif action == NEW_IP:
                self.new_ip(line)

            # a client has diconnected
            elif action == DISCONNECT:
                self.disconnect(line)

            # change the id of the current user (used at the first connexion)
            elif action == CHANGE_ID:
                self.change_id(line)
                # We send chests after the ID has been changed
                # otherwise, the chests IDs are -1 !
                self.send_own_chests()

            # if a movement is received
            elif action == MOVE:
                mover_id = get_id_from_all_packet(line)
                unparsed_target = self.get_data_from(line)
                target = unparsed_target.split("/")
                target = list(map(int, target))
                self.game.distant_player_move(mover_id, target)
                # ID + Action + str

            # if the action is on chests
            elif action == CHEST:
                player_id = get_id_from_all_packet(line)
                data = self.get_data_from(line)
                parsed_data = data.split("_")
                # If we receive a packet composed of all chests positions ("positions_13/2/10_12/1/11...")
                if parsed_data[0] == "positions":
                    self.game.world_map.generate_distant_chests(
                        parsed_data[1:]
                    )
                #  If we receivee a packet that requests one of our chests ("request_13/13_10...")
                if parsed_data[0] == "request":
                    print(
                        "[Chests] Player [{}] requested the chest at position ".format(
                            player_id
                        ),
                        parsed_data[1:],
                    )
                    self.handle_requested_chest(parsed_data[1:], player_id)
                # If we receive a packet containing the items ("items_Plate/Armor_Axe_Sword...")
                if parsed_data[0] == "ownership":
                    print("[Chests] You receveid the ownership of the chest")
                    self.take_ownership(parsed_data[1:], open=True)
                # If we receive a packet of a player that disconnects
                if parsed_data[0] == "disconnect":
                    print(
                        "[Chests] You received a disconnection packet containing a chest"
                    )
                    self.take_ownership(parsed_data[1:], open=False)
                    self.send_new_ownership(parsed_data[1:])
                #  If we receive a refuse packet ("refuse")
                if parsed_data[0] == "refuse":
                    print(
                        "[Chests] Your chest request has been refused, your inventory might be full"
                    )
                # If we receive an update packet ("update_13/20"")
                if parsed_data[0] == "update":
                    self.update_chests(parsed_data[1:])
                if parsed_data[0] == "changeowner":
                    self.change_owner(parsed_data[1:])

            elif action == CHAT:
                self.chat_message(line)

            elif action == ENEMY:
                self.receive_enemy_update(line)
            else:
                print("[Unknown Action :", action, "]")

    def create_connection(self, line):
        # if line[1] not in self.players:
        #     self.players[line[1]] = Player()
        ip = get_ip_from_packet(line)
        self._client.stdin.write(str.encode("!" + ip + "\n"))
        self._client.stdin.flush()

    def first_connection(self, line):
        """Manage the first connection with a client and send the info to other clients

        Args:
            target_ip (str): string that contains the ip:port of the new connection
        """

        target_ip = self.get_data_from(line)
        new_id = self.generate_new_id()
        self.game.other_player[int(new_id)] = DistantPlayer(self.game)
        self.game.distant_enemy_list[int(new_id)] = []
        for ip in self.client_ip_port:
            # this loop sends to all other client the information (<ip>:<port>) of the new player
            msg = str(str(self.game.own_id) + " 2 " + target_ip + ":" + new_id)
            self.send_message(msg, ip)

        for ip in self.client_ip_port:
            # this loop sends to the new user all the ip contained in self.client_ip_port and all the relative position of the players
            # block that sends the ip
            msg = str(
                str(self.game.own_id)
                + " 2 "
                + ip
                + ":"
                + self.game.player_id[ip]
            )
            self.send_message(msg, target_ip)
        # Send to the client his id and our ip:port (he will add it to his player_id dictionnary)
        msg = str(
            str(self.game.own_id)
            + " 10 "
            + self.ip
            + ":"
            + str(self.port)
            + ":"
            + new_id
        )
        self.send_message(msg, target_ip)
        # add to our player_id dictionnary his id
        self.game.player_id[target_ip] = new_id
        # Sending position of chests and players to the new ip
        self.init_player_pos(target_ip)
        self.init_chests_pos(target_ip)
        self.init_distant_enemy(target_ip)

    def generate_new_id(self):
        if len(self.game.player_id) > 0:
            # get last id and add 1 to it
            new_id = str(
                max(
                    int(max(list(self.game.player_id.values()))) + 1,
                    self.game.own_id + 1,
                )
            )
        else:
            new_id = str(self.game.own_id + 1)
        return new_id

    def init_player_pos(self, target_ip):
        """Sends our position to the new player"""
        # Send the position of other players
        for id, player in self.game.other_player.items():
            pX, pY = player.get_current_pos()
            pos_msg = str(id) + " 4 " + str(pX) + "/" + str(pY)
            self.send_message(pos_msg, target_ip)

        # Send our current position to the new connexion
        pX, pY = self.game.player.get_current_pos()
        pos_msg = str(self.game.own_id) + " 4 " + str(pX) + "/" + str(pY)
        self.send_message(pos_msg, target_ip)

    def init_chests_pos(self, target_ip):
        """First sends the position of local chests
        and then the position of distant chests to the connecting
        player

        Args:
            target_ip (str): IP+port of the connection player
        """
        # LOCAL CHESTS
        local_chests_pos = self.game.world_map.local_chests_pos
        pos_msg = str(self.game.own_id) + " 6 " + "positions"
        # Formatting and adding the message every local chest pos (i know the game id is already in the first field but it's easier for me like this first)
        for chest_pos in local_chests_pos:
            pos_msg += (
                "_"
                + str(chest_pos[0])
                + "/"
                + str(chest_pos[1])
                + "/"
                + str(self.game.own_id)
            )
        # Sending packet
        self.send_message(pos_msg, target_ip)

        # DISTANT CHESTS
        dist_chests_pos = self.game.world_map.dist_chests_pos
        dist_chests = self.game.world_map.dist_chests
        pos_msg = str(self.game.own_id) + " 6 " + "positions"
        # Formatting and adding the message every local chest pos
        for chest_pos in dist_chests_pos:
            pos_msg += (
                "_"
                + str(chest_pos[0])
                + "/"
                + str(chest_pos[1])
                + "/"
                + str(dist_chests[chest_pos[1]][chest_pos[0]].owner_id)
            )
        # Sending packet
        self.send_message(pos_msg, target_ip)

    def new_connexion(self, line):
        """Handle a new connexion (new client) on the network

        Args:
            line (str)
        """
        # self.players[line[1]] = Player()
        # Establish connection with the new client
        self.create_connection(line)
        # Manage first connection / info to other clients
        self.first_connection(line)

        try:
            client = self.get_data_from(line)
            self.add_to_clients(client)
        except Exception as e:
            print("Error new connexion", e)
        # add the new ip to the client_ip_port set

    def new_ip(self, line):
        """Add a new ip to the set

        Args:
            line (str)
        """
        # data is in the form "ip:port:id"
        self.create_connection(line)
        id = get_id_from_packet(line)
        ip = get_ip_from_packet(line)
        self.game.player_id[ip] = id
        self.game.other_player[int(id)] = DistantPlayer(self.game)
        self.game.distant_enemy_list[int(id)] = []
        print("[Server] New connection [" + id + "] ", "with ip :", ip)
        try:
            self.add_to_clients(ip)
        except Exception as e:
            print("Error new ip", e)
        self.init_distant_enemy(ip)

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
            p_id = get_id_from_all_packet(line)
            self.remove_from_other_player(p_id)
            # self.kill(client)
            # self.remove_connexion(client)
        except Exception as e:
            print("Error disconnect", e)
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

        del self.game.player_id[client]
        self.client_ip_port.remove(client)
        self._client.stdin.write(str.encode(str("-" + client + "\n")))

    def remove_from_player_id(self, client):
        """remove the client from the dict player_id

        Args:
            client (string): ip:port
        """
        del self.player_id[client]

    def remove_from_other_player(self, p_id):
        """remove the player from the game

        Args:
            p_id (int): id of the player to remove
        """
        #Editing the map :
        pos = self.game.other_player[p_id].get_current_pos()
        self.game.world_map.map[pos[1]][pos[0]].wall=False
        del self.game.other_player[p_id]
        #Deleting all enemy of the player
        del self.game.distant_enemy_list[p_id]


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

    @staticmethod
    def get_action_from(line):
        """get action part of the packet

        Args:
            line (string): string of the packet

        Raises:
            Exception: if the packet is not normative

        Returns:
            string : action
        """
        line = line.split(" ")
        if len(line) == 1:
            raise Exception("Can't split the line")
        return line[1]

    def change_id(self, line):
        """Change current client id by the one given in the packet

        Args:
            line (string) : packet
        """
        ip = get_ip_from_packet(line)
        own_id = get_id_from_packet(line)
        self.game.player_id[ip] = line.split(" ")[0]
        self.game.own_id = int(own_id)
        self.game.other_player[int(line.split(" ")[0])] = DistantPlayer(
            self.game
        )
        self.game.distant_enemy_list[int(line.split(" ")[0])] = []

    def chat_message(self, line):
        my_message = self.get_data_from(line)
        print("[Chat] My message : ", my_message)
        self.game.chat.receive_chat(my_message)

    def send_message(self, msg: str, ip: str, chat=False):
        """format message and send it to the ip

        Args:
            msg (string): packet
            ip (string): recipient
        """
        msg = msg.replace("\n", "")
        if not chat:
            try:
                check_message(msg)
            except ValueError:
                print("Error send_message : value")
                return

            msg = msg.split(" ")
            self._client.stdin.write(str.encode(ip + "\n"))
            self._client.stdin.flush()
            for word in msg:
                word += "\n"
                word = str.encode(word)
                self._client.stdin.write(word)
                self._client.stdin.flush()
        if chat:

            msg = msg.split(" ")
            # Creation of a list with the data we want to send
            # msg[0] : Player id
            # msg [1] : action
            mylist = [msg[0], msg[1]]

            # concatenation of data segment in order to make it msg [3]
            # we use _ in order to separate words " " doesn't work trought our data sending
            my_str = str(self.game.own_id) + "_said_:_"
            for i in range(2, len(msg)):
                my_str += msg[i] + "_"
            mylist.append(my_str)
            self._client.stdin.write(str.encode(ip + "\n"))
            self._client.stdin.flush()
            for word in mylist:
                word += "\n"
                word = str.encode(word)
                self._client.stdin.write(word)
                self._client.stdin.flush()

    def send_global_message(self, msg, chat=False):
        """SOON DEPRECATED
        A function that sends to every other player in the game
        instead of juste one

        Args:
            msg (str): the message/packet to send
        """
        try:
            self.send_message(msg, "all", chat=chat)
        except:
            print("Couldn't send a global message")

    ### -- CHESTS RELATED -- ###

    def send_own_chests(self):
        """This function is called when a client connects to
        the host of the game, after the ID change (to get the right owner ID for
        chests). It sends to every other players the position of the new client local chests"""
        local_chests_pos = self.game.world_map.local_chests_pos
        local_chests = self.game.world_map.local_chests

        # Generating local chests
        self.game.world_map.generate_local_chests()

        # Updating chests ID
        for pos in local_chests_pos:
            local_chests[pos[1]][pos[0]].owner_id = self.game.own_id

        pos_msg = str(self.game.own_id) + " 6 " + "positions"
        # Formatting and adding the message every local chest pos
        for chest_pos in local_chests_pos:
            pos_msg += (
                "_"
                + str(chest_pos[0])
                + "/"
                + str(chest_pos[1])
                + "/"
                + str(self.game.own_id)
            )
        # Sending packet
        self.game.network.send_global_message(pos_msg)

    def handle_requested_chest(self, parsed_data, player_id):
        """Handles what to do when receiving a chest request

        Args:
            parsed_data (str): the parsed data
            player_id ([type]): id of the player that requested the chest
        """
        pos = tuple(map(int, parsed_data[0].split("/")))
        inv_slots = parsed_data[1]

        # Getting back player ip
        try:
            for ip, id in self.game.player_id.items():
                if str(id) == str(player_id):
                    player_ip = ip
        except:
            print("[Chests] : Can't find player in id list")

        # If we are the owner of the chest
        if self.game.world_map.local_chests[pos[1]][pos[0]]:
            # Checking if player has enough slots in inventory to get the full chest
            if int(inv_slots) >= len(
                self.game.world_map.local_chests[pos[1]][pos[0]].loots
            ):

                # Building the packet and sending message
                msg = (
                    str(self.game.own_id)
                    + " 6 "
                    + "ownership"
                    + "_"
                    + str(pos[0])
                    + "/"
                    + str(pos[1])
                )
                print("[Chests] : Gave property to", player_id)
                self.send_message(msg, player_ip)

                # Sending packet to inform of the ownership change
                print("[Chests] : Sending ownership change")

                # Updating chest locally
                self.game.world_map.local_chests[pos[1]][pos[0]] = None
                self.game.world_map.dist_chests[pos[1]][pos[0]] = DistantChest(
                    pos, int(player_id)
                )

                udpate_msg = (
                    str(self.game.own_id)
                    + " 6 "
                    + "changeowner"
                    + "_"
                    + str(pos[0])
                    + "/"
                    + str(pos[1])
                    + "_"
                    + str(player_id)
                )
                self.send_global_message(udpate_msg)
            else:
                # Sending a refuse message
                msg = str(self.game.own_id) + " 6 " + "refuse"
                self.send_message(msg, player_ip)
        else:
            # Sending a refuse message
            msg = str(self.game.own_id) + " 6 " + "refuse"
            self.send_message(msg, player_ip)

    def update_chests(self, parsed_data):
        """Updates a chest when an update packet is received
        Checks if the chest is local or distant to update it

        Args:
            parsed_data (str): the parsed packet data
        """
        pos = tuple(map(int, parsed_data[0].split("/")))
        if self.game.world_map.local_chests[pos[1]][pos[0]]:
            self.game.world_map.local_chests[pos[1]][pos[0]].is_opened = True
            self.game.world_map.local_chests[pos[1]][
                pos[0]
            ].image = dict_img_obj["chestO"].convert_alpha()
            self.game.world_map.local_chests[pos[1]][
                pos[0]
            ].image.set_colorkey((0, 0, 0))
        else:
            self.game.world_map.dist_chests[pos[1]][pos[0]].is_opened = True
            self.game.world_map.dist_chests[pos[1]][
                pos[0]
            ].image = dict_img_obj["d_chestO"].convert_alpha()
            self.game.world_map.dist_chests[pos[1]][pos[0]].image.set_colorkey(
                (0, 0, 0)
            )

    def take_ownership(self, parsed_data, open=False):
        """Take the ownership of the chest if the ownership packet is receveid, and then
        automatically opens it because we don't want the player to click two times on it to open it

        Args:
            parsed_data (str): The packet parsed data
        """
        pos = tuple(map(int, parsed_data[0].split("/")))
        # Changing location of chest to the map of local chests
        self.game.world_map.dist_chests[pos[1]][pos[0]] = None
        self.game.world_map.local_chests[pos[1]][pos[0]] = Chest(pos)
        # Opening the chest
        if open:
            # Sending packet to update chest for everyone (actually update = inform that a chest is opened)
            udpate_msg = (
                str(self.game.own_id)
                + " 6 "
                + "update"
                + "_"
                + str(pos[0])
                + "/"
                + str(pos[1])
            )
            self.send_global_message(udpate_msg)
            self.game.world_map.local_chests[pos[1]][pos[0]].use_chest(
                self.game.player
            )

    def change_owner(self, parsed_data):
        """Changes the owner of the distant chest when a change owner packet
        is received. If it's our chest, do nothing

        Args:
            parsed_data (str): the parsed packet data
        """
        pos = tuple(map(int, parsed_data[0].split("/")))
        player_id = parsed_data[1]
        if self.game.world_map.dist_chests[pos[1]][pos[0]]:
            self.game.world_map.dist_chests[pos[1]][pos[0]].owner_id = int(
                player_id
            )

    def send_chests_disconnect(self):
        """Sends to the first player in our player ip dict our chests
        before disconnecting
        """
        print("[Chests] Sending chests before disconnetion")
        for pos in self.game.world_map.local_chests_pos:
            if not self.game.world_map.local_chests[pos[1]][pos[0]].is_opened:
                msg = (
                    str(self.game.own_id)
                    + " 6 "
                    + "disconnect"
                    + "_"
                    + str(pos[0])
                    + "/"
                    + str(pos[1])
                )
                player_ip = random.choice(list(self.game.player_id.keys()))
                self.send_message(msg, player_ip)

    def send_new_ownership(self, parsed_data):
        """Sends the fact that we took ownership of the chest to other
        players"""
        pos = tuple(map(int, parsed_data[0].split("/")))
        msg = (
            str(self.game.own_id)
            + " 6 "
            + "changeowner"
            + "_"
            + str(pos[0])
            + "/"
            + str(pos[1])
            + "_"
            + str(self.game.own_id)
        )
        self.send_global_message(msg)

    ### --- Enemy related --- ###
    def init_distant_enemy(self, target_ip):
        """Send all local enemy data to other player when first connecting"""
        basic_line = (
            str(self.game.own_id) + " 8 " + "1/"
        )  # id + manage enemy + new enemy
        for enemy in self.game.local_enemy_list:
            line = (
                basic_line
                + str(enemy.id)
                + "/"
                + str(enemy.tileX)
                + "/"
                + str(enemy.tileY)
            )
            self.send_message(line, target_ip)

    def send_enemy_disconnect(self):
        """Sends to the first player in our player ip dict our enemies
        before disconnecting
        """
        print("[Enemy] Sending enemies before disconnetion")
        for enemy in self.game.local_enemy_list:
            self.give_enemy_ownership(enemy, random.choice(list(self.game.player_id.keys())), isDisconnexion=True)

    def give_enemy_ownership(self, enemy, player_ip, isDisconnexion=False):
        msg = (
            str(self.game.own_id)
            + " 8 "
            + "2/")
        if isDisconnexion :
            msg = msg + "1/"
        else :
            msg = msg + "0/"
        msg =  (msg + str(enemy.id)
            + "/"
            + str(enemy.tileX)
            + "/"
            + str(enemy.tileY))
        self.send_message(msg, player_ip)

    def send_enemy_update(self, e_id, pos, isNewEnemy=False):
        """Send a message when a enemy is created or moving
        Args:
            e_id (int): local enemy id (each enemy is identified by owner_id + local_id)
            pos (tuple(int,int)): the position of the enemy we are updating
            isNewEnemy (bool): is True when it's the first time we are sending a packet about this enemy
        """
        # isNew value is 1 when it's a new enemy
        line = str(self.game.own_id) + " 8 "
        line = line + "{isNew}".format(isNew=1 if isNewEnemy else 0)
        line = line + "/" + str(e_id) + "/" + str(pos[0]) + "/" + str(pos[1])
        self.send_global_message(line)

    def receive_enemy_update(self, line):
        """Manage the reception of enemy update
        Args :
            line : the content of the packet received
        """
        owner_id = get_id_from_all_packet(line)
        data = self.get_data_from(line)
        data = data.split("/")
        if int(data[0])==2 :
            type_ownership = data[1]
            enemy_id = int(data[2])
            pos = (int(data[3]), int(data[4]))
            if not (len(self.game.local_enemy_list) >= 5) and (type_ownership==1):
                #We already have fully enemy list, so we delete the enemy since there can not be as much enemy in the game
                print("[ENEMY] You received the ownership of an enemy !")
                new_e = local_Enemy(self.game.world_map, enemy_id)
                new_e.tileX, new_e.tileY = pos
                self.send_enemy_update(
                new_e.id, new_e.get_pos(), isNewEnemy=True)
                self.game.local_enemy_list.append(new_e)
        else:
            enemy_id = int(data[1])
            pos = (int(data[2]), int(data[3]))
            if int(data[0])==1:
                self.game.distant_enemy_list[owner_id].append(
                    distant_Enemy(self.game.world_map, enemy_id, pos)
                )
            else:
                enemy = find_enemy_by_id(
                    self.game.distant_enemy_list[owner_id], enemy_id
                )
                enemy.walk(pos)