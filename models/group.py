class Group():
    def __init__(self, name: str, desc: str = ''):
        self.name = name
        self.desc = ''
        self.admins = []
        self.members = []

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