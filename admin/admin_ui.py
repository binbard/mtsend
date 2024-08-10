import globals
import tkinter as tk
from tkinter import messagebox
from models.event_type import EventType
from models.device import Device
from lib.device_manager import DeviceManager
import queue
import threading
from functools import partial

def get_title(subtitle = ''):
    title = globals.APP_NAME + ' ' + 'Administrator'
    if subtitle == '': return title
    return title + ' - ' + subtitle

class AdminUI(tk.Tk):
    def __init__(self, service_queue, device_manager: DeviceManager):
        super().__init__()
        self.title(get_title())
        self.geometry("800x600")

        self.service_queue = service_queue
        self.device_manager = device_manager

        self.toolbar_frame = tk.Frame(self, bd=1, relief=tk.RAISED)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH)

        self.create_toolbar()
        self.screen_my_network()

    def create_toolbar(self):

        exit_button = tk.Button(self.toolbar_frame, text="Exit", command=self.exit_app)
        exit_button.pack(side=tk.LEFT, padx=2, pady=2)

        about_button = tk.Button(self.toolbar_frame, text="About", command=self.about_action)
        about_button.pack(side=tk.LEFT, padx=2, pady=2)

        you_button = tk.Button(self.toolbar_frame, text="You", command=self.you_action)
        you_button.pack(side=tk.LEFT, padx=2, pady=2)

        screen1_button = tk.Button(self.toolbar_frame, text="My Network", command=self.screen_my_network)
        screen1_button.pack(side=tk.LEFT, padx=2, pady=2)

        screen2_button = tk.Button(self.toolbar_frame, text="My Groups", command=self.screen_my_groups)
        screen2_button.pack(side=tk.LEFT, padx=2, pady=2)

    def exit_app(self):
        self.quit()

    def about_action(self):
        messagebox.showinfo("About", f"Solution made by: {", ".join(globals.AUTHORS)} for Tally CodeBrewers")

    def you_action(self):
        messagebox.showinfo("You", f"You are {globals.DEVICE_NAME}")

    def screen_my_network(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.title(get_title('My Network'))

        tk.Label(self.main_frame, text="Devices List", bg="brown",fg="white",font=("Georgia",12)).pack(padx=40, pady=20)

        self.devices_frame = None

        def update_devices(self):
            if self.devices_frame is None:
                self.devices_frame = tk.Frame(self.main_frame)
                self.devices_frame.pack(fill=tk.BOTH, expand=True)
            else:
                for widget in self.devices_frame.winfo_children():
                    widget.destroy()
            
            devices = self.device_manager.get_devices()
            
            headers = ["IP", "Name", "Type", "Online"]
            header_frame = tk.Frame(self.devices_frame)
            header_frame.pack(fill=tk.X)

            for col, header in enumerate(headers):
                header_label = tk.Label(header_frame, text=header, font=('bold'))
                header_label.pack(side=tk.LEFT, padx=5, pady=5)

            device_frame = tk.Frame(self.devices_frame)
            device_frame.pack(fill=tk.BOTH, expand=True)

            for row, device in enumerate(devices):
                ip_label = tk.Label(device_frame, text=device.ip)
                name_label = tk.Label(device_frame, text=device.name)
                type_label = tk.Label(device_frame, text='Client')
                online_label = tk.Label(device_frame, text="Online" if device.last_seen else "Offline")

                ip_label.pack(side=tk.LEFT, padx=5, pady=5)
                name_label.pack(side=tk.LEFT, padx=5, pady=5)
                type_label.pack(side=tk.LEFT, padx=5, pady=5)
                online_label.pack(side=tk.LEFT, padx=5, pady=5)
                tk.Label(device_frame, text="|").pack(side=tk.LEFT, padx=5, pady=5)


            
        def handle_queue(self):
            for i in range(self.service_queue.qsize()):
                try:
                    data = self.service_queue.get(timeout=1)
                    print('lol', data)
                    dtype = data.get('type')
                    if dtype == EventType.DEVICES_UPDATED:
                        update_devices(self)
                    else:
                        self.service_queue.put(data)
                except queue.Empty:
                    pass
            self.after(1000, partial(handle_queue, self))

        self.after(1000, partial(handle_queue, self))


    def screen_my_groups(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.title(get_title('My Groups'))
        
        tk.Label(self.main_frame, text="Groups List", bg="brown",fg="white",font=("Georgia",12)).pack(padx=40, pady=20)
        

if __name__ == "__main__":
    app = ClientUI()
    app.mainloop()
