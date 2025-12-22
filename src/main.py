import tkinter as tk
from tkinter import messagebox, scrolledtext

import discord
import os
import uuid
from dataclasses import dataclass, field
import asyncio
import threading
import datetime
import dateparser
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Keep your token in .env file. format: DISCORD_TOKEN=your_token_here
load_dotenv()
HIDDEN_TOKEN = os.getenv('DISCORD_TOKEN')
if not HIDDEN_TOKEN:
    print("CRITICAL ERROR: No DISCORD_TOKEN found in .env file.")

client = discord.Client()
scheduler = AsyncIOScheduler()

log_widget = None


@dataclass
class Task:
    """Stores the data for the task."""
    target_id: int
    message: str
    run_time: datetime.datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: str = "Pending"

    def __str__(self):
        time_str = self.run_time.strftime("%H:%M:%S")
        return f"[{time_str}] ID:{self.target_id}  - {self.run_time} - {self.status}"
    


class TaskController():
    def __init__(self, log_callback, update_list_callback):
            self.scheduler = AsyncIOScheduler()
            self.log = log_callback
            self.update_list = update_list_callback
            self.active_tasks = []

            self.loop = None
            self.client = None
            self.scheduler = None

    def start_background(self):
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()
            
    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.client = discord.Client()
        self.scheduler = AsyncIOScheduler(event_loop=self.loop)

        @self.client.event
        async def on_ready():
            self.scheduler.start()
            self.log(f'Logged in as {self.client.user} (User Account)')
            self.log(f"System ready.") 
        
        if HIDDEN_TOKEN:
            self.loop.run_until_complete(self.client.start(HIDDEN_TOKEN))
        else:
            self.log("❌ Error: No Token Found")

    
    def add_task(self, task: Task):
        self.active_tasks.append(task)
        self.update_list(self.active_tasks)

        if self.loop: 
            self.scheduler.add_job(self._execute_task, 'date', run_date=task.run_time, args=[task])
            self.log(f"Task Added: {task.run_time.strftime('%H:%M:%S')}")
        else:
            self.log("Error: Bot not connected yet.")


    async def _execute_task(self, task: Task):
        task.status = "Running"
        self.update_list(self.active_tasks)

        try:
            self.log(f"Executing task {task.id}...")

            # Find
            target = self.client.get_channel(task.target_id)
            if not target:
                try:
                    target = await self.client.fetch_user(task.target_id)
                except:
                    target = await self.client.fetch_channel(task.target_id)
            # Send 
            if target:
                await target.send(task.message)
                self.log(f"Message sent to {task.target_id}")
                task.status = "Completed"
            else: 
                self.log(f"Could not find target ID: {task.target_id}")
                task.status = "Failed"
        except Exception as e:
            self.log(f"Error executing task {task.id}: {e}")
            task.status = "Error"

        self.update_list(self.active_tasks)



class AppView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord Auto-Sender")
        self.geometry("700x450")
        self.configure(bg="#2C2F33") # Discord Grey

        self.controller = TaskController(log_callback = self.log_msg,
        update_list_callback = self.refresh_task_list)

        self._build_ui()
        self.controller.start_background()
    
    def _build_ui(self):
        # Inputs
        frame_input = tk.Frame(self, bg="#2C2F33")
        frame_input.pack(side="left", fill="y", padx=20, pady=20)

        def make_field(label, parent):
            tk.Label(parent, text = label, bg="#2C2F33", fg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,0))
            entry = tk.Entry(parent, bg="#99AAB5", width = 25)
            entry.pack(pady=5)
            return entry
        
        self.entry_id = make_field("Target ID:", frame_input)
        self.entry_time = make_field("Time:", frame_input)
        self.entry_msg = make_field("Message:", frame_input)

        tk.Button(frame_input, text="ADD TASK", bg="#7289DA", fg="white", font=("Arial", 10, "bold"), 
                  command=self.on_add_task).pack(pady=20, fill="x")
        
        # Display
        frame_display = tk.Frame(self, bg="#2C2F33")
        frame_display.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # List of Tasks
        tk.Label(frame_display, text="Task Queue:", bg="#2C2F33", fg="white").pack(anchor="w")
        self.task_listbox = tk.Listbox(frame_display, height=10, bg="#23272A", fg="white", font=("Consolas", 9))
        self.task_listbox.pack(fill="x", pady=(0, 10))

        # System Log
        tk.Label(frame_display, text="System Log:", bg="#2C2F33", fg="white").pack(anchor="w")
        self.log_box = tk.Text(frame_display, height=8, bg="#23272A", fg="#00FF00", font=("Consolas", 8))
        self.log_box.pack(fill="both", expand=True)

    def log_msg(self, text):
            """Updates the log box."""
            self.log_box.insert(tk.END, text + "\n")
            self.log_box.see(tk.END)

    def refresh_task_list(self, tasks):
        """Redraws the task list from scratch based on current data."""
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            self.task_listbox.insert(tk.END, str(task))

    def on_add_task(self):
        # 1. Get Inputs
        t_id = self.entry_id.get().strip()
        t_time = self.entry_time.get().strip()
        t_msg = self.entry_msg.get().strip()

        if not t_id or not t_time or not t_msg:
            messagebox.showerror("Error", "Missing fields")
            return

        # 2. Parse Time
        dt = dateparser.parse(t_time, settings={'PREFER_DATES_FROM': 'future'})
        if not dt or dt < datetime.datetime.now():
            messagebox.showerror("Error", "Invalid Time")
            return

        # 3. Create the Task Object
        new_task = Task(target_id=int(t_id), message=t_msg, run_time=dt)

        # 4. Pass to Controller
        self.controller.add_task(new_task)
        
        # Clear specific inputs (keep ID in case you want to send another to same person)
        self.entry_msg.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)

if __name__ == "__main__":
    if not HIDDEN_TOKEN:
        messagebox.showerror("Error", "No Token in .env file")
    app = AppView()
    app.mainloop()