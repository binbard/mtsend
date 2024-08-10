import globals
import tkinter as tk
from tkinter import messagebox
from models.event_type import EventType
from models.device import Device
from admin.screen_my_groups import screen_my_groups
from admin.screen_my_network import screen_my_network
from lib.device_manager import DeviceManager
from lib.group_manager import GroupManager
from admin.admin_service import AdminService
from lib.main_socket import MainSocket
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
        screen_my_network(self)
    
    def get_title(self, subtitle = ''):
        title = globals.APP_NAME + ' ' + 'Administrator'
        if subtitle == '': return title
        return title + ' - ' + subtitle

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

    def exit_app(self):
        self.quit()

    def about_action(self):
        messagebox.showinfo("About", f"Solution made by: {", ".join(globals.AUTHORS)} for Tally CodeBrewers")

    def you_action(self):
        messagebox.showinfo("You", f"You are {globals.DEVICE_NAME}")

if __name__ == "__main__":
    app = ClientUI()
    app.mainloop()
