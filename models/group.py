import json

class Group():
    def __init__(self, id, name: str, creator: str, participants = []):
        self.id = id
        self.name = name
        self.desc = ''
        self.creator = creator
        self.password = ''
        self.admins = []
        self.members = participants
        self.messages = []

    def add_member(self, member):
        if member not in self.members:
            self.members.append(member)
    
    def add_admin(self, admin):
        if admin not in self.admins:
            self.admins.append(admin)
    
    def remove_member(self, member):
        if member in self.members:
            self.members.remove(member)
    
    def remove_admin(self, admin):
        if admin in self.admins:
            self.admins.remove(admin)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Group):
            return self.id == value.id
        return False