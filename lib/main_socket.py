from globals import mprint
import globals
import socket
import threading
from models.packet_type import PacketType
from lib.device_manager import DeviceManager
import struct

class MainSocket():
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind((globals.MC_HOST, globals.MC_PORT))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(1024)

            packet_data = struct.unpack(globals.fmt_str, data)
            
            ptype = PacketType(packet_data[0])

            if ptype == PacketType.ONLINE:
                mprint(f'User {address} is online')
            elif ptype == PacketType.OFFLINE:
                mprint(f'User {address} is offline')
            
            elif ptype == PacketType.GROUP_JOIN_REQ:
                mprint(f'Admin {address} asking to join the group')
    
    def send(self, packet_type: PacketType, data: bytes, address):
        if len(data) > 1023:
            raise ValueError('Data length is greater than 1023')
        
        packet = struct.pack(globals.fmt_str, packet_type.value, data)
        self.sock.sendto(packet, address)