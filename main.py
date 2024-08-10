from dotenv import load_dotenv
load_dotenv()

import globals
from models.device_type import DeviceType

from app import MtSendApplication
import argparse

def main():
    parser = argparse.ArgumentParser(description='MtSend Application')
    parser.add_argument('--type', type=str, help='Device type')
    parser.add_argument('--listen', type=int, help='Listen on port')
    parser.add_argument('--recv', type=int, help='Listen on port')
    parser.add_argument('--send', type=int, help='Send to port')
    parser.add_argument('--name', type=str, help='Device name')
    args = parser.parse_args()
    
    if args.type == 'server' or args.type == 'admin':
        globals.DEVICE_TYPE = DeviceType.ADMIN
    
    if args.listen or args.recv:
        globals.MC_PORT = args.listen or args.recv
    
    if args.send:
        globals.MC_SEND_PORT = args.send

    if args.name:
        globals.DEVICE_NAME = args.name
    
    app = MtSendApplication()
    app.run()


if __name__ == '__main__':
    globals.DEV_MODE = True
    main()