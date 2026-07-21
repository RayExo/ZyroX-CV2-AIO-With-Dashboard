# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
import subprocess
# os.system("")
import asyncio
import traceback
from threading import Thread
from datetime import datetime
import random
import time

import aiohttp
import discord
from discord import Spotify
from discord.ext import commands, tasks

from core import Context
from core.Cog import Cog
from core.zyrox import zyrox
from utils.Tools import *
from utils.config import *
from utils.emoji import SUCCESS, ERROR, TICK, CROSS, REACTION_TEST_EMOJIS
from utils.sync_emojis import run_sync

import cogs

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

if JISHAKU_ENABLED:
    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
    os.environ["JISHAKU_HIDE"] = "True"
    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

if not OWNER_IDS:
    print("\033[33m⚠ OWNER_IDS is not set in .env — no bot owners configured.\033[0m")
    print("\033[33m  Set OWNER_IDS=YOUR_DISCORD_USER_ID before running in production.\033[0m")

client = zyrox()
tree = client.tree

# --- Background Task for Stats ---
async def update_stats():
    """Update server/user counts in channel names when channel IDs are configured."""
    if not SERVER_COUNT_CHANNEL_ID and not USER_COUNT_CHANNEL_ID:
        return
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            servers = len(client.guilds)
            users = sum(guild.member_count for guild in client.guilds if guild.member_count is not None)

            if SERVER_COUNT_CHANNEL_ID:
                server_channel = client.get_channel(SERVER_COUNT_CHANNEL_ID)
                if server_channel:
                    await server_channel.edit(name=f"Servers: {servers}")

            if USER_COUNT_CHANNEL_ID:
                user_channel = client.get_channel(USER_COUNT_CHANNEL_ID)
                if user_channel:
                    await user_channel.edit(name=f"Users: {users}")

        except Exception as e:
            print(f"Error updating stats: {e}")

        await asyncio.sleep(600)

# --- Event Handlers ---
@client.event
async def on_ready():
    await client.wait_until_ready()
    
    print("""
        \033[1;31m
 ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗██╔╝
██║     ██║   ██║██║  ██║█████╗   ╚███╔╝ 
██║     ██║   ██║██║  ██║██╔══╝   ██╔██╗ 
╚██████╗╚██████╔╝██████╔╝███████╗██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
        \033[0m
       """)
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")

    # Sync application emojis on startup
    await run_sync(TOKEN)

    async def sync_commands():
        try:
            synced = await client.tree.sync()
            all_commands = list(client.commands)
            print(f"Synced Total {len(all_commands)} Client Commands and {len(synced)} Slash Commands")
        except Exception as e:
            print(f"Error syncing command tree: {e}")

    client.loop.create_task(sync_commands())
    if SERVER_COUNT_CHANNEL_ID or USER_COUNT_CHANNEL_ID:
        client.loop.create_task(update_stats())


@client.event
async def on_guild_join(guild: discord.Guild):
    if not LOG_CHANNEL_ID:
        return
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"{BRAND_NAME} has been added to the server: **{guild.name}** (ID: `{guild.id}`)")

@client.event
async def on_command_completion(context: commands.Context) -> None:
    if not CMD_WEBHOOK_URL or context.command is None or context.author.id in OWNER_IDS:
        return

    full_command_name = context.command.qualified_name
    split = full_command_name.split("\n")
    executed_command = str(split[0])

    embed_color = 0xFF0000
    embed = discord.Embed(color=embed_color)
    avatar_url = context.author.display_avatar.url

    embed.set_author(name=f"Cmd Executed: {executed_command}", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)

    if context.guild is not None:
        embed.add_field(name="User", value=f"{context.author.mention} (`{context.author.id}`)", inline=False)
        embed.add_field(name="Server", value=f"{context.guild.name} (`{context.guild.id}`)", inline=False)
        embed.add_field(name="Channel", value=f"{context.channel.mention} (`{context.channel.id}`)", inline=False)
    else:
        embed.add_field(name="User (DM)", value=f"{context.author.mention} (`{context.author.id}`)", inline=False)

    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text=f"{BRAND_NAME} Development™ ❤️", icon_url=client.user.display_avatar.url)

    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(CMD_WEBHOOK_URL, session=session)
            await webhook.send(embed=embed)
    except Exception as e:
        print(f'Command log webhook failed: {e}')


