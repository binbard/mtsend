import globals
import tkinter as tk
from functools import partial
from models.event_type import EventType
import queue

def screen_my_network(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.title(self.get_title('My Network'))

        tk.Label(self.main_frame, text="Devices List", bg="brown",fg="white",font=("Georgia",12)).pack(padx=40, pady=20)

        self.devices_frame = None

        def update_devices(self):
            if self.devices_frame is None:
                self.devices_frame = tk.Frame(self.main_frame)
                self.devices_frame.pack(fill=tk.BOTH, expand=True)
            else:
                for widget in self.devices_frame.winfo_children():
                    widget.destroy()

            if self.device_manager.is_empty():
                tk.Label(self.devices_frame, text="No online devices", font=('bold')).pack()
                return
            
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
                
        update_devices(self)
        
            
        def handle_queue(self):
            for i in range(globals.service_queue.qsize()):
                try:
                    data = globals.service_queue.get(timeout=1)
                    print('lol', data)
                    dtype = data.get('type')
                    if dtype == EventType.DEVICES_UPDATED:
                        update_devices(self)
                    else:
                        globals.service_queue.put(data)
                except queue.Empty:
                    pass
            self.after(1000, partial(handle_queue, self))

        self.after(1000, partial(handle_queue, self))