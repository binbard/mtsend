import os
import logging
from models.device_type import DeviceType
import names
from queue import Queue
import importlib
import helpers.db_helper as DbHelper

### Constants

DEV_MODE = False

APP_NAME = 'MtSend'

DEVICE_ONLINE_TIMEOUT = 10
DEVICE_TYPE = DeviceType.CLIENT

DEVICE_NAME = None

MC_HOST = '224.0.0.2'
MC_PORT = 8090

TESTING_LOCAL = False

MC_SEND_HOST = MC_HOST
MC_SEND_PORT = MC_PORT

fmt_str = 'B1023s'

GROUP_FILE_TOTAL_SIZE = 10240
GROUP_FILE_CHUNK_SIZE = 10204
group_fmt_str = f"B{GROUP_FILE_TOTAL_SIZE - 1}s"
group_file_subfmt_str = "30sI10204s"

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

db_helper: DbHelper = importlib.import_module('helpers.db_helper')

DEVICE_NAME = db_helper.get_devicename()
if DEVICE_NAME is None:
    DEVICE_NAME = names.get_full_name()
    db_helper.set_devicename(DEVICE_NAME)


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