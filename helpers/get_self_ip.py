import globals
import socket, psutil

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception as e:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def get_is_up(ip_address):
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for interface_name, interface_addresses in interfaces.items():
        for address in interface_addresses:
            if address.family == socket.AF_INET and address.address == ip_address:
                if stats[interface_name].isup:
                    return True
                else:
                    return False
    return False
