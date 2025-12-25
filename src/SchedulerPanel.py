import tkinter as tk
from tkinter import messagebox
import datetime
import dateparser
from Task import Task

class SchedulerPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2C2F33")
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="SCHEDULER", bg="#2C2F33", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

        self.entry_id = self._make_field("DM Channel ID (from URL):")
        self.entry_time = self._make_field("Time (e.g. 'in 10m'):")
        self.entry_msg = self._make_field("Message:")

        tk.Button(self, text="SCHEDULE MESSAGE", bg="#7289DA", fg="white", font=("Arial", 11, "bold"), 
                  command=self.on_schedule, bd=0, pady=5).pack(pady=20, fill="x")

    def _make_field(self, label_text):
        tk.Label(self, text=label_text, bg="#2C2F33", fg="#99AAB5").pack(anchor="w", pady=(5,0))
        entry = tk.Entry(self, bg="#40444B", fg="white", insertbackground="white", bd=0, font=("Arial", 11))
        entry.pack(fill="x", pady=5, ipady=3)
        return entry

    # Helper methods for other panels to use
    def set_target_id(self, val):
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, str(val))

    def get_target_id(self):
        return self.entry_id.get().strip()

    def on_schedule(self):
        c_id = self.entry_id.get().strip()
        t_time = self.entry_time.get().strip()
        t_msg = self.entry_msg.get().strip()

        if not c_id or not t_time or not t_msg:
            messagebox.showerror("Error", "Missing fields")
            return

        dt = dateparser.parse(t_time, settings={'PREFER_DATES_FROM': 'future'})
        if not dt or dt < datetime.datetime.now():
            messagebox.showerror("Error", "Invalid Time")
            return

        new_task = Task(channel_id=int(c_id), message=t_msg, run_time=dt)
        self.controller.add_task(new_task)
        
        # Clear inputs
        self.entry_msg.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)