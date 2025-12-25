import tkinter as tk
from ContactsPanel import ContactsPanel
from SchedulerPanel import SchedulerPanel
from LogsPanel import LogsPanel

from TaskController import TaskController

class AppView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord DM Manager")
        self.geometry("950x500")
        self.configure(bg="#2C2F33")

        # 1. Create Panels first (so we can pass their methods to controller)
        # Note: We can't pass controller to them yet, because controller needs THEM first.
        # So we create panels -> create controller -> assign controller to panels.
        
        self.contacts_panel = ContactsPanel(self, None) 
        self.scheduler_panel = SchedulerPanel(self, None)
        self.logs_panel = LogsPanel(self)

        # 2. Create Controller
        self.controller = TaskController(
            log_callback=self.logs_panel.log,
            update_tasks_cb=self.logs_panel.refresh_queue,
            update_contacts_cb=self.contacts_panel.update_list
        )

        # 3. Link Controller back to panels
        self.contacts_panel.controller = self.controller
        self.scheduler_panel.controller = self.controller

        # 4. Layout
        self.contacts_panel.pack(side="left", fill="y", padx=5, pady=5)
        self.scheduler_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.logs_panel.pack(side="right", fill="y", padx=5, pady=5)

        # 5. Start
        self.controller.start_background()