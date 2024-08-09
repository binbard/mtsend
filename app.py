import globals
from globals import mprint

from lib.main_socket import MainSocket

class MtSendApplication():
    def __init__(self):
        self.main_socket = MainSocket()
        self.on = True
    
    def run(self):
        self.main_socket.listen()
    
    def __del__(self):
        self.main_socket.close()
        mprint('MtSendApplication has been closed')