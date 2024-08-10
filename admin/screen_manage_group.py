import tkinter as tk
from functools import partial
from tkinter import messagebox


def show_group_details(admin_ui, group_name):
    details_frame = admin_ui.details_frame
    for widget in details_frame.winfo_children():
        widget.destroy()

    group_info = admin_ui.group_details.get(group_name, {})
    description = group_info.get("description", "No description available.")
    members = group_info.get("members", [])
    
    tk.Label(details_frame, text=f"Group: {group_name}", font=("Arial", 14), bg="brown", fg="white").pack(anchor="w", padx=10, pady=(10, 5))
    tk.Label(details_frame, text=f"Description: {description}", font=("Arial", 12), anchor="w").pack(anchor="w", padx=10, pady=5)
    
    members_frame = tk.Frame(details_frame)
    members_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    admin_ui.member_check_vars = {}

    for member in members:
        member_name = member["name"]
        ip_address = member["ip"]
        status = member["status"]

        member_frame = tk.Frame(members_frame, bg="white", relief=tk.RAISED, bd=2)
        member_frame.pack(fill=tk.X, pady=2)

        tk.Label(member_frame, text=f"Name: {member_name}", font=("Arial", 12), bg="white").pack(side=tk.LEFT, padx=5)
        tk.Label(member_frame, text=f"IP: {ip_address}", font=("Arial", 12), bg="white").pack(side=tk.LEFT, padx=5)
        tk.Label(member_frame, text=f"Status: {status}", font=("Arial", 12), bg="white").pack(side=tk.LEFT, padx=5)
        var = tk.BooleanVar()
        admin_ui.member_check_vars[member_name] = var
        check_button = tk.Checkbutton(member_frame, variable=var, bg="white")
        check_button.pack(side=tk.RIGHT, padx=5)

    remove_button = tk.Button(details_frame, text="Remove Selected Users", font=("Arial", 12), bg="red", fg="white", command=partial(remove_selected_users, admin_ui, group_name))
    remove_button.pack(anchor="w", padx=10, pady=10)

def remove_selected_users(admin_ui, group_name):
    selected_members = [name for name, var in admin_ui.member_check_vars.items() if var.get()]
    if not selected_members:
        messagebox.showinfo("No Selection", "No users selected for removal.")
        return

    # Prompt the user for confirmation
    confirmation = messagebox.askyesno(
        "Confirm Removal",
        f"Do you really want to remove {len(selected_members)} member(s)?"
    )

    if confirmation:
        # Remove selected members from the group
        admin_ui.group_details[group_name]["members"] = [
            member for member in admin_ui.group_details[group_name]["members"] if member["name"] not in selected_members
        ]
        # Refresh the group details display
        show_group_details(admin_ui, group_name)

def screen_manage_group(admin_ui):
    admin_ui.details_frame = tk.Frame(admin_ui.main_frame)
    admin_ui.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    for widget in admin_ui.main_frame.winfo_children():
        widget.destroy()

    admin_ui.title(admin_ui.get_title('Manage Groups'))

    header_frame = tk.Frame(admin_ui.main_frame)
    header_frame.pack(padx=40, pady=(20, 10), fill=tk.X)

    tk.Label(header_frame, text="Manage Groups", bg="brown", fg="white", font=("Georgia", 12)).pack()

    manage_frame = tk.Frame(admin_ui.main_frame)
    manage_frame.pack(padx=40, pady=10, fill=tk.BOTH, expand=True)

    group_names_frame = tk.Frame(manage_frame)
    group_names_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    admin_ui.details_frame = tk.Frame(manage_frame)
    admin_ui.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    separator = tk.Frame(manage_frame, height=2, bg="gray")
    separator.pack(side=tk.LEFT, fill=tk.X, padx=(0, 10))

    # Dummy data for groups
    admin_ui.group_details = {
        "Group A": {
            "description": "This is Group A",
            "members": [
                {"name": "Alice", "ip": "192.168.1.1", "status": "Online"},
                {"name": "Bob", "ip": "192.168.1.2", "status": "Offline"}
            ]
        },
        "Group B": {
            "description": "This is Group B",
            "members": [
                {"name": "Charlie", "ip": "192.168.1.3", "status": "Online"},
                {"name": "David", "ip": "192.168.1.4", "status": "Offline"}
            ]
        },
        "Group C": {
            "description": "This is Group C",
            "members": [
                {"name": "Eve", "ip": "192.168.1.5", "status": "Online"},
                {"name": "Frank", "ip": "192.168.1.6", "status": "Offline"}
            ]
        }
    }

    for group_name in admin_ui.group_details.keys():
        label = tk.Label(group_names_frame, text=group_name, padx=10, pady=5, anchor='w', cursor="hand2", font=("Arial", 14), bg="lightgray")
        label.pack(fill=tk.X)
        label.bind("<Button-1>", partial(lambda event, g=group_name: show_group_details(admin_ui, g)))
