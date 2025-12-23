import discord
import os
from dotenv import load_dotenv

load_dotenv()
HIDDEN_TOKEN = os.getenv('DISCORD_TOKEN')
DM_ID = os.getenv('DM_CHANNEL_ID') 

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        print(self.cached_messages)
        target = self.get_channel(int(DM_ID))
        print(target.recipient)



    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

client = MyClient()
client.run(HIDDEN_TOKEN)
