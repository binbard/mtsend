import globals
from lib.main_socket import MainSocket
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from models.packet_type import PacketType
import uuid
import json
import threading
import socket
import random
import string
import struct
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
            s.bind(('0.0.0.0', port))
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
                        print(f"Connected by {addr}")
                        group_data = json.dumps(group.__dict__)
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
