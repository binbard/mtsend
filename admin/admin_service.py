from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from models.packet_type import PacketType

class AdminService():
    def __init__(self, main_socket: MainSocket, device_manager: DeviceManager, group_manager: GroupManager):
        self.main_socket = main_socket
        self.device_manager = device_manager    
        self.group_manager = group_manager
    
    def create_new_group(self, name, desc = ''):
        group = self.group_manager.add_group(name, desc, self.device_manager.get_device_name())
        self.main_socket.send(PacketType.GROUP_JOIN_REQ, b'')