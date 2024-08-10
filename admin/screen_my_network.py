import tkinter as tk
from functools import partial
from models.event_type import EventType
import queue

def screen_my_network(self):
    for widget in self.main_frame.winfo_children():
        widget.destroy()
    
    self.title(self.get_title('My Network'))

    tk.Label(self.main_frame, text="Devices List", bg="brown", fg="white", font=("Georgia", 12)).pack(padx=40, pady=20)

    self.devices_frame = None
    self.check_vars = []
    self.device_labels = []
    
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

            var = tk.BooleanVar()
            check_button = tk.Checkbutton(device_frame, variable=var)
            check_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.check_vars.append(var)
            self.device_labels.append(device.name)

    update_devices(self)
    
    def handle_queue(self):
        for i in range(self.service_queue.qsize()):
            try:
                data = self.service_queue.get(timeout=1)
                dtype = data.get('type')
                if dtype == EventType.DEVICES_UPDATED:
                    update_devices(self)
                else:
                    self.service_queue.put(data)
            except queue.Empty:
                pass
        self.after(1000, partial(handle_queue, self))

    self.after(1000, partial(handle_queue, self))

    # Function to handle "Add Group" button click
    def add_group():
        # Create a pop-up window
        group_popup = tk.Toplevel(self)
        group_popup.title("Add Group")

        tk.Label(group_popup, text="Enter Group Name:").pack(padx=10, pady=10)
        group_name_entry = tk.Entry(group_popup)
        group_name_entry.pack(padx=10, pady=10)

        def confirm_group():
            group_name = group_name_entry.get().strip()
            if group_name:  # Ensure that the group name is not empty
                selected_devices = [name for var, name in zip(self.check_vars, self.device_labels) if var.get()]
                if selected_devices:
                    display_group_info(group_name, selected_devices)
                else:
                    display_group_info(group_name, ["No devices selected"])
            else:
                display_group_info("Group name cannot be empty", [])

            group_popup.destroy()

        tk.Button(group_popup, text="Confirm", command=confirm_group).pack(padx=10, pady=10)

    # Add the "Add Group" button below the devices list
    tk.Button(self.main_frame, text="Add Group", command=add_group).pack(pady=20)

    # Initialize the group display frame here
    self.group_display_frame = tk.Frame(self.main_frame)
    self.group_display_frame.pack(pady=20, fill=tk.X)

    # Function to display group information in the frame below "Add Group" button
    def display_group_info(group_name, selected_devices):
        # Create a new frame for each group
        group_frame = tk.Frame(self.group_display_frame)
        group_frame.pack(fill=tk.X, pady=10)

        # Display the group name
        group_label = tk.Label(group_frame, text=f"Group Name: {group_name}", font=('bold', 12))
        group_label.pack(pady=5)

        # Display the selected devices
        devices_label = tk.Label(group_frame, text="Selected Devices:", font=('bold', 10))
        devices_label.pack(pady=5)

        devices_text = "\n".join(selected_devices)
        devices_list_label = tk.Label(group_frame, text=devices_text)
        devices_list_label.pack(pady=5)