# --- Utility Commands ---
@client.command(name='spotify')
async def spotify(ctx: Context, user: discord.Member = None):
    """Shows what a user is listening to on Spotify."""
    user = user or ctx.author
    spotify_activity = next((activity for activity in user.activities if isinstance(activity, Spotify)), None)

    if not spotify_activity:
        return await ctx.send(f"{user.name} is not listening to Spotify.")
    
    embed = discord.Embed(
        title=f"{user.name}'s Spotify",
        description=f"**Listening to:** {spotify_activity.title}",
        color=0x1DB954 # Spotify Green
    )
    embed.set_thumbnail(url=spotify_activity.album_cover_url)
    embed.add_field(name="Artist", value=spotify_activity.artist)
    embed.add_field(name="Album", value=spotify_activity.album)
    embed.set_footer(text=f"Song started at {spotify_activity.created_at.strftime('%H:%M')}")
    await ctx.send(embed=embed)


@client.command(name='makeinvite', aliases=['createinvite', 'makeinv'])
@commands.is_owner()
async def make_invite(ctx: Context, guild_id: int = None):
    """Creates an invite for a specified server (owner only)."""
    if guild_id is None:
        return await ctx.send("Please provide a Guild ID.")
        
    guild = client.get_guild(guild_id)
    if not guild:
        return await ctx.send("Invalid Guild ID. I am not in that server.")

    if guild.system_channel and guild.system_channel.permissions_for(guild.me).create_instant_invite:
        try:
            invite = await guild.system_channel.create_invite(max_age=0, max_uses=0, unique=True, reason="Owner requested invite.")
            return await ctx.send(f"Invite for **{guild.name}**:\n{invite.url}")
        except Exception:
            pass

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).create_instant_invite:
            try:
                invite = await channel.create_invite(max_age=0, max_uses=0, unique=True, reason="Owner requested invite.")
                return await ctx.send(f"Invite for **{guild.name}** (from #{channel.name}):\n{invite.url}")
            except Exception:
                continue
                
    await ctx.send(f"I don't have 'Create Instant Invite' permission in any channel in **{guild.name}**.")


# --- Webhook Management Commands ---
@client.command(name='create_hook', aliases=['makehook'])
@commands.has_permissions(administrator=True)
async def create_hook(ctx: Context, *, name: str = None):
    """Creates a webhook in the current channel."""
    if name is None:
        return await ctx.send("Please provide a name for the webhook.")
    
    try:
        webhook = await ctx.channel.create_webhook(name=name, reason=f"Created by {ctx.author}")
        embed = discord.Embed(
            title=f"{SUCCESS} Webhook Created",
            description=f"A webhook named **{webhook.name}** was created.",
            color=0xFF0000
        )
        await ctx.author.send(f"Webhook URL for **{webhook.name}** in **{ctx.channel.name}**:\n||{webhook.url}||", embed=embed)
        await ctx.send("Webhook created. I've sent the URL to your DMs.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to create webhooks here.")
    except Exception:
        await ctx.send(f"Webhook created: **{webhook.name}**\n||{webhook.url}||\n(I could not DM you the URL.)")


@client.command(name='delete_hook', aliases=['delhook'])
@commands.has_permissions(administrator=True)
async def delete_hook(ctx: Context, webhook_url: str = None):
    """Deletes a webhook using its URL."""
    if webhook_url is None:
        return await ctx.send("Please provide the webhook URL to delete.")

    try:
        async with aiohttp.ClientSession() as session:
            webhook = await discord.Webhook.from_url(webhook_url, session=session)
            await webhook.delete(reason=f"Deleted by {ctx.author}")
        await ctx.send(f"{SUCCESS} Webhook deleted successfully.")
    except (discord.NotFound, ValueError):
        await ctx.send(f"{ERROR} Webhook not found or URL is invalid.")


