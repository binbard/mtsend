from globals import mprint
import globals
import socket
import threading
from models.packet_type import PacketType
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from models.message import Message
from models.file import File
from models.event_type import EventType
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
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.GROUP_FILE_CHUNK_SIZE)

        self.group_id = group_id
        self.group: Group = self.group_manager.get_group(group_id)

        self.sock.bind((get_my_ip(), self.group.port))
        
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        if not globals.TESTING_LOCAL:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        mreq = struct.pack('4sl', socket.inet_aton(globals.MC_HOST), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(1)

        self.dfiles = {
            'none.txt': File('none.txt', 'txt', 0)
        }
    
    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        mprint(f'Client Group Listening on PORT {self.group.port}')
        while True:
            try:
                data, address = self.sock.recvfrom(globals.GROUP_FILE_TOTAL_SIZE)

                packet_data = struct.unpack(globals.group_fmt_str, data)
                
                ptype = PacketType(packet_data[0])
                pdata = packet_data[1].rstrip(b'\x00')

                if ptype == PacketType.GROUP_LEAVE_REQ:
                    mprint(f'Admin {address} asking to leave the group')
                
                elif ptype == PacketType.GROUP_JOIN_ACK:
                    mprint(f'Admin {address} confirmed join request')
                
                elif ptype == PacketType.GROUP_JOIN_REQ:
                    mprint(f'Admin {address} asking to join the group')
                
                elif ptype == PacketType.GROUP_TEXT_MESSAGE:
                    mprint(f'Admin {address} sending a text')
                    json_data = json.loads(pdata.decode('utf-8'))
                    self.group.add_message(json_data)
                    message: Message = Message(json_data['type'], json_data['content'])
                    print(message.content)
                    globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})
                
                elif ptype == PacketType.GROUP_FILE_MESSAGE:
                    json_data = json.loads(pdata.decode('utf-8'))
                    file_data = json_data['content']
                    file = File.from_dict(file_data)
                    self.dfiles[file.name] = file
                    self.group.add_message(file.name)
                    message: Message = Message(json_data['type'], json_data['content'])
                    globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})
                    mprint(f'Admin {address} sending a file info')
                
                elif ptype == PacketType.GROUP_FILE_CHUNK:
                    mprint(f'Admin {address} sent a file chunk')

                    unpacked_data = struct.unpack(globals.group_file_subfmt_str, pdata)
                    file_name = unpacked_data[0].decode('utf-8').strip('\x00')
                    chunk_number = unpacked_data[1]
                    data = unpacked_data[2]
                    file = self.dfiles[file_name]
                    if file is None:
                        mprint(f'File {file_name} not found')
                        continue
                    print(f'Chunk {chunk_number} received')
                    file.add_chunk(chunk_number, data)
                    if file.is_completed():
                        print(f"Full file received: {file_name}")
                
            except socket.timeout:
                pass
            except Exception as e:
                mprint(f'Error: {e}')
    
    def send(self, packet_type: PacketType, data: bytes, address = (globals.MC_SEND_HOST, globals.MC_SEND_PORT)):
        if len(data) > globals.GROUP_FILE_TOTAL_SIZE - 1:
            raise ValueError(f'Data length is greater than {globals.GROUP_FILE_TOTAL_SIZE - 1}')
        
        packet = struct.pack(globals.group_fmt_str, packet_type.value, data)
        self.sock.sendto(packet, address)
    
    def __del__(self):
        self.sock.close()
        mprint('MainSocket has been closed')
