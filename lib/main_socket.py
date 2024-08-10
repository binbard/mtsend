from globals import mprint
import globals
import socket
import threading
from models.packet_type import PacketType
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from helpers.get_self_ip import get_my_ip
import struct
import time
import json

class MainSocket():
    def __init__(self, device_manager: DeviceManager, group_manager: GroupManager):
        self.device_manager = device_manager
        self.group_manager = group_manager
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((get_my_ip(), globals.MC_PORT))
        
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        if not globals.TESTING_LOCAL:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        mreq = struct.pack('4sl', socket.inet_aton(globals.MC_HOST), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(1)
    
    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.online_teller, daemon=True).start()

    def online_teller(self):
        mprint('Online teller started')
        while True:
            json_data = json.dumps({'name': globals.DEVICE_NAME})
            self.send(PacketType.ONLINE, json_data.encode(), (globals.MC_SEND_HOST, globals.MC_SEND_PORT))
            # mprint('Sent online packet')
            time.sleep(10)
    
    def get_group_info_from_admin(self, host: str, port: int):
        def connect_and_receive(self, host, port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((host, port))
                    print(f"Connected to admin on port {port}")

                    data = s.recv(1024)
                    if data:
                        packet_data = struct.unpack(globals.fmt_str, data)
                
                        ptype = PacketType(packet_data[0])
                        pdata = packet_data[1].rstrip(b'\x00')

                        if ptype == PacketType.GROUP_INFO:
                            json_data = json.loads(pdata.decode('utf-8'))
                            group_id = json_data['id']
                            group_name = json_data['name']
                            creator = json_data['creator']
                            participants = json_data['participants']
                            port = json_data['port']
                            print(f"Group ID: {group_id}")
                            print(f"Group Name: {group_name}")
                            print(f"Creator: {creator}")
                            print(f"Participants: {participants}")
                            print(f"Port: {port}")
                            self.group_manager.add_group(group_id, group_name, creator, participants, port)
                    else:
                        print("No data received from the server.")
            except socket.timeout:
                print(f"Connection timed out")
            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

        client_thread = threading.Thread(target=connect_and_receive, args=(self,host,port), daemon=True)
        client_thread.start()


    def listen(self):
        mprint(f'Listen PORT {globals.MC_PORT} and Send PORT {globals.MC_SEND_PORT}')
        while True:
            try:
                data, address = self.sock.recvfrom(1024)

                if address[0] == get_my_ip() and address[1] == globals.MC_PORT:
                    print('Ignoring self packet')
                    continue

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
                    group_data = json.loads(pdata.decode('utf-8'))
                    port = group_data['port']
                    participants = group_data['participants']
                    my_ip = get_my_ip()
                    if my_ip in participants:
                        self.get_group_info_from_admin(address[0], port)
                    else:
                        mprint('This group is not for me')
                
            except socket.timeout:
                pass
            except Exception as e:
                mprint(f'Error: {e}')
    
    def send(self, packet_type: PacketType, data: bytes, address = (globals.MC_SEND_HOST, globals.MC_SEND_PORT)):
        if len(data) > 1023:
            raise ValueError('Data length is greater than 1023')
        
        packet = struct.pack(globals.fmt_str, packet_type.value, data)
        # print('sending', packet_type, address)
        self.sock.sendto(packet, address)
    
    def __del__(self):
        self.sock.close()
        mprint('MainSocket has been closed')