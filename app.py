import globals
from globals import mprint
from models.device_type import DeviceType
from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from helpers.get_self_ip import get_my_ip
import queue

class MtSendApplication():
    def __init__(self):
        self.group_manager = GroupManager()
        self.device_manager = DeviceManager()
        self.device_manager.start()
        
        self.main_socket = MainSocket(self.device_manager, self.group_manager)

        self.app_ui = None
        self.on = True
        
        if globals.HEADLESS_MODE:
            mprint('Headless mode enabled')
            return
        
        if globals.DEVICE_TYPE == DeviceType.ADMIN:
            from admin.admin_ui import AdminUI
            self.app_ui = AdminUI(self.main_socket, self.device_manager, self.group_manager)
        else:
            from client.client_ui import ClientUI
            self.app_ui = ClientUI(self.main_socket, self.device_manager, self.group_manager)
    
    def run(self):
        mprint('=> You are user', globals.DEVICE_NAME, globals.MC_IP)
        self.main_socket.start()

        if globals.HEADLESS_MODE:
            while self.on:
                pass
        else:
            self.app_ui.mainloop()
    
    def __del__(self):
        mprint('MtSendApplication has been closed')