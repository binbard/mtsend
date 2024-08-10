import globals
import tkinter as tk
from functools import partial
from models.event_type import EventType
import os
import queue

def open_file(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        os.startfile(file_path)

def show_chat(self, group_name):
    for widget in self.chat_display.winfo_children():
        widget.destroy()

    chat_history = self.group_chats.get(group_name, [])
    for message in chat_history:
        if message["type"] == "text":
            label = tk.Label(self.chat_display, text=message["content"], anchor='w', padx=10, pady=5, bg="white")
            label.pack(fill=tk.X, pady=2)
        elif message["type"] == "file":
            file_name = message["content"]
            button = tk.Button(self.chat_display, text=f"File: {file_name}", relief=tk.FLAT, bg="lightblue", padx=10, pady=5)
            button.pack(fill=tk.X, pady=2)
            button.bind("<Button-1>", lambda e, f=file_name: open_file(f))
    
    for widget in self.names_frame.winfo_children():
        if widget.cget("text") == group_name:
            widget.config(bg="brown", fg="white")
            self.active_label = widget
            # self.title_label.config(text=f"{group_name} Chat")
        else:
            widget.config(bg="lightgray", fg="black")

def send_message(self):
    message = self.chat_entry.get()
    if message:
        label = tk.Label(self.chat_display, text="You: " + message, anchor='w', padx=10, pady=5, bg="white")
        label.pack(fill=tk.X, pady=2)
        self.chat_entry.delete(0, tk.END)

def screen_my_groups(self):
    for widget in self.main_frame.winfo_children():
        widget.destroy()

    self.title(self.get_title('My Groups'))
    
    header_frame = tk.Frame(self.main_frame)
    header_frame.pack(padx=40, pady=(20, 10), fill=tk.X)

    tk.Label(header_frame, text="Groups List", bg="brown", fg="white", font=("Georgia", 12)).pack()

    groups_frame = tk.Frame(self.main_frame)
    groups_frame.pack(padx=40, pady=10, fill=tk.BOTH, expand=True)

    self.names_frame = tk.Frame(groups_frame)
    self.names_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    chat_frame = tk.Frame(groups_frame)
    chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    separator = tk.Frame(groups_frame, height=2, bg="gray")
    separator.pack(side=tk.LEFT, fill=tk.X, padx=(0, 10))

    self.chat_display = tk.Frame(chat_frame)
    self.chat_display.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

    self.group_chats = {
        "Group 1": [
            {"type": "text", "content": "Welcome to Group 1!"},
            {"type": "text", "content": "This is a test message."},
            {"type": "file", "content": "hello.txt"}
        ],
        "Group 2": [{"type": "text", "content": "Group 2 chat history here."}],
        "Group 3": [{"type": "text", "content": "Chat history for Group 3."}]
    }

    def update_groups(self):
        for widget in self.names_frame.winfo_children():
            widget.destroy()

        groups = self.client_service.group_manager.groups
        for group in groups:
            self.group_chats[group.name] = group.messages
            
        for group_name in self.group_chats.keys():
            label = tk.Label(self.names_frame, text=group_name, padx=10, pady=5, anchor='w', cursor="hand2", font=("Arial", 14), bg="lightgray")
            label.pack(fill=tk.X)
            label.bind("<Button-1>", lambda event, g=group_name: partial(show_chat, self)(g))
        
    update_groups(self)

    def handle_queue(self):
        for i in range(globals.service_queue.qsize()):
            try:
                data = globals.service_queue.get(timeout=1)
                dtype = data.get('type')
                if dtype == EventType.GROUPS_UPDATED:
                    update_groups(self)
                else:
                    globals.service_queue.put(data)
            except queue.Empty:
                pass
        self.after(1000, partial(handle_queue, self))

    self.after(1000, partial(handle_queue, self))
