import os
import logging
from models.device_type import DeviceType
import names
from queue import Queue

### Constants

DEV_MODE = False

APP_NAME = 'MtSend'

DEVICE_ONLINE_TIMEOUT = 10
DEVICE_TYPE = DeviceType.CLIENT

DEVICE_NAME = names.get_full_name()

MC_HOST = '224.0.0.2'
MC_PORT = 8090

MC_SEND_HOST = MC_HOST
MC_SEND_PORT = MC_PORT

fmt_str = 'B1023s'

AUTHORS = [
    'Gaurav Singh Mehra',
    'Suryansh Bajpai',
    'Harshit Jawla',
]

service_queue = Queue()

home_directory = os.path.dirname(os.path.abspath(__file__))

data_directory = os.path.join(home_directory, '_data')
temp_directory = os.path.join(data_directory, '_temp')

if not os.path.exists(home_directory):
    os.makedirs(home_directory)

if not os.path.exists(temp_directory):
    os.makedirs(temp_directory)

def mpath(file_name, dir = home_directory):
    return os.path.join(dir, file_name)

def temp_path(file_name):
    return mpath(file_name, temp_directory)

def data_path(file_name):
    return mpath(file_name, data_directory)

groups_file = data_path('groups.json')

### Logging configuration

logger = logging.getLogger(APP_NAME)
handler = logging.FileHandler(data_path('server.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def mprint(*args):
    global DEV_MODE
    message = ' '.join(map(str, args))
    if DEV_MODE:
        print(message)
    else:
        logger.info(message)

print('Globals module loaded')