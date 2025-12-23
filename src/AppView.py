import tkinter as tk
from tkinter import messagebox
import datetime
import dateparser

from Task import Task
from TaskController import TaskController

class AppView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord DM Manager")
        self.geometry("900x500")
        self.configure(bg="#2C2F33")

        self.controller = TaskController(
            log_callback=self.log_msg,
            update_tasks_cb=self.refresh_task_list,
            update_contacts_cb=self.refresh_contact_list
        )

        self._build_ui()
        self.controller.start_background()
    
    def _build_ui(self):
        # --- LEFT: CONTACTS ---
        pnl_left = tk.Frame(self, bg="#23272A", width=250)
        pnl_left.pack(side="left", fill="y", padx=5, pady=5)
        pnl_left.pack_propagate(False)

        tk.Label(pnl_left, text="SAVED DMs", bg="#23272A", fg="#7289DA", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.contact_listbox = tk.Listbox(pnl_left, bg="#2C2F33", fg="white", bd=0)
        self.contact_listbox.pack(fill="both", expand=True, padx=5)
        self.contact_listbox.bind('<<ListboxSelect>>', self.on_contact_select)

        frame_btns = tk.Frame(pnl_left, bg="#23272A")
        frame_btns.pack(fill="x", pady=10)
        
        tk.Button(frame_btns, text="Save Channel ID", bg="#43B581", fg="white", command=self.on_save_contact).pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(frame_btns, text="Delete", bg="#F04747", fg="white", command=self.on_delete_contact).pack(side="right", padx=5, expand=True, fill="x")


        # --- MIDDLE: INPUTS ---
        pnl_mid = tk.Frame(self, bg="#2C2F33")
        pnl_mid.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(pnl_mid, text="SCHEDULER", bg="#2C2F33", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

        def make_field(label):
            tk.Label(pnl_mid, text=label, bg="#2C2F33", fg="#99AAB5").pack(anchor="w", pady=(5,0))
            entry = tk.Entry(pnl_mid, bg="#40444B", fg="white", insertbackground="white", bd=0, font=("Arial", 11))
            entry.pack(fill="x", pady=5, ipady=3)
            return entry
        
        # CHANGED: Label now asks for DM Channel ID
        self.entry_id = make_field("DM Channel ID (from URL):")
        self.entry_time = make_field("Time (e.g. 'in 10m'):")
        self.entry_msg = make_field("Message:")

        tk.Button(pnl_mid, text="SCHEDULE", bg="#7289DA", fg="white", font=("Arial", 11, "bold"), 
                  command=self.on_add_task, bd=0, pady=5).pack(pady=20, fill="x")


        # --- RIGHT: LOGS ---
        pnl_right = tk.Frame(self, bg="#23272A", width=300)
        pnl_right.pack(side="right", fill="y", padx=5, pady=5)
        pnl_right.pack_propagate(False)

        tk.Label(pnl_right, text="LOGS", bg="#23272A", fg="#7289DA", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.task_listbox = tk.Listbox(pnl_right, bg="#2C2F33", fg="white", height=8, bd=0)
        self.task_listbox.pack(fill="x", padx=5)

        tk.Label(pnl_right, text="System Output:", bg="#23272A", fg="#99AAB5").pack(anchor="w", padx=5, pady=(10,0))
        self.log_box = tk.Text(pnl_right, bg="#000000", fg="#00FF00", font=("Consolas", 8), bd=0)
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)

    # --- CALLBACKS ---

    def log_msg(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def refresh_task_list(self, tasks):
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            self.task_listbox.insert(tk.END, str(task))

    def refresh_contact_list(self, contacts):
        self.contact_listbox.delete(0, tk.END)
        for c in contacts:
            self.contact_listbox.insert(tk.END, str(c))

    def on_contact_select(self, event):
        selection = self.contact_listbox.curselection()
        if selection:
            index = selection[0]
            contact = self.controller.saved_contacts[index]
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(contact.channel_id))

    def on_save_contact(self):
        raw_id = self.entry_id.get().strip()
        if raw_id.isdigit():
            self.controller.save_new_contact(int(raw_id))
        else:
            messagebox.showerror("Error", "Enter a numeric Channel ID.")

    def on_delete_contact(self):
        selection = self.contact_listbox.curselection()
        if selection:
            self.controller.delete_contact(selection[0])

    def on_add_task(self):
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
        
        self.entry_msg.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)