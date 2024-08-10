from tinydb import TinyDB, Query
import os

_db = TinyDB(os.path.join('_data', 'db.json'))

Device = Query()
Group = Query()
Message = Query()

def get_devicename():
    device = _db.table('devices').get(Device.name.exists())
    return device['name'] if device else None

def set_devicename(name):
    _db.table('devices').upsert({'name': name}, Device.name.exists())

def get_deviceip():
    device = _db.table('devices').get(Device.ip.exists())
    return device['ip'] if device else None

def set_deviceip(ip):
    _db.table('devices').upsert({'ip': ip}, Device.ip.exists())

def get_groups():
    groups = _db.table('groups').all()
    for group in groups:
        group.pop('messages', None)
    return groups

def set_groups(groups):
    _db.table('groups').truncate()
    _db.table('groups').insert_multiple(groups)

def get_messages(group_id):
    group = _db.table('groups').get(Group.id == group_id)
    return group['messages'] if group else []

def add_group_message(group_id, message):
    group = _db.table('groups').get(Group.id == group_id)
    if group:
        messages = group['messages']
        messages.append(message)
        _db.table('groups').update({'messages': messages}, Group.id == group_id)

def set_group(group):
    _db.table('groups').upsert(group, Group.id == group.id)

def remove_group(group):
    _db.table('groups').remove(Group.id == group.id)

def set_messages(group_id, messages):
    group = _db.table('groups').get(Group.id == group_id)
    if group:
        _db.table('groups').update({'messages': messages}, Group.id == group_id)
    else:
        _db.table('groups').insert({'id': group_id, 'messages': messages})

def create_group(group):
    _db.table('groups').insert(group)
