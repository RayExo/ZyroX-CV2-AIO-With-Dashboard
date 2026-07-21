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
from utils.emoji import TICK, ZWARNING
from discord.ext import commands
from discord import ui
from utils.Tools import *

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(255, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(
        name="ban",
        help="Bans a user from the Server",
        usage="ban <member>",
        aliases=["fuckban", "hackban","kuttaban"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):

        member = ctx.guild.get_member(user.id)
        if not member:
            try:
                user = await self.bot.fetch_user(user.id)
            except discord.NotFound:
                # User not found container
                container = ui.Container()
                container.add_item(ui.TextDisplay(f"❌ **User Not Found**\nUser with ID {user.id} not found."))
                view = ui.LayoutView()
                view.add_item(container)
                await ctx.send(view=view)
                return

        bans = [entry async for entry in ctx.guild.bans()]
        if any(ban_entry.user.id == user.id for ban_entry in bans):
            # Already banned container
            container = ui.Container()
            container.add_item(ui.TextDisplay(f"⚠️ **{user.name} is Already Banned!**"))
            container.add_item(ui.TextDisplay("**Requested User is already banned in this server.**"))
            container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            await ctx.send(view=view)
            return

        if member == ctx.guild.owner:
            # Server owner error container
            container = ui.Container()
            container.add_item(ui.TextDisplay("❌ **Error Banning User**"))
            container.add_item(ui.TextDisplay("I can't ban the Server Owner!"))
            container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            return await ctx.send(view=view)

        if isinstance(member, discord.Member) and member.top_role >= ctx.guild.me.top_role:
            # Role hierarchy error container
            container = ui.Container()
            container.add_item(ui.TextDisplay("❌ **Error Banning User**"))
            container.add_item(ui.TextDisplay("I can't ban a user with a higher or equal role!"))
            container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            return await ctx.send(view=view)

        if isinstance(member, discord.Member):
            if ctx.author != ctx.guild.owner:
                if member.top_role >= ctx.author.top_role:
                    # Author role hierarchy error container
                    container = ui.Container()
                    container.add_item(ui.TextDisplay("❌ **Error Banning User**"))
                    container.add_item(ui.TextDisplay("You can't ban a user with a higher or equal role!"))
                    container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
                    view = ui.LayoutView()
                    view.add_item(container)
                    return await ctx.send(view=view)

        # Try to DM the user
        try:
            await user.send(f"{ZWARNING} You have been banned from **{ctx.guild.name}** by **{ctx.author}**. Reason: {reason or 'No reason provided'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        # Ban the user
        await ctx.guild.ban(user, reason=f"Ban requested by {ctx.author} for reason: {reason or 'No reason provided'}")

        # Success container with Components V2
        container = ui.Container()
        container.add_item(ui.TextDisplay(f"✅ **Successfully Banned {user.name}**"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**{TICK} | [{user}](https://discord.com/users/{user.id}) Has Been Banned Successfully**"
            f"\n**Reason:** {reason or 'No reason provided'}"
            f"\n**DM Sent:** {dm_status}"
            f"\n**Moderator:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(f"*Requested by {ctx.author} • {discord.utils.format_dt(discord.utils.utcnow(), 'R')}*"))
        
        view = ui.LayoutView()
        view.add_item(container)
        
        message = await ctx.send(view=view)

async def setup(bot):
    await bot.add_cog(Ban(bot))