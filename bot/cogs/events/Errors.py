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
import json
import aiosqlite
from discord.ext import commands
from utils.config import serverLink
from core import zyrox, Cog, Context
from utils.Tools import get_ignore_data

class Errors(Cog):
  def __init__(self, client: zyrox):
    self.client = client

  @commands.Cog.listener()
  async def on_command_error(self, ctx: Context, error):
    if ctx.command is None:
      return
    

    if isinstance(error, commands.CommandNotFound):
      return

    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.CheckFailure):
      data = await get_ignore_data(ctx.guild.id)
      ch = data["channel"]
      iuser = data["user"]
      cmd = data["command"]
      buser = data["bypassuser"]

      if str(ctx.author.id) in buser:
        return

      if str(ctx.channel.id) in ch:
        await ctx.reply(f"{ctx.author.mention} **This channel was in ignored list try my commands on other channel**.",
                        delete_after=8)
        return

      if str(ctx.author.id) in iuser:
        await ctx.reply(f"{ctx.author.mention} **You are set as an ignored user for this guild. Please try my commands in a different guild.**", delete_after=8)
        return

      if ctx.command.name in cmd or any(alias in cmd for alias in ctx.command.aliases):
        await ctx.reply(f"{ctx.author.mention} **This command is ignored in this guild. Please use other commands or try this command in a different guild**", delete_after=8)
        return

    if isinstance(error, commands.NoPrivateMessage):
      embed = discord.Embed(color=0xFF0000, description="You can't use my commands in DMs.")
      embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=20)
      return

    if isinstance(error, commands.TooManyArguments):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.CommandOnCooldown):
      embed = discord.Embed(color=0xFF0000, description=f"**{ctx.author.mention} Couldown is here Bro Tryy commands in {error.retry_after:.2f} seconds**.")
      embed.set_author(name="Cooldown", icon_url=self.client.user.avatar.url)
      
      embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=10)
      return

    if isinstance(error, commands.MaxConcurrencyReached):
      embed = discord.Embed(color=0xFF0000, description=f"{ctx.author.mention} This command is already in progress. Please let it finish and try again afterward.")
      embed.set_author(name="Command in Progress.", icon_url=self.client.user.avatar.url)
      
      embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=10)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.MissingPermissions):
      missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_permissions]
      fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1]) if len(missing) > 2 else " and ".join(missing)
      embed = discord.Embed(color=0xFF0000, description=f"**Ops! You don't have {fmt} Permission to run the {ctx.command.name} command!**")
      embed.set_author(name="Missing Permissions", icon_url=self.client.user.avatar.url)
      
      embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=7)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.BadArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.BotMissingPermissions):
      missing = ", ".join(error.missing_permissions)
      await ctx.reply(f'** Huh! I need {missing} Permission to run the {ctx.command.qualified_name}command! Give me {missing} Permission**', delete_after=7)
      return

    if isinstance(error, discord.HTTPException):
      print(f"[ERROR] HTTPException in {ctx.command}: {error}")
      return

    if isinstance(error, commands.CommandInvokeError):
      print(f"[ERROR] CommandInvokeError in {ctx.command}: {error}")
      print(f"  Original: {error.original}")
      return

