import tkinter as tk

class AdminUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Home")
        self.geometry("800x600")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.draw_screen1()

    def draw_screen1(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="This is Screen 1").pack(pady=20)
        tk.Button(self.main_frame, text="Go to Screen 2", command=self.draw_screen2).pack(pady=10)

    def draw_screen2(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="This is Screen 2").pack(pady=20)
        tk.Button(self.main_frame, text="Go to Screen 1", command=self.draw_screen1).pack(pady=10)
