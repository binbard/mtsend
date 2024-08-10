import globals
from globals import mprint
from models.device import Device, DeviceType
from models.group import Group
from models.event_type import EventType
import time
import threading
import queue

class GroupManager():
    def __init__(self, service_queue: queue.Queue):
        self.groups: Group = []
        self.service_queue = service_queue
    
    def add_group(self, name, desc, creator):
        group = Group(name, desc, creator)
        self.groups.append(group)
        mprint(f'New group {name} has been created')
        self.service_queue.put({'type': EventType.GROUPS_UPDATED})
    
    def remove_group(self, name, creator):
        group = Group(name, creator)
        self.groups.remove(group)
        mprint(f'Group {name} has been removed')
        self.service_queue.put({'type': EventType.GROUPS_UPDATED})