"""Network config"""

from os import path
from .assets import src_folder

CLIENT_NAME = 'tcpclient'
CLIENT_PATH = path.join(src_folder, CLIENT_NAME)


SERVER_NAME = 'tcpserver'
SERVER_PATH = path.join(src_folder, SERVER_NAME)

FIRST_CONNECTION = "0"
NEW_IP = "2"
DISCONNECT = "3"
MOVE = "4"
CHEST = "6"
CHAT = "7"
CHANGE_ID = "10"
