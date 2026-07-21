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

import json, sys, os
import discord
from discord.ext import commands
from core import Context
from utils.emoji import DENIED
import aiosqlite
import asyncio

async def setup_db():
  async with aiosqlite.connect('db/prefix.db') as db:
    await db.execute('''
      CREATE TABLE IF NOT EXISTS prefixes (
        guild_id INTEGER PRIMARY KEY,
        prefix TEXT NOT NULL
      )
    ''')
    await db.commit()


asyncio.run(setup_db())

async def is_topcheck_enabled(guild_id: int):
    async with aiosqlite.connect('db/topcheck.db') as db:
        async with db.execute("SELECT enabled FROM topcheck WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None and row[0] == 1
            


def read_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"guilds": {}}

def write_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_or_create_guild_config(file_path, guild_id, default_config):
    data = read_json(file_path)
    if "guilds" not in data:
        data["guilds"] = {}  

    guild_id_str = str(guild_id)
    if guild_id_str not in data["guilds"]:
        data["guilds"][guild_id_str] = default_config
        write_json(file_path, data)
    return data["guilds"][guild_id_str]

def update_guild_config(file_path, guild_id, new_data):
    data = read_json(file_path)
    if "guilds" not in data:
        data["guilds"] = {}  

    data["guilds"][str(guild_id)] = new_data
    write_json(file_path, data)

def getIgnore(guild_id):
    default_config = {
        "channel": [],
        "role": None,
        "user": [],
        "bypassrole": None,
        "bypassuser": [],
        "commands": []
    }
    return get_or_create_guild_config("ignore.json", guild_id, default_config)

def updateignore(guild_id, data):
    update_guild_config("ignore.json", guild_id, data)





async def getConfig(guildID):
  async with aiosqlite.connect('db/prefix.db') as db:
    async with db.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (guildID,)) as cursor:
      row = await cursor.fetchone()
      if row:
        return {"prefix": row[0]}
      else:
        defaultConfig = {"prefix": ">"}
        await updateConfig(guildID, defaultConfig)
        return defaultConfig

async def updateConfig(guildID, data):
  async with aiosqlite.connect('db/prefix.db') as db:
    await db.execute(
      "INSERT OR REPLACE INTO prefixes (guild_id, prefix) VALUES (?, ?)",
      (guildID, data["prefix"])
    )
    await db.commit()



def restart_program():
  python = sys.executable
  os.execl(python, python, *sys.argv)


def blacklist_check():

  async def predicate(ctx):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute("SELECT 1 FROM user_blacklist WHERE user_id = ?", (str(ctx.author.id),))
      user_blacklisted = await cursor.fetchone()
      if user_blacklisted:
        return False

      cursor = await db.execute("SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (str(ctx.guild.id),))
      guild_blacklisted = await cursor.fetchone()
      if guild_blacklisted:
        return False

    return True

  return commands.check(predicate)
    

async def get_ignore_data(guild_id: int) -> dict:
    async with aiosqlite.connect("db/ignore.db") as db:
        data = {
            "channel": set(),
            "user": set(),
            "command": set(),
            "bypassuser": set(),
        }

        async with db.execute("SELECT channel_id FROM ignored_channels WHERE guild_id = ?", (guild_id,)) as cursor:
            channels = await cursor.fetchall()
            data["channel"] = {str(channel_id) for (channel_id,) in channels}

        async with db.execute("SELECT user_id FROM ignored_users WHERE guild_id = ?", (guild_id,)) as cursor:
            users = await cursor.fetchall()
            data["user"] = {str(user_id) for (user_id,) in users}

        async with db.execute("SELECT command_name FROM ignored_commands WHERE guild_id = ?", (guild_id,)) as cursor:
            commands = await cursor.fetchall()
            data["command"] = {command_name.strip().lower() for (command_name,) in commands}

        async with db.execute("SELECT user_id FROM bypassed_users WHERE guild_id = ?", (guild_id,)) as cursor:
            bypass_users = await cursor.fetchall()
            data["bypassuser"] = {str(user_id) for (user_id,) in bypass_users}

    return data

def ignore_check():
    async def predicate(ctx):
        data = await get_ignore_data(ctx.guild.id)
        ch = data["channel"]
        iuser = data["user"]
        cmd = data["command"]
        buser = data["bypassuser"]

        if str(ctx.author.id) in buser:
            return True
        if str(ctx.channel.id) in ch or str(ctx.author.id) in iuser:
            return False

        command_name = ctx.command.name.strip().lower()
        aliases = [alias.strip().lower() for alias in ctx.command.aliases]
        if command_name in cmd or any(alias in cmd for alias in aliases):
            return False

        return True

    return commands.check(predicate)

def top_check():
    async def predicate(ctx):
        if not ctx.guild:
            return True

        if getattr(ctx, "invoked_with", None) in ["help", "h"]:
            return True

        topcheck_enabled = await is_topcheck_enabled(ctx.guild.id)

        if not topcheck_enabled:
            return True

        if ctx.author != ctx.guild.owner and ctx.author.top_role.position <= ctx.guild.me.top_role.position:
            embed = discord.Embed(
                title=f"{DENIED} Access Denied", 
                description="Your top role must be at a **higher** position than my top role.",
                color=0x000000
            )
            embed.set_footer(
                text=f"“{ctx.command.qualified_name}” command executed by {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=embed)
            return False

        return True

    return commands.check(predicate)