@client.command(name='list_hooks', aliases=['hooks'])
@commands.has_permissions(administrator=True)
async def list_hooks(ctx: Context):
    """Lists all webhooks in the current channel."""
    try:
        webhooks = await ctx.channel.webhooks()
        if not webhooks:
            return await ctx.send("No webhooks found in this channel.")

        embed = discord.Embed(title=f"Webhooks in #{ctx.channel.name}", color=0xFF0000)
        description = "\n".join([f"**Name:** {wh.name} | **ID:** `{wh.id}`" for wh in webhooks])
        embed.description = description
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have permission to view webhooks in this channel.")


# --- Game Command ---
@client.command()
async def reaction(ctx: Context):
    """See how fast you can react to the correct emoji."""
    emojis = ["🍪", "🎉", "🧋", "🍒", "🍑", "💸", "🌙", "💕"]
    correct_emoji = random.choice(emojis)
    random.shuffle(emojis)
    
    embed = discord.Embed(
        title="Reaction Test",
        description="I will show an emoji in a few seconds. Get ready to click it!",
        color=0xFF0000
    )
    message = await ctx.send(embed=embed)
    
    for emoji in emojis:
        await message.add_reaction(emoji)
        
    await asyncio.sleep(random.uniform(2.0, 7.0))
    
    embed.description = f"**GET THE {correct_emoji} EMOJI!**"
    await message.edit(embed=embed)
    start_time = time.time()

    def check(reaction, user):
        return (
            reaction.message.id == message.id
            and str(reaction.emoji) == correct_emoji
            and user == ctx.author
        )

    try:
        reaction, user = await client.wait_for("reaction_add", timeout=15.0, check=check)
        end_time = time.time()
        reaction_time = end_time - start_time
        
        embed.description = f"{user.mention} got the {correct_emoji} in **{reaction_time:.2f} seconds**!"
        await message.edit(embed=embed)
    except asyncio.TimeoutError:
        embed.description = "Timeout! You were too slow."
        await message.edit(embed=embed)


# ---API Server for Dashboard Backend ---
import uvicorn
from threading import Thread
from api.server import create_app
from api.dependencies import set_bot

fastapi_app = create_app()
fastapi_app.state.bot = client
set_bot(client)

def run_api():
    uvicorn.run(fastapi_app, host=API_HOST, port=API_PORT, log_level="warning")

def keep_alive():
    if not API_ENABLED:
        print(f"\033[33m◈ API Server: Disabled via API_ENABLED=false\033[0m")
        return
    print(f"\033[32m◈ API Server: Starting on {API_HOST}:{API_PORT}\033[0m")
    if API_HOST in ("0.0.0.0", "::"):
        print("\033[33m  ⚠ API bound to all interfaces — use API_HOST=127.0.0.1 unless behind a reverse proxy.\033[0m")
    server = Thread(target=run_api, daemon=True)
    server.start()

keep_alive()

# --- Cloudflare Tunnel (HTTPS for API) — only when explicitly enabled ---
from utils.tunnel import start_tunnel
start_tunnel()

# --- Main Bot Execution ---
async def main():
    async with client:
        os.system("clear")
        if JISHAKU_ENABLED:
            await client.load_extension("jishaku")
            print("\033[33m◈ Jishaku: enabled (owner-only debug REPL)\033[0m")
        else:
            print("\033[32m◈ Jishaku: disabled (set JISHAKU_ENABLED=true to enable)\033[0m")
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                await client.start(TOKEN)
                break
            except discord.HTTPException as e:
                if e.status == 429: # Rate limited
                    wait_time = min((2 ** attempt) + random.random(), 60)
                    print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        else:
            raise Exception("Bot failed to start after multiple retries due to rate limiting.")

if __name__ == "__main__":
    asyncio.run(main())
