import discord
import dateparser
import datetime
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 1. Load Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Setup Intents
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True         

# 3. Initialize Bot
# We don't need a command_prefix anymore, but we keep it for legacy support
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

async def send_scheduled_message(user_id, message_content, author_name):
    try:
        user = await bot.fetch_user(user_id)
        if user:
            final_msg = f"**From {author_name}:** {message_content}"
            await user.send(final_msg)
            print(f"Sent message to {user.name}")
    except discord.Forbidden:
        print(f"Could not DM user {user_id}. No mutual server or DMs blocked.")
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # This syncs the / commands with Discord so they appear in the menu
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    scheduler.start()

# 4. The New Slash Command
@bot.tree.command(name="later", description="Schedule a message for later")
@app_commands.describe(destination="Who to send it to", time_str="When? (e.g. 'in 5 mins')", message="The message")
async def later(interaction: discord.Interaction, destination: discord.User, time_str: str, message: str):
    
    # Check if the time is valid
    dt = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})

    if dt is None:
        # 'ephemeral=True' means only YOU see this error message
        await interaction.response.send_message("I couldn't understand that time format.", ephemeral=True)
        return

    if dt < datetime.datetime.now():
        await interaction.response.send_message("That time is in the past!", ephemeral=True)
        return

    # Schedule the job
    scheduler.add_job(
        send_scheduled_message, 
        'date', 
        run_date=dt, 
        args=[destination.id, message, interaction.user.name]
    )

    await interaction.response.send_message(f"✅ Message for **{destination.display_name}** scheduled for {discord.utils.format_dt(dt, 'R')}.", ephemeral=True)

bot.run(TOKEN)