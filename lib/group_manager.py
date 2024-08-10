import globals
from globals import mprint
from models.device import Device, DeviceType
from models.group import Group
from models.event_type import EventType
import time
import threading
import queue

class GroupManager():
    def __init__(self):
        self.groups: Group = globals.db_helper.get_groups()
    
    def add_group(self, id, name, creator = globals.DEVICE_NAME, participants = [], port = 0) -> Group:
        group = Group(id, name, creator, participants, port = port)
        if group not in self.groups:
            self.groups.append(group)
            mprint(f'New group {name} has been created')
            # globals.db_helper.set_group(group)
            globals.service_queue.put({'type': EventType.GROUPS_UPDATED})
            return group
    
    def remove_group(self, id):
        group = self.get_group(id)
        if group:
            self.groups.remove(group)
            mprint(f'Group {group.name} has been removed')
            # globals.db_helper.remove_group(group)
            globals.service_queue.put({'type': EventType.GROUPS_UPDATED})
    
    def get_group(self, id) -> Group:
        for group in self.groups:
            if group.id == id:
                return group
        return None