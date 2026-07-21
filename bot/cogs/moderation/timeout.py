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
from utils.emoji import CROSS, DELETE, TICK, ZWARNING
from discord.ext import commands
from discord import ui
from datetime import timedelta
import re
from utils.Tools import *

#class TimeoutView(ui.View):
  #  def __init__(self, user, author):
    #    super().__init__(timeout=120)
      #  self.user = user
    #    self.author = author
      #  self.message = None  
      #  self.color = discord.Color.from_rgb(255, 0, 0)

  #  async def interaction_check(self, interaction: discord.Interaction) -> bool:
     #   if interaction.user != self.author:
        #    await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
      #      return False
      #  return True

  #  async def on_timeout(self):
      #  for item in self.children:
        #    item.disabled = True
       # if self.message:
        #    await self.message.edit(view=self)

   # @ui.button(label="Unmute", style=discord.ButtonStyle.success)
    #async def unmute(self, interaction: discord.Interaction, button: discord.ui.Button):
      #  modal = ReasonModal(user=self.user, author=self.author, view=self)
       # await interaction.response.send_modal(modal)
#
   # @ui.button(style=discord.ButtonStyle.gray, emoji=DELETE)
  #  async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
      #  await interaction.message.delete()
#
#class AlreadyTimedoutView(ui.View):
   # def __init__(self, user, author):
     #   super().__init__(timeout=60)
       # self.user = user
      #  self.author = author
      #  self.message = None  

   # async def interaction_check(self, interaction: discord.Interaction) -> bool:
      #  if interaction.user != self.author:
        #    await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
        #    return False
       # return True

  #  async def on_timeout(self):
      #  for item in self.children:
       #     item.disabled = True
      #  if self.message:
      #      try:
        #        await self.message.edit(view=self)
         #   except Exception:
           #     pass

 #   @ui.button(label="Unmute", style=discord.ButtonStyle.success)
  #  async def unmute(self, interaction: discord.Interaction, button: discord.ui.Button):
     #   modal = ReasonModal(user=self.user, author=self.author, view=self)
     #   await interaction.response.send_modal(modal)

   # @ui.button(style=discord.ButtonStyle.gray, emoji=DELETE)
   # async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
     #   await interaction.message.delete()
#
#class ReasonModal(ui.Modal):
   # def __init__(self, user, author, view):
      #  super().__init__(title="Unmute Reason")
      #  self.user = user
     #   self.author = author
     #   self.view = view
     #   self.reason_input = ui.TextInput(label="Reason for Unmuting", placeholder="Provide a reason to unmute or leave it blank.", required = False, max_length=2000, style=discord.TextStyle.paragraph)
    #    self.add_item(self.reason_input)

   # async def on_submit(self, interaction: discord.Interaction):
    #    reason = self.reason_input.value or "No reason provided"
     #   try:
        #    await self.user.send(f"You have been Unmuted in **{self.author.guild.name}** by **{self.author}**. Reason: {reason or 'No reason provided'}")
       #     dm_status = "Yes"
        #except discord.Forbidden:
         #   dm_status = "No"
       # except discord.HTTPException:
         #   dm_status = "No"

       # embed = discord.Embed(description=f"** Target User:** [{self.user}](https://discord.com/users/{self.user.id})\n **User Mention:** {self.user.mention}\n** DM Sent:** {dm_status}\n**Reason:** {reason}", color=0xFF0000)
       # embed.set_author(name=f"Successfully Unmuted {self.user.name}", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
     #   embed.add_field(name=" Moderator:", value=interaction.user.mention, inline=False)
       # embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
      #  embed.timestamp = discord.utils.utcnow()
#
     #   await self.user.edit(timed_out_until=None, reason=f"Unmute requested by {self.author}")
      #  await interaction.response.edit_message(embed=embed, view=self.view)
      #  for item in self.view.children:
       #     item.disabled = True
     #   await interaction.message.edit(view=self.view)

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(255, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    def parse_time(self, time_str):
        time_pattern = r"(\d+)([mhd])"
        match = re.match(time_pattern, time_str)
        if match:
            time_value = int(match.group(1))
            time_unit = match.group(2)
            if time_unit == 'm' and 0 < time_value <= 60:
                return timedelta(minutes=time_value), f"{time_value} minutes"
            elif time_unit == 'h' and 0 < time_value <= 24:
                return timedelta(hours=time_value), f"{time_value} hours"
            elif time_unit == 'd' and 0 < time_value <= 28:
                return timedelta(days=time_value), f"{time_value} days"
        return None, None

    @commands.hybrid_command(
        name="mute",
        help="Mutes a user with optional time and reason",
        usage="mute <member> [time] [reason]",
        aliases=["timeout", "stfu","chup"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, user: discord.Member, time: str = None, *, reason=None):

        if user.is_timed_out():
            embed = discord.Embed(description="**Requested User is already muted in this server.**", color=self.color)
           # embed.add_field(name="__Unmute__:", value="Click on the `Unmute` button to remove the timeout from the user.")
            embed.set_author(name=f"{user.name} is Already Timed Out!", icon_url=self.get_user_avatar(user))
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
           # view = AlreadyTimedoutView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed)
           # view.message = message
            return

        if user == ctx.guild.owner:
            error = discord.Embed(color=self.color, description="You can't timeout the Server Owner!")
            error.set_author(name="Error Timing Out User")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=error)

        if ctx.author != ctx.guild.owner and user.top_role >= ctx.author.top_role:
            error = discord.Embed(color=self.color, description="You can't timeout users having higher or equal role than yours!")
            error.set_author(name="Error Timing Out User")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=error)

        if user.top_role >= ctx.guild.me.top_role:
            error = discord.Embed(color=self.color, description="I can't timeout users having higher or equal role than mine.")
            error.set_author(name="Error Timing Out User")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=error)

        time_delta, duration_text = self.parse_time(time) if time else (timedelta(hours=24), "24 hours")

        if not time_delta:
            error = discord.Embed(color=self.color, description="Invalid time format! Use `<number><m/h/d>` where `m` is minutes (max 60), `h` is hours (max 24), and `d` is days (max 28).")
            error.set_author(name="Error Timing Out User")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=error)

        try:
            await user.send(f"{ZWARNING} You have been muted in **{ctx.guild.name}** by **{ctx.author}** for {duration_text}. Reason: {reason or 'None'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        await user.edit(timed_out_until=discord.utils.utcnow() + time_delta, reason=f"Muted by {ctx.author} for {duration_text}. Reason: {reason or 'None'}")


        embed = discord.Embed(description=f"**{TICK} | Successfully Muted [{user}](https://discord.com/users/{user.id}) For {duration_text}\nReason {reason}**",
                              color=self.color)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_author(name=f"Successfully Muted {user.name}", icon_url=self.get_user_avatar(user))
      #  embed.add_field(name=" Moderator:", value=ctx.author.mention, inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
        embed.timestamp = discord.utils.utcnow()
        
        #view = TimeoutView(user=user, author=ctx.author)
        message = await ctx.send(embed=embed)
       # view.message = message

    @mute.error
    async def mute_error(self, ctx, error):
        
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(title=f"{CROSS}> Access Denied", description="I don't have permission to mute members.", color=self.color)
            await ctx.send(embed=embed)
        elif isinstance(error, discord.Forbidden):
            embed = discord.Embed(title=f"{CROSS} Missing Permissions", description="I can't mute this user as they might have higher privileges (e.g., Admin).", color=self.color)
            await ctx.send(embed=embed)
            
        else:
            embed = discord.Embed(title=f"{CROSS} Unexpected Error", description=str(error), color=self.color)
            await ctx.send(embed=embed)

