import tkinter as tk
from tkinter import messagebox

from Task import Task


class ContactsPanel(tk.Frame):
    def __init__(self, parent, controller):
        # Initialize Frame with specific styling
        super().__init__(parent, bg="#23272A", width=250)
        self.pack_propagate(False) # Force fixed width
        self.controller = controller
        self.parent = parent # Reference to AppView to talk to other panels
        
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="SAVED DMs", bg="#23272A", fg="#7289DA", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Listbox
        self.listbox = tk.Listbox(self, bg="#2C2F33", fg="white", bd=0, highlightthickness=0)
        self.listbox.pack(fill="both", expand=True, padx=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Quiet Time Inputs
        frame_qt = tk.Frame(self, bg="#23272A")
        frame_qt.pack(fill="x", pady=5, padx=5)
        
        tk.Label(frame_qt, text="Quiet Time (HH:MM)", bg="#23272A", fg="gray", font=("Arial", 8)).pack(anchor="w")
        
        f_times = tk.Frame(frame_qt, bg="#23272A")
        f_times.pack(fill="x")
        
        self.qt_start = tk.Entry(f_times, bg="#40444B", fg="white", width=6, bd=0)
        self.qt_start.pack(side="left", padx=(0,5))
        self.qt_start.insert(0, "22:00")
        
        tk.Label(f_times, text="to", bg="#23272A", fg="gray").pack(side="left")
        
        self.qt_end = tk.Entry(f_times, bg="#40444B", fg="white", width=6, bd=0)
        self.qt_end.pack(side="left", padx=5)
        self.qt_end.insert(0, "08:00")

        # Buttons
        frame_btns = tk.Frame(self, bg="#23272A")
        frame_btns.pack(fill="x", pady=10)
        
        tk.Button(frame_btns, text="Save ID", bg="#43B581", fg="white", bd=0, 
                  command=self.on_save).pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(frame_btns, text="Delete", bg="#F04747", fg="white", bd=0,
                  command=self.on_delete).pack(side="right", padx=5, expand=True, fill="x")

    def update_list(self, contacts):
        self.listbox.delete(0, tk.END)
        for i, c in enumerate(contacts):
            self.listbox.insert(tk.END, str(c))
            # Zebra Striping
            bg_color = "#2C2F33" if i % 2 == 0 else "#202225"
            self.listbox.itemconfigure(i, bg=bg_color)

    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            contact = self.controller.saved_contacts[index]
            
            # 1. Update QT boxes
            self.qt_start.delete(0, tk.END)
            self.qt_end.delete(0, tk.END)
            if contact.qt_start: self.qt_start.insert(0, contact.qt_start)
            if contact.qt_end: self.qt_end.insert(0, contact.qt_end)

            # 2. Tell the Middle Panel to fill the ID
            # We access the middle panel via the parent (AppView)
            self.parent.scheduler_panel.set_target_id(contact.channel_id)

    def on_save(self):
        # Retrieve ID from the Middle Panel
        raw_id = self.parent.scheduler_panel.get_target_id()
        q_start = self.qt_start.get().strip()
        q_end = self.qt_end.get().strip()

        if raw_id.isdigit():
            self.controller.save_new_contact(int(raw_id), q_start, q_end)
        else:
            messagebox.showerror("Error", "Enter a numeric Channel ID in the middle panel first.")

    def on_delete(self):
        selection = self.listbox.curselection()
        if selection:
            self.controller.delete_contact(selection[0])