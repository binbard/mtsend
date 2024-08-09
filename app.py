import globals
from globals import mprint

from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager

class MtSendApplication():
    def __init__(self):
        self.device_manager = DeviceManager()
        self.device_manager.start()
        
        self.main_socket = MainSocket(self.device_manager)
        self.on = True
    
    def run(self):
        mprint('=> You are user', globals.DEVICE_NAME)
        self.main_socket.start()
    
    def __del__(self):
        mprint('MtSendApplication has been closed')