import discord
import threading
import asyncio
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from Task import Task, SavedContact
from Storage import Storage

class TaskController():
    def __init__(self, log_callback, update_tasks_cb, update_contacts_cb):
            # might be useless line
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
            self.scheduler = None

    # Login and keep the bot running in background when app start (bad practice)
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

    def save_new_contact(self, channel_id):
        if not self.loop:
            self.log("Error: Bot not connected yet.")
            return
        asyncio.run_coroutine_threadsafe(self._fetch_and_save(channel_id), self.loop)
    async def _fetch_and_save(self, channel_id):
        try:
            self.log(f"Fetching user {channel_id}...")
            channel = await self.client.fetch_channel(channel_id)
            if not isinstance(channel, discord.DMChannel):
                    self.log("Error: That ID is not a Direct Message channel.")
                    return
            recipient = channel.recipient
            if not recipient:
                self.log("Error: Could not find user in this DM.")
                return
            new_contact = SavedContact(
                channel_id=channel.id,
                username=recipient.name,
            )
            for c in self.saved_contacts:
                if c.channel_id == new_contact.channel_id:
                    self.log(f"Contact {new_contact.username} already saved.")
                    return

            self.saved_contacts.append(new_contact)
            Storage.save_contacts(self.saved_contacts)
            self.update_contacts_gui(self.saved_contacts)
            self.log(f"Saved DM with: {new_contact.username}")


        except discord.NotFound:
            self.log("Channel ID not found.")
        except discord.Forbidden:
            self.log("No access to this channel.")
        except Exception as e:
            self.log(f"Error: {e}")

    def delete_contact(self, index):
        if 0 <= index < len(self.saved_contacts):
            removed = self.saved_contacts.pop(index)
            Storage.save_contacts(self.saved_contacts)
            self.update_contacts_gui(self.saved_contacts)
            self.log(f"Deleted {removed.username}")


    def add_task(self, task: Task):
        self.active_tasks.append(task)
        self.update_tasks_gui(self.active_tasks)

        if self.loop: 
            self.scheduler.add_job(self._execute_task, 'date', 
                                   run_date=task.run_time, args=[task])
            self.log(f"Task Added: {task.run_time.strftime('%H:%M:%S')}")
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
