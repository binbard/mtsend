from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from models.packet_type import PacketType

class ClientService():
    def __init__(self, main_socket: MainSocket, device_manager: DeviceManager, group_manager: GroupManager):
        self.main_socket = main_socket
        self.device_manager = device_manager    
        self.group_manager = group_manager