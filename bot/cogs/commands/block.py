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
from utils.emoji import CROSS, TICK
from discord.ext import commands
import aiosqlite
from utils import Paginator, DescriptionEmbedPaginator
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.cv2 import CV2, build_container

class CV2(LayoutView):
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        items = [TextDisplay(f"**{title}**")]
        for s in sections:
            if s:
                items.append(Separator(visible=True))
                items.append(TextDisplay(str(s)))
        self.add_item(build_container(*items))

class Block(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.loop.create_task(self.set_db())

  #@commands.Cog.listener()
  async def set_db(self):
    async with aiosqlite.connect('db/block.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_blacklist (
                user_id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guild_blacklist (
                guild_id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
      


  @commands.group(name="blacklist", aliases=["bl"], invoke_without_command=True)
  @commands.is_owner()
  async def blacklist(self, ctx):
    if ctx.subcommand_passed is None:
      ctx.command.reset_cooldown(ctx)
      await ctx.send_help(ctx.command)

  @blacklist.group(name="user", help="Add/Remove a user to the blacklist.", invoke_without_command=True)
  @commands.is_owner()
  async def user(self, ctx):
    if ctx.subcommand_passed is None:
      ctx.command.reset_cooldown(ctx)
      await ctx.send_help(ctx.command)

  @user.command(name="add", help="Adds a user to the blacklist.")
  @commands.is_owner()
  async def add_user(self, ctx, user: discord.User):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute('SELECT user_id FROM user_blacklist WHERE user_id = ?', (user.id,))
      if await cursor.fetchone():
        await ctx.reply(view=CV2("User Already Blacklisted", f"{user.mention} is already blacklisted."))
      else:
        await db.execute('INSERT INTO user_blacklist (user_id) VALUES (?)', (user.id,))
        await db.commit()
        await ctx.reply(view=CV2(f"{TICK} User Blacklisted", f"{user.mention} has been added to the blacklist."))

  @user.command(name="remove", help="Remove a user from the blacklist.")
  @commands.is_owner()
  async def remove_user(self, ctx, user: discord.User):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute('SELECT user_id FROM user_blacklist WHERE user_id = ?', (user.id,))
      if not await cursor.fetchone():
        await ctx.reply(view=CV2(f"{CROSS} User Not Blacklisted", f"{user.mention} is not in the blacklist."))
      else:
        await db.execute('DELETE FROM user_blacklist WHERE user_id = ?', (user.id,))
        await db.commit()
        await ctx.reply(view=CV2(f"{TICK} User Unblacklisted", f"{user.mention} has been removed from the blacklist."))

  @user.command(name="show", aliases=["list"], help="Shows all Blacklisted users.")
  @commands.is_owner()
  async def show_users(self, ctx):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute('SELECT user_id FROM user_blacklist')
      rows = await cursor.fetchall()
      if not rows:
        await ctx.reply(view=CV2(f"{CROSS} No Blacklisted Users", "There are no users in the blacklist."))
        return

      blacklist = []
      for row in rows:
        user_id = row[0]
        try:
          user = await self.bot.fetch_user(user_id)
          username = user.name
          user_link = f"https://discord.com/users/{user_id}"
          #indexx = [""for index, user in enumerate(blacklist)]

          blacklist.append(f"**[{username}]({user_link})** - ({user_id})")
        except discord.NotFound:
          blacklist.append(f"User ID: {user_id} (User not found)")
      entries = [f"{index+1}. {user}" for index, user in enumerate(blacklist)]
      paginator = Paginator(source=DescriptionEmbedPaginator(
        entries=entries,
        title=f"List of Blacklisted Users - {len(blacklist)}",
        description="",
        per_page=10,
        color=0xFF0000),
        ctx=ctx
      )
      await paginator.paginate()

  @blacklist.group(name="guild", help="Add/Remove a guild to the blacklist.", invoke_without_command=True)
  @commands.is_owner()
  async def guild(self, ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @guild.command(name="add", help="Adds a guild to the blacklist.")
  @commands.is_owner()
  async def add_guild(self, ctx, guild_id: int):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute('SELECT guild_id FROM guild_blacklist WHERE guild_id = ?', (guild_id,))
      if await cursor.fetchone():
        await ctx.reply(view=CV2(f"{CROSS} Guild Already Blacklisted", f"Guild with ID `{guild_id}` is already blacklisted."))
      else:
        await db.execute('INSERT INTO guild_blacklist (guild_id) VALUES (?)', (guild_id,))
        await db.commit()
        await ctx.reply(view=CV2(f"{TICK} Guild Blacklisted", f"Guild with ID `{guild_id}` has been added to the blacklist."))

  @guild.command(name="remove", help="Remove a guild from the blacklist.")
  @commands.is_owner()
  async def remove_guild(self, ctx, guild_id: int):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute('SELECT guild_id FROM guild_blacklist WHERE guild_id = ?', (guild_id,))
      if not await cursor.fetchone():
        await ctx.reply(view=CV2(f"{CROSS} Guild Not Blacklisted", f"Guild with ID `{guild_id}` is not in the blacklist."))
      else:
        await db.execute('DELETE FROM guild_blacklist WHERE guild_id = ?', (guild_id,))
        await db.commit()
        await ctx.reply(view=CV2(f"{TICK} Guild Unblacklisted", f"Guild with ID `{guild_id}` has been removed from the blacklist."))
        

  @guild.command(name="show", aliases=["list"], help="Shows the list of blacklisted guilds")
  @commands.is_owner()
  async def show_guilds(self, ctx):
    async with aiosqlite.connect('db/block.db') as db:
      cursor = await db.execute('SELECT guild_id FROM guild_blacklist')
      rows = await cursor.fetchall()
      if not rows:
        await ctx.reply(view=CV2(f"{CROSS} No Blacklisted Guilds", "There are no guilds in the blacklist."))
        return

      blacklist = []
      for row in rows:
        guild_id = row[0]
        try:
          guild = await self.bot.fetch_guild(guild_id)
          guild_name = guild.name
          guild_link = f"https://discord.com/guilds/{guild_id}"
          blacklist.append(f"[{guild_name}]({guild_link}) - ({guild_id})")
        except discord.NotFound:
          blacklist.append(f"Guild ID: {guild_id} (Guild not found)")
      entries = [f"{index+1}. {guild}" for index, guild in enumerate(blacklist)]
      paginator = Paginator(source=DescriptionEmbedPaginator(
        entries=entries,
        title=f"List of Blacklisted Guilds - {len(blacklist)}",
        description="",
        per_page=10,
        color=0xFF0000),
        ctx=ctx
      )
      await paginator.paginate()


 