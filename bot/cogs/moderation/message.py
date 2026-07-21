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

import discord
from utils.emoji import TICK
from discord.ext import commands, tasks
import asyncio
import datetime
import re
from typing import *
from utils.Tools import *
from discord.ui import Button, View
from typing import Union, Optional
from typing import Union, Optional
from io import BytesIO
import requests
import aiohttp
import time
from datetime import datetime, timezone, timedelta


time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def convert(argument):
  args = argument.lower()
  matches = re.findall(time_regex, args)
  time = 0
  for key, value in matches:
    try:
      time += time_dict[value] * float(key)
    except KeyError:
      raise commands.BadArgument(
        f"{value} is an invalid time key! h|m|s|d are valid arguments")
    except ValueError:
      raise commands.BadArgument(f"{key} is not a number!")
  return round(time)

async def do_removal(ctx, limit, predicate, *, before=None, after=None):
  if limit > 2000:
      return await ctx.error(f"Too many messages to search given ({limit}/2000)")

  if before is None:
      before = ctx.message
  else:
      before = discord.Object(id=before)

  if after is not None:
      after = discord.Object(id=after)

  try:
      deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
  except discord.Forbidden as e:
      return await ctx.error("I do not have permissions to delete messages.")
  except discord.HTTPException as e:
      return await ctx.error(f"Error: {e} (try a smaller search?)")

  spammers = Counter(m.author.display_name for m in deleted)
  deleted = len(deleted)
  messages = [f'{TICK} | {deleted} message{" was" if deleted == 1 else "s were"} removed.']
  if deleted:
      messages.append("")
      spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
      messages.extend(f"**{name}**: {count}" for name, count in spammers)

  to_send = "\n".join(messages)

  if len(to_send) > 2000:
      await ctx.send(f"{TICK} | Successfully removed {deleted} messages.", delete_after=7)
  else:
      await ctx.send(to_send, delete_after=7)
    

class Message(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.color = 0xFF0000


  @commands.group(invoke_without_command=True, aliases=["purge"], help="Clears the messages")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def clear(self, ctx, Choice: Union[discord.Member, int], Amount: int = None):
        await ctx.message.delete()

        if isinstance(Choice, discord.Member):
            search = Amount or 5
            return await do_removal(ctx, search, lambda e: e.author == Choice)

        elif isinstance(Choice, int):
            return await do_removal(ctx, Choice, lambda e: True)



  @clear.command(help="Clears the messages having embeds")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def embeds(self, ctx, search=100):
        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: len(e.embeds))


  @clear.command(help="Clears the messages having files")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def files(self, ctx, search=100):

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: len(e.attachments))

  @clear.command(help="Clears the messages having images")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def images(self, ctx, search=100):

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))


  @clear.command(name="all", help="Clears all messages")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def _remove_all(self, ctx, search=100):

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: True)

  @clear.command(help="Clears the messages of a specific user")
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def user(self, ctx, member: discord.Member, search=100):

        await ctx.message.delete()
        await do_removal(ctx, search, lambda e: e.author == member)



  @clear.command(help="Clears the messages containing a specifix string")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def contains(self, ctx, *, string: str):

        await ctx.message.delete()
        if len(string) < 3:
            await ctx.error("The substring length must be at least 3 characters.")
        else:
            await do_removal(ctx, 100, lambda e: string in e.content)

  @clear.command(name="bot", aliases=["bots","b"], help="Clears the messages sent by bot")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def _bot(self, ctx, prefix=None, search=100):

        await ctx.message.delete()

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await do_removal(ctx, search, predicate)

  @clear.command(name="emoji", aliases=["emojis"], help="Clears the messages having emojis")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)

  async def _emoji(self, ctx, search=100):

        await ctx.message.delete()
        custom_emoji = re.compile(r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>")

        def predicate(m):
            return custom_emoji.search(m.content)

        await do_removal(ctx, search, predicate)

  @clear.command(name="reactions", help="Clears the reaction from the messages")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def _reactions(self, ctx, search=100):

        await ctx.message.delete()

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.success(f"{TICK} | Successfully removed {total_reactions} reactions.")
            



  @commands.command(name="purgebots",
                    aliases=["cleanup", "pb", "clearbot", "clearbots"],
                    help="Clear recently bot messages in channel")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def _purgebot(self, ctx, prefix=None, search=100):

    await ctx.message.delete()

    def predicate(m):
        return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))
      
    await do_removal(ctx, search, predicate)


  @commands.command(name="purgeuser",
                    aliases=["pu", "cu", "clearuser"],
                    help="Clear recent messages of a user in channel")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def purguser(self, ctx, member: discord.Member, search=100):
      
      await ctx.message.delete()
      await do_removal(ctx, search, lambda e: e.author == member)

 