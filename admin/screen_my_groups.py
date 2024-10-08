import globals
import tkinter as tk
from functools import partial
from models.event_type import EventType
from models.message import Message
from models.file import File
from tkinter import filedialog
import os
import queue

def open_file(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        os.startfile(file_path)

def show_chat(self, group_id):
    for widget in self.chat_display.winfo_children():
        widget.destroy()

    group = self.admin_service.group_manager.get_group(group_id)

    self.current_group_id = group_id

    chat_history = group.messages
    for message in chat_history:
        if type(message) is str:
            message = {"type": "text", "content": message}
            label = tk.Label(self.chat_display, text=message["content"], anchor='w', padx=10, pady=5, bg="white")
            label.pack(fill=tk.X, pady=2)
        elif message["type"] == "text":
            label = tk.Label(self.chat_display, text=message["content"], anchor='w', padx=10, pady=5, bg="white")
            label.pack(fill=tk.X, pady=2)
        elif message["type"] == "file":
            file_name = message["content"]
            button = tk.Button(self.chat_display, text=f"File: {file_name}", relief=tk.FLAT, bg="lightblue", padx=10, pady=5)
            button.pack(fill=tk.X, pady=2)
            button.bind("<Button-1>", lambda e, f=file_name: open_file(f))
    
    for widget in self.names_frame.winfo_children():
        if widget.cget("text") == group.name:
            widget.config(bg="brown", fg="white")
            self.active_label = widget
        else:
            widget.config(bg="lightgray", fg="black")

def send_message(self):
    if self.current_group_id is None:
        return
    msg = self.chat_entry.get()
    if not msg or msg.isspace():
        send_file(self)
    if msg:
        label = tk.Label(self.chat_display, text=msg, anchor='w', padx=10, pady=5, bg="white")
        label.pack(fill=tk.X, pady=2)
        self.chat_entry.delete(0, tk.END)
        message: Message = Message("text", msg)
        self.admin_service.send_message(self.current_group_id, message)

def choose_file(self):
    self.selected_file_path = filedialog.askopenfilename()
    if self.selected_file_path:
        file_name = os.path.basename(self.selected_file_path)
        self.selected_file_label.config(text=f"Selected File: {file_name}")
    else:
        self.selected_file_label.config(text="No file selected")

def send_file(self):
    if self.current_group_id is None or not hasattr(self, 'selected_file_path'):
        return
    
    file_path = self.selected_file_path
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    chunk_size = globals.GROUP_FILE_CHUNK_SIZE - 1
    total_chunks = file_size // chunk_size + 1

    file = File(file_name, file_name.split('.')[-1], total_chunks)
    file.path = file_path
    
    message = Message("file", file)
    self.admin_service.send_message(self.current_group_id, message)
    
    show_chat(self, self.current_group_id)
    self.selected_file_label.config(text="No file selected")
    del self.selected_file_path


def screen_my_groups(self):
    self.current_screen = "my_groups"

    for widget in self.main_frame.winfo_children():
        widget.destroy()

    self.title(self.get_title('My Groups'))

    self.current_group_id = None
    
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

    chat_input_frame = tk.Frame(chat_frame)
    chat_input_frame.pack(fill=tk.X)

    self.chat_entry = tk.Entry(chat_input_frame, font=("Arial", 12))
    self.chat_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

    send_button = tk.Button(chat_input_frame, text="Send", font=("Arial", 12), command=partial(send_message, self))
    send_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    choose_file_button = tk.Button(chat_input_frame, text="Choose File", font=("Arial", 12), command=partial(choose_file, self))
    choose_file_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    self.selected_file_label = tk.Label(chat_input_frame, text="No file selected", font=("Arial", 12), fg="gray")
    self.selected_file_label.pack(side=tk.LEFT, padx=10, pady=5)

    def update_groups(self):
        for widget in self.names_frame.winfo_children():
            widget.destroy()

        groups = self.admin_service.group_manager.groups
        
        for group in groups:
            label = tk.Label(self.names_frame, text=group.name, padx=10, pady=5, anchor='w', cursor="hand2", font=("Arial", 14), bg="lightgray")
            label.pack(fill=tk.X)
            label.bind("<Button-1>", lambda event, g=group.id: partial(show_chat, self)(g))
    
    update_groups(self)

    def handle_queue(self):
        if self.current_screen != "my_groups":
            return
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
