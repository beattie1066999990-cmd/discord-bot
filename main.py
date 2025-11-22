import discord
from discord.ext import commands
from discord import app_commands
import requests
import re
from io import StringIO
import os

TOKEN = os.getenv "TOKEN"
INTENTS = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=INTENTS)

OFFSETS_URL = "https://offsets.ntgetwritewatch.workers.dev/offsets.hpp"
OFFSET_RE = re.compile(r"inline constexpr uintptr_t\s+(\w+)\s*=\s*(0x[0-9A-Fa-f]+)")

async def fetch_offsets():
    """Fetch offsets and return a dictionary."""
    try:
        resp = requests.get(OFFSETS_URL, timeout=10)
        resp.raise_for_status()
        found = OFFSET_RE.findall(resp.text)
        return {name: value for name, value in found}
    except Exception as e:
        print("Error fetching offsets:", e)
        return {}

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Error syncing commands:", e)
    print("Bot is ready!")

@bot.tree.command(name="offset", description="Fetch and show current offsets.")
async def offset(interaction: discord.Interaction):
    await interaction.response.defer()  # avoid timeout
    offsets = await fetch_offsets()
    
    if not offsets:
        await interaction.followup.send("Could not fetch offsets.")
        return
    
    # Prepare the message
    msg = "\n".join(f"**{name}** = `{value}`" for name, value in offsets.items())

    # If too long, send as a file
    if len(msg) > 1900:
        buf = StringIO(msg)
        buf.seek(0)
        file = discord.File(fp=buf, filename="offsets.txt")
        await interaction.followup.send("Offsets are too long, sending as file:", file=file)
    else:
        await interaction.followup.send(msg)

bot.run(TOKEN)

