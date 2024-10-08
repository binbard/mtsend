import globals
from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from models.packet_type import PacketType
from admin.admin_group_socket import GroupSocket
from models.message import Message
from models.file import File
from models.group import Group
from models.event_type import EventType
import uuid
import json
import threading
import socket
import random
import string
import struct
import os
import math
from typing import List

def generate_password(length=12) -> str:
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

class AdminService:
    def __init__(self, main_socket: MainSocket, device_manager: DeviceManager, group_manager: GroupManager):
        self.main_socket = main_socket
        self.device_manager = device_manager    
        self.group_manager = group_manager

    def listen_for_connections(self, port: int, group_id: str):
        group = self.group_manager.get_group(group_id)
        if group is None:
            print(f"Group {group_id} does not exist")
            return
        
        group.password = generate_password()
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((globals.MC_IP_ADDR, port))
            s.listen()
            s.settimeout(10)
            print(f"Listening for connections on port {port}...")

            try:
                while True:
                    conn, addr = s.accept()

                    if addr[0] not in group.participants:
                        print(f"Connection from {addr} is not allowed")
                        conn.close()
                        continue

                    with conn:
                        if group.sock is None:
                            print(f"Starting group socket for {group.name} on port {port}")
                            group_socket = GroupSocket(self.device_manager, self.group_manager, group_id)
                            group.sock = group_socket.sock
                            group_socket.start()
                        print(f"Connected by {addr}")
                        group_data = json.dumps(group.to_dict())
                        packet = struct.pack(globals.fmt_str, PacketType.GROUP_INFO.value, group_data.encode())
                        conn.sendall(packet)
            except socket.timeout:
                print(f"Group {group_id} [{group.name}] registration timeout")

    def create_new_group(self, name: str, participants: List[str]):
        print("Creating new group")
        group_id = str(uuid.uuid4())
        group = self.group_manager.add_group(group_id, name, creator=globals.DEVICE_NAME, participants=participants)
        print("only for", participants)
        for participant in participants:
            group.add_participant(participant)
        
        port = random.randint(10000, 65535)
        group.port = port

        listener_thread = threading.Thread(target=self.listen_for_connections, args=(port, group_id), daemon=True)
        listener_thread.start()

        group_data_json = json.dumps(group.__dict__)

        self.main_socket.send(PacketType.GROUP_JOIN_REQ, group_data_json.encode(), (globals.MC_SEND_HOST, globals.MC_SEND_PORT))

        return group
    
    def send_message(self, group_id: str, message: Message):
        group = self.group_manager.get_group(group_id)
        if group is None:
            print(f"Group {group_id} does not exist")
            return
        if group.sock is None:
            print(f"Group {group_id} is not connected")
            return

        if message.type == "file":
            file: File = message.content

            group.add_message(f"Sent <{file.name}>")
            globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})

            file_size = os.path.getsize(file.path)
            total_chunks = math.ceil(file_size / globals.GROUP_FILE_CHUNK_SIZE)

            file.size = file_size
            file.total_chunks = total_chunks

            file_json = json.dumps(file.to_dict())

            self.send_group_message(group, PacketType.GROUP_FILE_MESSAGE, file_json.encode())

            file_name = file.name.encode('utf-8').ljust(30, b'\x00')

            with open(file.path, 'rb') as f:
                sent_chunks = 0
                chunk = f.read(globals.GROUP_FILE_CHUNK_SIZE)

                while chunk:
                    sent_chunks += 1
                    chunk = chunk.ljust(globals.GROUP_FILE_CHUNK_SIZE, b'\x00')
                    packet = struct.pack(globals.group_file_subfmt_str, file_name, sent_chunks, chunk)
                    self.send_group_message(group, PacketType.GROUP_FILE_CHUNK, packet)
                    print(f'Sent chunk {sent_chunks}/{total_chunks} with size {len(chunk)}')

                    chunk = f.read(globals.GROUP_FILE_CHUNK_SIZE)
                print(f'Sent {sent_chunks} chunks')
            
            self.send_group_message(group, PacketType.GROUP_FILE_SEND_COMPLETE, file_name)

        else:
            message_data = message.__dict__
            message_json = json.dumps(message_data)
            self.send_group_message(group, PacketType.GROUP_TEXT_MESSAGE, message_json.encode())
            group.add_message(message_data)
            globals.service_queue.put({'type': EventType.GROUP_CHAT_UPDATED})

    def send_group_message(self, group: Group, packet_type: PacketType, data: bytes):
        if len(data) > globals.GROUP_FILE_TOTAL_SIZE - 1:
            raise ValueError(f'Data length is greater than {globals.GROUP_FILE_TOTAL_SIZE - 1} is {len(data)}')
        if group.sock is None or group.port is None or group.port == 0:
            print(f"Group {group.name} is not connected")
            return
        
        packet = struct.pack(globals.group_fmt_str, packet_type.value, data)
        print(f"Group Sending {packet_type.name} to {group.name}")
        group.sock.sendto(packet, (globals.MC_SEND_HOST, int(group.port)))