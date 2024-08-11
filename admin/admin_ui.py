import globals
import tkinter as tk
from tkinter import messagebox
from models.event_type import EventType
from models.device import Device
from admin.screen_my_groups import screen_my_groups
from admin.screen_my_network import screen_my_network
from admin.screen_manage_group import screen_manage_group
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from admin.admin_service import AdminService
from lib.main_socket import MainSocket
from helpers.get_self_ip import get_my_ip
import queue
import threading
from functools import partial

def get_title(subtitle = ''):
    title = globals.APP_NAME + ' ' + 'Administrator'
    if subtitle == '': return title
    return title + ' - ' + subtitle

class AdminUI(tk.Tk):
    def __init__(self, main_socket: MainSocket, device_manager: DeviceManager, group_manager: GroupManager):
        super().__init__()
        self.title(get_title())
        self.geometry("800x600")

        self.admin_service = AdminService(main_socket, device_manager, group_manager)

        self.toolbar_frame = tk.Frame(self, bd=1, relief=tk.RAISED)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH)

        self.create_toolbar()

        self.current_screen = "my_network"
        self.add_fake_groups()
        screen_my_network(self)
    
    def get_title(self, subtitle = ''):
        title = globals.APP_NAME + ' ' + 'Administrator'
        if subtitle == '': return title
        return title + ' - ' + subtitle
    
    def add_fake_groups(self):
        my_ip = get_my_ip()
        
        self.admin_service.group_manager.add_group("1", "Group 1", my_ip).messages = [
            {"type": "text", "content": "Welcome to Group 1!"},
            {"type": "text", "content": "This is a test message."},
            {"type": "file", "content": "hello.txt"}
        ]
        self.admin_service.group_manager.add_group("2", "Group 2", my_ip).messages = [{"type": "text", "content": "Group 2 chat history here."}]
        self.admin_service.group_manager.add_group("3", "Group 3", my_ip).messages = [{"type": "text", "content": "Chat history for Group 3."}]

    def create_toolbar(self):

        exit_button = tk.Button(self.toolbar_frame, text="Exit", command=self.exit_app)
        exit_button.pack(side=tk.LEFT, padx=2, pady=2)

        about_button = tk.Button(self.toolbar_frame, text="About", command=self.about_action)
        about_button.pack(side=tk.LEFT, padx=2, pady=2)

        you_button = tk.Button(self.toolbar_frame, text="You", command=self.you_action)
        you_button.pack(side=tk.LEFT, padx=2, pady=2)

        screen1_button = tk.Button(self.toolbar_frame, text="My Network", command=partial(screen_my_network, self))
        screen1_button.pack(side=tk.LEFT, padx=2, pady=2)

        screen2_button = tk.Button(self.toolbar_frame, text="My Groups", command=partial(screen_my_groups, self))
        screen2_button.pack(side=tk.LEFT, padx=2, pady=2)

        screen3_button = tk.Button(self.toolbar_frame, text="Manage Group", command=partial(screen_manage_group, self))
        screen3_button.pack(side=tk.LEFT, padx=2, pady=2)

    def exit_app(self):
        self.quit()

    def about_action(self):
        messagebox.showinfo("About", f"Solution made by: {', '.join(globals.AUTHORS)} for TCB")

    def you_action(self):
        messagebox.showinfo("You", f"You are {globals.DEVICE_NAME} and your IP is {globals.MC_IP}")