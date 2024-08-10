import globals
import socket

def get_my_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        sock.connect((globals.MC_HOST, globals.MC_PORT))

        local_ip = sock.getsockname()[0]
        
        return local_ip
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
