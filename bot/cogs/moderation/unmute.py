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
from utils.emoji import DELETE, TICK, ZWARNING
from discord.ext import commands
from discord import ui
from utils.Tools import *
from datetime import timedelta

#class MuteUnmuteView(ui.View):
   # def __init__(self, user, author):
      #  super().__init__(timeout=120)
      #  self.user = user
        #self.author = author
      #  self.message = None  

  #  async def interaction_check(self, interaction: discord.Interaction) -> bool:
      #  if interaction.user != self.author:
        #    await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
       #     return False
      #  return True

   # async def on_timeout(self):
      #  for item in self.children:
         #   if item.label != "Delete":
            #    item.disabled = True
      #  if self.message:
         #   try:
             #   await self.message.edit(view=self)
          #  except Exception:
              #  pass

   # @ui.button(label="Add Timeout", style=discord.ButtonStyle.danger)
   # async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):
      #  modal = MuteReasonModal(user=self.user, author=self.author, view=self)
      #  await interaction.response.send_modal(modal)

        
     #   for item in self.children:
        #    if item.label != "Delete":
              #  item.disabled = True
        #await self.message.edit(view=self)

   # @ui.button(style=discord.ButtonStyle.gray, emoji=DELETE)
   # async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
     #   await interaction.message.delete()


#class MuteReasonModal(ui.Modal):
   # def __init__(self, user, author, view):
       # super().__init__(title="Mute Information")
      #  self.user = user
       # self.author = author
       # self.view = view
       # self.time_input = ui.TextInput(label="Duration (m/h/d)", placeholder="Leave blank for default 24h", required=False, max_length=5)
      #  self.reason_input = ui.TextInput(label="Reason", placeholder="Provide a reason or leave it blank.", required=False, max_length=2000, style=discord.TextStyle.paragraph)
       # self.add_item(self.time_input)
       # self.add_item(self.reason_input)

    #async def on_submit(self, interaction: discord.Interaction):
      #  reason = self.reason_input.value or "No reason provided"
      #  time_str = self.time_input.value or "24h"
        #time_seconds = self.parse_duration(time_str)

       # if time_seconds is None:
          #  await interaction.response.send_message(f"Invalid time format! Please provide in m (minutes), h (hours), or d (days).", ephemeral=True)
          #  return

      #  try:
         #   await self.user.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=time_seconds))
      #  except discord.Forbidden:
          #  await interaction.response.send_message(f"Failed to mute {self.user.mention}. I lack the permissions.", ephemeral=True)
         #   return

        
     #   try:
        #    await self.user.send(f"{ZWARNING} You have been muted in **{interaction.guild.name}** for {time_str}. Reason: {reason}")
         #   dm_status = "Yes"
       # except discord.Forbidden:
          #  dm_status = "No"
        #except discord.HTTPException:
           # dm_status = "No"

      #  success_embed = discord.Embed(
         #   description=f"** Target User:** [{self.user}](https://discord.com/users/{self.user.id})\n**User Mention:** {self.user.mention}\n**Reason:** {reason}\n **DM Sent:** {dm_status}", 
          #  color=0xFF0000
      #  )
       # success_embed.set_author(name=f"Muted {self.user.name}", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
      #  success_embed.add_field(name=" Moderator:", value=self.author.mention, inline=False)
       # success_embed.add_field(name="Duration", value=f"{time_str}", inline=False)
   #     success_embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
       # success_embed.timestamp = discord.utils.utcnow()

       # await interaction.response.edit_message(embed=success_embed, view=self.view)

        
       # for item in self.view.children:
           # if item.label != "Delete":
              #  item.disabled = True
      #  await self.view.message.edit(view=self.view)

  #  def parse_duration(self, duration_str: str) -> int:
       # try:
           # if duration_str.endswith("m"):
               # duration = int(duration_str[:-1])
               # return duration * 60
           # elif duration_str.endswith("h"):
               # duration = int(duration_str[:-1])
          #      return duration * 3600
           # elif duration_str.endswith("d"):
                #duration = int(duration_str[:-1])
               # return duration * 86400
           # else:
                
              #  duration = int(duration_str)
             #   if duration > 60:
                   # return (duration // 60) * 3600  
              #  else:
                 #   return duration * 60  
       # except ValueError:
       #     return None


class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(255, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(
        name="unmute",
        help="Unmutes a user from the Server",
        usage="unmute <member>",
        aliases=["untimeout"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, user: discord.Member):
        if not user.timed_out_until or user.timed_out_until <= discord.utils.utcnow():
            embed = discord.Embed(description="**Requested User is not muted in this server.**", color=self.color)
            #embed.add_field(name="__Mute__:", value="Click on the `Add Timeout` button to mute the mentioned user.")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_author(name=f"{user.name} is Not Muted!", icon_url=self.get_user_avatar(user))
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
          #  view = MuteUnmuteView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed)
          #  view.message = message
            return

        try:
            await user.edit(timed_out_until=None)

            
            try:
                await user.send(f"{TICK} You have been unmuted in **{ctx.guild.name}**.")
                dm_status = "Yes"
            except discord.Forbidden:
                dm_status = "No"
            except discord.HTTPException:
                dm_status = "No"

        except discord.Forbidden:
            error = discord.Embed(color=self.color, description="I can't unmute a user with higher permissions!")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            error.set_author(name="Error Unmuting User", icon_url="https://cdn.discordapp.com/emojis/1448949627712966717.png?v=1&size=48&quality=lossless")
            return await ctx.send(embed=error)

        embed = discord.Embed(
            description=f"**{TICK} | Successfully Unmuted [{user}](https://discord.com/users/{user.id})**",
            color=self.color
        )        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_author(name=f"Successfully Unmuted {user.name}", icon_url=self.get_user_avatar(user))
    #    embed.add_field(name=" Moderator:", value=ctx.author.mention, inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
        embed.timestamp = discord.utils.utcnow()

     #   view = MuteUnmuteView(user=user, author=ctx.author)
        message = await ctx.send(embed=embed)
      #  view.message = message

