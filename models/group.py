import json

class Group():
    def __init__(self, id, name: str, creator: str, participants = [], port = 0):
        self.id = id
        self.name = name
        self.desc = ''
        self.creator = creator
        self.ip = ''
        self.port = port
        self.password = ''
        self.admins = []
        self.participants = participants
        self.messages = []
        self.sock = None

    def add_participant(self, participant):
        if participant not in self.participants:
            self.participants.append(participant)
    
    def add_admin(self, admin):
        if admin not in self.admins:
            self.admins.append(admin)
    
    def add_message(self, message):
        self.messages.append(message)
    
    def remove_participant(self, participant):
        if participant in self.participants:
            self.participants.remove(participant)
    
    def remove_admin(self, admin):
        if admin in self.admins:
            self.admins.remove(admin)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Group):
            return self.id == value.id
        return False
    
    def to_dict(self):
        mdict = {k: v for k, v in self.__dict__.items() if not callable(v) and not k.startswith('__')}
        mdict['sock'] = None
        return mdict