"""Network config"""

from os import path
from .assets import src_folder

CLIENT_NAME = 'tcpclient'
CLIENT_PATH = path.join(src_folder, CLIENT_NAME)


SERVER_NAME = 'tcpserver'
SERVER_PATH = path.join(src_folder, SERVER_NAME)
