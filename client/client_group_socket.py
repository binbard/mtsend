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

def fmt_size(bytes):
    return f"{bytes / 1024:.2f} KB" if bytes < 1024 * 1024 else f"{bytes / (1024 * 1024):.2f} MB"

class GroupSocket():
    def __init__(self, device_manager: DeviceManager, group_manager: GroupManager, group_id: str):
        self.device_manager = device_manager
        self.group_manager = group_manager
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.GROUP_FILE_CHUNK_SIZE)

        self.group_id = group_id
        self.group: Group = self.group_manager.get_group(group_id)

        self.sock.bind((globals.MC_IP_ADDR, self.group.port))
        
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

                mprint(f'Packet received: {ptype.name}')

                if ptype == PacketType.GROUP_LEAVE_REQ:
                    mprint(f'Admin {address} asking to leave the group')
                
                elif ptype == PacketType.GROUP_JOIN_ACK:
                    mprint(f'Admin {address} confirmed join request')
                
                elif ptype == PacketType.GROUP_JOIN_REQ:
                    mprint(f'Admin {address} asking to join the group')
                
                elif ptype == PacketType.GROUP_TEXT_MESSAGE:
                    json_data = json.loads(pdata.decode('utf-8'))
                    self.group.add_message(json_data)
                    message: Message = Message(json_data['type'], json_data['content'])
                    mprint(f'{self.group.name}: {message.content}')
                    globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})
                
                elif ptype == PacketType.GROUP_FILE_MESSAGE:
                    file_json = json.loads(pdata.decode('utf-8'))
                    file = File.from_dict(file_json)
                    file_name = file.name[:30]
                    self.dfiles[file_name] = file
                    # self.group.add_message(f'Receiving <{file.name}> Size: {file.size} Chunks: {file.total_chunks}')
                    message: Message = Message(json_data['type'], json_data['content'])

                    globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})
                    mprint(f'Admin {address} sending a file info {file_name}')

                elif ptype == PacketType.GROUP_FILE_SEND_COMPLETE:
                    file_name = pdata.decode('utf-8')
                    file_name = file_name[:30]
                    file = self.dfiles[file_name]
                    if file is None:
                        mprint(f'File {file_name} not found')
                        continue
                    if file.is_completed():
                        mprint(f"Full file received: {file_name} Chunks received: {len(file.data)}/{file.total_chunks}")
                        file.save_file()
                        self.group.add_message(f'Received <{file.name}> Size: {fmt_size(file.size)}')
                        message: Message = Message(json_data['type'], json_data['content'])
                        globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})
                        mprint(f'Admin {address} sending a file info {file_name}')
                
                elif ptype == PacketType.GROUP_FILE_CHUNK:
                    mprint(f'Admin {address} sent a file chunk')
                    # mprint(f'Total chunk size: {len(pdata)}, expected: {struct.calcsize(globals.group_file_subfmt_str)}')
                    pdata = pdata.ljust(globals.GROUP_FILE_TOTAL_SIZE - 1, b'\x00')

                    unpacked_data = struct.unpack(globals.group_file_subfmt_str, pdata)
                    file_name = unpacked_data[0].decode('utf-8').strip('\x00')
                    chunk_number = unpacked_data[1]
                    data = unpacked_data[2]
                    mprint("lol", file_name, chunk_number)
                    file = self.dfiles[file_name]
                    if file is None:
                        mprint(f'File {file_name} not found')
                        continue
                    mprint(f'Chunk {chunk_number} received for {file_name} file')
                    if chunk_number == file.total_chunks:
                        data = data.rstrip(b'\x00')
                    file.add_chunk(chunk_number, data)
                
            except socket.timeout:
                pass
            except Exception as e:
                mprint(f'Error: {e}')
                pass
    
    def send_message(self, packet_type: PacketType, data: bytes):
        if len(data) > globals.GROUP_FILE_TOTAL_SIZE - 1:
            raise ValueError(f'Data length is greater than {globals.GROUP_FILE_TOTAL_SIZE - 1} is {len(data)}')
        if self.sock is None or self.group.port is None or self.group.port == 0:
            print(f"Group {self.group.name} is not connected")
            return
        
        packet = struct.pack(globals.group_fmt_str, packet_type.value, data)
        self.sock.sendto(packet, (globals.MC_SEND_HOST, self.group.port+1))
    
    def __del__(self):
        self.sock.close()
        mprint('MainSocket has been closed')
