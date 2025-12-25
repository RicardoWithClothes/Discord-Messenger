import discord
import threading
import asyncio
import os
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from Task import Task, SavedContact
from Storage import Storage

class TaskController():
    def __init__(self, log_callback, update_tasks_cb, update_contacts_cb):
        self.scheduler = AsyncIOScheduler()
        self.log = log_callback

        self.update_tasks_gui = update_tasks_cb
        self.update_contacts_gui = update_contacts_cb
        
        self.active_tasks = []
        self.saved_contacts = Storage.load_contacts()

        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.loop = None
        self.client = None


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
            self.log(f'Logged in as {self.client.user}')
            self.log(f"System ready.")
            self.update_contacts_gui(self.saved_contacts) 

        if self.token:
            self.loop.run_until_complete(self.client.start(self.token))
        else:
            self.log("Error: No Token Found")


    def save_new_contact(self, channel_id, qt_start=None, qt_end=None):
        if not self.loop:
            self.log("Error: Bot not connected yet.")
            return
        asyncio.run_coroutine_threadsafe(self._fetch_and_save(channel_id, qt_start, qt_end), self.loop)


    def _apply_quiet_time(self, task: Task):
        for c in self.saved_contacts:
            if c.channel_id == task.channel_id:
                contact = c
                break
        if not contact or not contact.qt_start or not contact.qt_end: 
            return task
        
        target_dt = task.run_time

        qt_start_dt = datetime.datetime.strptime(contact.qt_start, "%H:%M").time()
        qt_end_dt = datetime.datetime.strptime(contact.qt_end, "%H:%M").time()
        check_time = target_dt.time()
        in_qt = False

        if qt_start_dt < qt_end_dt:
            in_qt = qt_start_dt <= check_time <= qt_end_dt
        else:
            in_qt = check_time >= qt_start_dt or check_time <= qt_end_dt

        if in_qt:
            new_time = target_dt.replace(hour=qt_end_dt.hour, minute=qt_end_dt.minute, second=0)
            if new_time < target_dt:
                new_time += datetime.timedelta(days=1)
            task.run_time = new_time
            self.log(f"Rescheduled to {task.run_time.strftime('%H:%M:%S')}")
        return task
    

    async def _fetch_and_save(self, channel_id, qt_start, qt_end):
        try:
            self.log(f"Fetching user {channel_id}...")
            channel = await self.client.fetch_channel(channel_id)
            if not isinstance(channel, discord.DMChannel):
                    self.log("Error: That ID is not a Direct Message channel.")
                    return
            recipient = channel.recipient
            if not recipient:
                self.log("Error: No User found.")
                return

            new_contact = SavedContact(
                channel_id=channel.id,
                username=recipient.name,
                qt_start=qt_start,
                qt_end=qt_end,
            )
            self.saved_contacts = [c for c in self.saved_contacts if c.channel_id != new_contact.channel_id] 

            self.saved_contacts.append(new_contact)
            Storage.save_contacts(self.saved_contacts)
            self.update_contacts_gui(self.saved_contacts)
            self.log(f"Updated {new_contact.username} (QT: {qt_start}-{qt_end})")

        except Exception as e:
            self.log(f"Error: {e}")

    def delete_contact(self, index):
        if 0 <= index < len(self.saved_contacts):
            removed = self.saved_contacts.pop(index)
            Storage.save_contacts(self.saved_contacts)
            self.update_contacts_gui(self.saved_contacts)
            self.log(f"Deleted {removed.username}")


    def add_task(self, task: Task):
        final_task = self._apply_quiet_time(task)
        
        self.active_tasks.append(final_task)
        self.update_tasks_gui(self.active_tasks)

        if self.loop: 
            self.scheduler.add_job(
                self._execute_task, 
                'date', 
                run_date=final_task.run_time, 
                args=[final_task]
            )
            self.log(f"Task Added: {final_task.run_time.strftime('%H:%M:%S')}")
        else:
            self.log("Error: Bot not connected yet.")


    async def _execute_task(self, task: Task):
        task.status = "Running"
        self.update_tasks_gui(self.active_tasks)

        try:
            self.log(f"Executing task {task.id}...")

            # Find the DM channel
            target = self.client.get_channel(task.channel_id)
            if not target:
                target = await self.client.fetch_channel(task.channel_id)
            # Send 
            if target:
                await target.send(task.message)
                name = target.recipient.name if isinstance(target, discord.DMChannel) and target.recipient else "Unknown"
                self.log(f"Message sent to {name} at {task.run_time.strftime('%H:%M:%S')}")
                task.status = "Completed"

        except Exception as e:
            self.log(f"Error: {e}")
            task.status = "Error"

        self.update_tasks_gui(self.active_tasks)
