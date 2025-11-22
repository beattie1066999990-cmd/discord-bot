import discord
from discord.ext import commands
from discord import app_commands
import requests
from math import ceil
import os
print("All environment variables:", os.environ)
TOKEN = os.getenv("TOKEN")
print("Token prefix:", TOKEN[:5])  # just for debugging

INTENTS = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=INTENTS)

OFFSETS_URL = "https://yub-x.com/hyperion"
offset_text = "Offsets not loaded yet."


def fetch_raw_offsets():
    """Downloads the entire offsets.hpp file as raw text."""
    try:
        resp = requests.get(OFFSETS_URL, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"Failed to download offsets:\n{e}"


@bot.event
async def on_ready():
    global offset_text
    offset_text = fetch_raw_offsets()
    print("Offsets fetched.")
    try:
        await bot.tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Sync error:", e)
    print(f"Bot is ready as {bot.user}")


@bot.tree.command(name="offset", description="Paste the latest offsets.hpp file text.")
async def offset(interaction: discord.Interaction):
    global offset_text

    # Short text → send in code block
    if len(offset_text) <= 1900:
        await interaction.response.send_message(f"```\n{offset_text}\n```")
    else:
        # Too long → send as file
        from io import StringIO
        buf = StringIO(offset_text)
        buf.seek(0)
        file = discord.File(buf, filename="offsets.hpp")
        await interaction.response.send_message("Offsets are too long, sending as file:", file=file)


bot.run(TOKEN)



