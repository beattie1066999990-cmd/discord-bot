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

OFFSETS_URL = "https://offsets.ntgetwritewatch.workers.dev/offsets.hpp"
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

    # If short enough, send in code block
    if len(offset_text) <= 1900:
        await interaction.response.send_message(f"```\n{offset_text}\n```")
        return

    # Split into pages of 1900 characters
    pages = [offset_text[i:i+1900] for i in range(0, len(offset_text), 1900)]
    total_pages = len(pages)

    # Send first page in an embed
    embed = discord.Embed(title="Offsets.hpp", description=f"Page 1/{total_pages}", color=0x00ff00)
    embed.add_field(name="Offsets", value=f"```\n{pages[0]}\n```", inline=False)
    message = await interaction.response.send_message(embed=embed)

    # If too long, send remaining pages as files
    if total_pages > 1:
        from io import StringIO
        for i, page in enumerate(pages[1:], start=2):
            buf = StringIO(page)
            buf.seek(0)
            file = discord.File(buf, filename=f"offsets_page_{i}.txt")
            await interaction.followup.send(f"Page {i}/{total_pages}:", file=file)


bot.run(TOKEN)

