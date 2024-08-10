import globals
from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from models.packet_type import PacketType
import uuid
import json

class AdminService():
    def __init__(self, main_socket: MainSocket, device_manager: DeviceManager, group_manager: GroupManager):
        self.main_socket = main_socket
        self.device_manager = device_manager    
        self.group_manager = group_manager
    
    def create_new_group(self, name, participants):
        group_id = uuid.uuid4()
        group = self.group_manager.add_group(group_id, name, desc = '', creator = globals.DEVICE_NAME)
        for participant in participants:
            group.add_member(participant)
        group_data = json.dumps(group.__dict__)
        self.main_socket.send(PacketType.GROUP_JOIN_REQ, group_data.encode())
        return group
    