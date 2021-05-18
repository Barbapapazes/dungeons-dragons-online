
import subprocess
import os
import queue
import signal
import time
import threading
from src.Player import DistantPlayer
from src.Map import dict_img_obj
from src.config.network import CLIENT_PATH, SERVER_PATH, FIRST_CONNECTION, NEW_IP, DISCONNECT, CHANGE_ID, MOVE, CHAT, CHEST
from src.utils.network import enqueue_output, get_ip, check_message, get_id_from_packet, get_ip_from_packet, get_id_from_all_packet
from src.Item import CONSUMABLE_ITEM, COMBAT_ITEM, ORES_ITEM, CombatItem, ConsumableItem, OresItem
from os import path
import traceback


class Network:
    def __init__(self, game):
        self.game = game
        self.player_id = game.player_id
        self.ip = get_ip()
        self.port = 8000
        self._server = self.create_serveur()
        print("[Server] Socket :", self.get_socket())

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
                self.send_chests()

            # if a movement is received
            elif action == MOVE:
                mover_id = get_id_from_all_packet(line)
                unparsed_target = self.get_data_from(line)
                target = unparsed_target.split("/")
                target = list(map(int, target))
                self.game.distant_player_move(
                    mover_id, target)
                # ID + Action + str
            
            # if the action is on chests
            elif action == CHEST:
                player_id = get_id_from_all_packet(line)
                data = self.get_data_from(line)
                parsed_data = data.split("_")
                # If we receive a packet composed of all chests positions
                if parsed_data[0] == "positions":
                    self.game.world_map.generate_distant_chests(parsed_data[1:])
                # If we receivee a packet that requests one of our chests
                if parsed_data[0] == "request":
                    print("[Chests] Player [{}] requested the chest at position ".format(player_id), parsed_data[1:])
                    self.handle_requested_chest(parsed_data[1:], player_id)
                # If we receive a packet containing the items
                if parsed_data[0] == "items":
                    print("[Chests] Your chest request has been accepted")
                    self.get_chests_items(parsed_data[1:])
                # If we receive a refuse packet
                if parsed_data[0] == "refuse":
                    print("[Chests] Your chest request has been refused, your inventory might be full")
                # If we receive an update packet
                if parsed_data[0] == "update":
                    self.update_chests(parsed_data[1:])
                    
            elif action == CHAT:
                self.chat_message(line)
            
            else:
                print("[Unknown Action :", action, "]")

    def create_connection(self, line):
        # if line[1] not in self.players:
        #     self.players[line[1]] = Player()
        ip = get_ip_from_packet(line)
        # data is of the form "ip:port:id"
        ip_array = ip.split(":")
        if len(ip_array) not in [2, 3]:
            return
        self.connections[ip] = subprocess.Popen(
            [CLIENT_PATH, ip_array[0], ip_array[1]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # queue.Queue() is a queue FIFO (First In First Out) with an unlimited size
        tmp_queue = queue.Queue()
        tmp_thread = threading.Thread(
            target=enqueue_output,
            args=(self.connections[ip].stdout, tmp_queue),
        )

        # the thread will die with the end of the main procuss
        tmp_thread.daemon = True
        # thread is launched
        tmp_thread.start()
        self.ping[ip] = (tmp_thread, tmp_queue)

    def first_connection(self, line):
        """Manage the first connection with a client and send the info to other clients

        Args:
            target_ip (str): string that contains the ip:port of the new connection
        """

        target_ip = self.get_data_from(line)
        new_id = self.generate_new_id()
        self.game.other_player[int(new_id)] = DistantPlayer()
        for ip in self.client_ip_port:
            # this loop sends to all other client the information (<ip>:<port>) of the new player
            msg = str(str(self.game.own_id) + " 2 "
                      + target_ip + ":" + new_id)
            self.send_message(msg, ip)

        for ip in self.client_ip_port:
            # this loop sends to the new user all the ip contained in self.client_ip_port and all the relative position of the players
            # block that sends the ip
            msg = str(str(self.game.own_id) + " 2 "
                      + ip + ":" + self.game.player_id[ip])
            self.send_message(msg, target_ip)
        # Send to the client his id and our ip:port (he will add it to his player_id dictionnary)
        msg = str(str(self.game.own_id) + " 10 "
                  + self.ip + ":" + str(self.port) + ":" + new_id)
        self.send_message(msg, target_ip)
        # add to our player_id dictionnary his id
        self.game.player_id[target_ip] = new_id
        # Sending position of chest and players to the new ip
        self.init_player_pos(target_ip)
        self.init_chests_pos(target_ip)
        
    def generate_new_id(self):
        if len(self.game.player_id) > 0:
            # get last id and add 1 to it
            new_id = str(
                max(int(max(list(self.game.player_id.values()))) + 1, self.game.own_id + 1))
        else:
            new_id = str(self.game.own_id + 1)
        return new_id

    def init_player_pos(self, target_ip):
        """Send the position of all player to the new client to init other_player position
        """
        # Send our current position to the new connexion
        pX, pY = self.game.player.get_current_pos()
        pos_msg = str(self.game.own_id) + " 4 " + str(pX) + "/" + str(pY)
        self.send_message(pos_msg, target_ip)
    
    def init_chests_pos(self, target_ip):
        """Sends the position of chests to the new client to init the chests positions"""
        # LOCAL CHESTS
        local_chests_pos = self.game.world_map.local_chests_pos
        pos_msg = str(self.game.own_id) + " 6 " + "positions"
        # Formatting and adding the message every local chest pos (i know the game id is already in the first field but it's easier for me like this first)
        for chest_pos in local_chests_pos:
            pos_msg += "_" + str(chest_pos[0]) + "/" + str(chest_pos[1]) + "/" + str(self.game.own_id)
        # Sending packet
        self.send_message(pos_msg, target_ip)

        # DISTANT CHESTS
        dist_chests_pos = self.game.world_map.dist_chests_pos
        dist_chests = self.game.world_map.dist_chests
        pos_msg = str(self.game.own_id) + " 6 " + "positions"
        # Formatting and adding the message every local chest pos
        for chest_pos in dist_chests_pos:
            pos_msg += "_" + str(chest_pos[0]) + "/" + str(chest_pos[1]) + "/" + str(dist_chests[chest_pos[1]][chest_pos[0]].owner_id)
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
        self.game.other_player[int(id)] = DistantPlayer()
        print("New connection : [", id, "] ", ip)
        try:
            self.add_to_clients(ip)
        except Exception as e:
            print("Error new ip", e)

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
            self.remove_from_other_player(int(self.player_id[client]))
            self.remove_from_player_id(client)
            self.kill(client)
            self.remove_connexion(client)
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
        self.client_ip_port.remove(client)

    def remove_from_player_id(self, client):
        """remove the client from the dict player_id

        Args:
            client (string): ip:port
        """
        del self.player_id[client]

    def remove_from_other_player(self, p_id):
        """remove the player from the dict other_player

        Args:
            p_id (int): id of the player to remove
        """
        del self.game.other_player[p_id]

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

    @ staticmethod
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

    @ staticmethod
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
        self.game.other_player[int(line.split(" ")[0])] = DistantPlayer()
    
    def send_chests(self):
        """This function is called when a client connects to 
        the host of the game, after the ID change. It sends to 
        every other players the position of the client local chests"""

        local_chests_pos = self.game.world_map.local_chests_pos
        local_chests = self.game.world_map.local_chests

        # Updating chests ID
        for pos in local_chests_pos:
            local_chests[pos[1]][pos[0]].owner_id = self.game.own_id

        pos_msg = str(self.game.own_id) + " 6 " + "positions"
        # Formatting and adding the message every local chest pos
        for chest_pos in local_chests_pos:
            pos_msg += "_" + str(chest_pos[0]) + "/" + str(chest_pos[1]) + "/" + str(self.game.own_id)
        # Sending packet
        self.game.network.send_global_message(pos_msg)        

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
                return

            msg = msg.split(" ")

            for word in msg:
                word += '\n'
                word = str.encode(word)
                self.connections[ip].stdin.write(word)
                self.connections[ip].stdin.flush()
        if(chat):

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
            for word in mylist:
                word += '\n'
                word = str.encode(word)
                self.connections[ip].stdin.write(word)
                self.connections[ip].stdin.flush()

    def send_global_message(self, msg):
        """Sends a message to everyone"""
        for player_ip in self.game.network.connections.keys():
            self.send_message(msg, player_ip)
    
    def handle_requested_chest(self, parsed_data, player_id):
        """Handles a chest request"""
        pos = tuple(map(int, parsed_data[0].split("/")))
        inv_slots = parsed_data[1]
        
        try: 
            for ip, id in self.game.player_id.items():
                if str(id)==str(player_id):
                    player_ip = ip
        except:
            print("[Chests] : Can't find player in id list")
        else:
            # Checking if player has enough slots in inventory to get the full chest
            if int(inv_slots) >= len(self.game.world_map.local_chests[pos[1]][pos[0]].loots):

                # Building the packet
                msg = str(self.game.own_id) + " 6 " + "items"
                for _ in range(len(self.game.world_map.local_chests[pos[1]][pos[0]].loots)):
                    item = self.game.world_map.local_chests[pos[1]][pos[0]].loots.pop()
                    item_name = item.name 
                    item_name = item_name.replace(" ", "/")
                    msg += "_" + item_name 
                
                # Sending approval packet
                self.send_message(msg, player_ip)
                self.game.world_map.local_chests[pos[1]][pos[0]].is_opened = True
                self.game.world_map.local_chests[pos[1]][pos[0]].image = dict_img_obj["chestO"].convert_alpha()
                self.game.world_map.local_chests[pos[1]][pos[0]].image.set_colorkey((0, 0, 0))
                print("[Chests] Accepted request from [{}]".format(player_id))

                # Sending packet to update chest for everyone 
                udpate_msg = str(self.game.own_id)  + " 6 " + "update" + "_" + str(pos[0]) + "/" + str(pos[1]) 
                self.send_global_message(udpate_msg)
            else:
                # Sending a refuse message
                msg = str(self.game.own_id) + " 6 " + "refuse"
                self.send_message(msg, player_ip)

    def get_chests_items(self, parsed_data):
        """Transform items given in a packet into
        items for the player"""
        for item in parsed_data:
            item_name = str(item).replace("/", " ")
            if item_name in COMBAT_ITEM:
                new_item = CombatItem(item_name)
            elif item_name in CONSUMABLE_ITEM:
                new_item = ConsumableItem(item_name)
            elif item_name in ORES_ITEM:
                new_item = OresItem(item_name)
            self.game.player.inventory.add_items([new_item])

    def update_chests(self, parsed_data):
        """Updates a chest that has been opened"""
        pos = tuple(map(int, parsed_data[0].split("/")))
        if self.game.world_map.local_chests[pos[1]][pos[0]]:
            self.game.world_map.local_chests[pos[1]][pos[0]].is_opened = True
            self.game.world_map.local_chests[pos[1]][pos[0]].image = dict_img_obj["chestO"].convert_alpha()
            self.game.world_map.local_chests[pos[1]][pos[0]].image.set_colorkey((0, 0, 0))
        else:
            self.game.world_map.dist_chests[pos[1]][pos[0]].is_opened = True
            self.game.world_map.dist_chests[pos[1]][pos[0]].image = dict_img_obj["d_chestO"].convert_alpha()
            self.game.world_map.dist_chests[pos[1]][pos[0]].image.set_colorkey((0, 0, 0))
        

