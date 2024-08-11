from globals import mprint
import globals
import socket
import threading
from models.packet_type import PacketType
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from helpers.get_self_ip import get_my_ip
from models.group import Group
import struct
import time
import json

class GroupSocket():
    def __init__(self, device_manager: DeviceManager, group_manager: GroupManager, group_id: str):
        self.device_manager = device_manager
        self.group_manager = group_manager
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.group_id = group_id
        self.group: Group = self.group_manager.get_group(group_id)

        print("Binding TOOOO", self.group.port+1)
        self.sock.bind((get_my_ip(), self.group.port+1))
        
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        if not globals.TESTING_LOCAL:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        mreq = struct.pack('4sl', socket.inet_aton(globals.MC_HOST), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(1)
    
    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        mprint(f'Admin Group Listen PORT {self.group.port}')
        while True:
            try:
                data, address = self.sock.recvfrom(1024)

                packet_data = struct.unpack(globals.fmt_str, data)
                
                ptype = PacketType(packet_data[0])
                pdata = packet_data[1].rstrip(b'\x00')

                if ptype == PacketType.GROUP_LEAVE_REQ:
                    mprint(f'Client {address} asking to join the group')
                
                elif ptype == PacketType.GROUP_JOIN_ACK:
                    mprint(f'Client {address} confirmed join group')
                
                elif ptype == PacketType.GROUP_JOIN_REQ:
                    mprint(f'Client {address} asking to join the group')
                
                elif ptype == PacketType.GROUP_FILE_CHUNK:
                    mprint(f'Client {address} sending a chunk not received')
                
            except socket.timeout:
                pass
            except Exception as e:
                mprint(f'Error: {e}')
    
    def send(self, packet_type: PacketType, data: bytes, address = (globals.MC_SEND_HOST, globals.MC_SEND_PORT)):
        if len(data) > 1023:
            raise ValueError('Data length is greater than 1023')
        
        packet = struct.pack(globals.fmt_str, packet_type.value, data)
        self.sock.sendto(packet, address)
    
    def __del__(self):
        self.sock.close()
        mprint('MainSocket has been closed')