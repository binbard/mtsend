from globals import mprint
import globals
import socket
import threading
from models.packet_type import PacketType
from lib.device_manager import DeviceManager
import struct
import time
import json

class MainSocket():
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', globals.MC_PORT))
        
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        mreq = struct.pack('4sl', socket.inet_aton(globals.MC_HOST), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(1)
    
    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.online_teller, daemon=True).start()
        while True:
            pass

    def online_teller(self):
        mprint('Online teller started')
        while True:
            json_data = json.dumps({'name': globals.DEVICE_NAME})
            self.send(PacketType.ONLINE, json_data.encode(), (globals.MC_SEND_HOST, globals.MC_SEND_PORT))
            # mprint('Sent online packet')
            time.sleep(10)

    def listen(self):
        mprint(f'Listen PORT {globals.MC_PORT} and Send PORT {globals.MC_SEND_PORT}')
        while True:
            try:
                data, address = self.sock.recvfrom(1024)

                packet_data = struct.unpack(globals.fmt_str, data)
                
                ptype = PacketType(packet_data[0])
                pdata = packet_data[1].rstrip(b'\x00')

                if ptype == PacketType.ONLINE:
                    json_data = json.loads(pdata.decode('utf-8'))
                    name = json_data['name'] if 'name' in json_data else 'Unknown'
                    self.device_manager.device_updater(address[0], name)

                elif ptype == PacketType.OFFLINE:
                    json_data = json.loads(pdata.decode('utf-8'))
                    name = json_data['name'] if 'name' in json_data else 'Unknown'
                    self.device_manager.remove_device(address)
                    
                elif ptype == PacketType.GROUP_JOIN_REQ:
                    mprint(f'Admin {address} asking to join the group')
            except socket.timeout:
                pass
            except Exception as e:
                mprint(f'Error: {e}')
    
    def send(self, packet_type: PacketType, data: bytes, address):
        if len(data) > 1023:
            raise ValueError('Data length is greater than 1023')
        
        packet = struct.pack(globals.fmt_str, packet_type.value, data)
        self.sock.sendto(packet, address)
    
    def __del__(self):
        self.sock.close()
        mprint('MainSocket has been closed')