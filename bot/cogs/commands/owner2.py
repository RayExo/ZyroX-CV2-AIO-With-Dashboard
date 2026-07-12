import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import Member
from utils import Paginator, DescriptionEmbedPaginator
from datetime import timedelta
import asyncio

class Global(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.local_frozen_nicks = {}  
        self.client.frozen_nicknames = {}

    @commands.group(name="global", invoke_without_command=True)
    @commands.is_owner()
    async def global_command(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @commands.command(name="GB",help="Bans the user from all mutual guilds.")
    @commands.is_owner()
    async def global_ban(self, ctx: commands.Context, user: discord.User, reason: str = "Severe violations of Discord's terms of service."):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"Are you sure to Ban {user.display_name} Globally?",
            description=f"The user is in **{mutual_count}** mutual guilds with the bot.\n\nGlobal Ban Requestor: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Processing global ban for {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    await guild.ban(user, reason=reason)
                    success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Success",
                description=f"Banned the user in {len(success)} of {mutual_count} mutual guilds.",
                color=0xFF0000
            )
            embed.add_field(name="Success Count", value=f"{len(success)} Guilds")
            embed.add_field(name="Failure Count", value=f"{len(failure)} Guilds")
            success_button = Button(label="List Successful", style=discord.ButtonStyle.green)
            failure_button = Button(label="List Unsuccessful", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Bans [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Unsuccessful Bans [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)

    @global_command.command(name="kick", help="Kicks the user from all mutual guilds.")
    @commands.is_owner()
    async def global_kick(self, ctx: commands.Context, user: discord.User, reason: str = "Severe violations of Discord's terms of service."):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"Are you sure to Kick {user.display_name} Globally?",
            description=f"The user is in **{mutual_count}** mutual guilds with the bot.\n\nGlobal Kick Requestor: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Processing global kick for {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    await guild.kick(user, reason=reason)
                    success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Success",
                description=f"Kicked the user in {len(success)} of {mutual_count} mutual guilds.",
                color=0xFF0000
            )
            embed.add_field(name="Success Count", value=f"{len(success)} Guilds")
            embed.add_field(name="Failure Count", value=f"{len(failure)} Guilds")
            success_button = Button(label="List Successful", style=discord.ButtonStyle.green)
            failure_button = Button(label="List Unsuccessful", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Kicks [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Unsuccessful Kicks [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)

    @global_command.command(name="timeout", help="Timeouts the user for 28 days in all mutual guilds.")
    @commands.is_owner()
    async def global_timeout(self, ctx: commands.Context, user: discord.User, reason: str = "Severe violations of Discord's terms of service."):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"Are you sure  to Timeout {user.display_name} Globally for 28 days?",
            description=f"The user is in **{mutual_count}** mutual guilds with the bot.\n\nGlobal Timeout Requestor: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Processing global timeout for {user.name}...")
            success, failure = [], []
            
            for guild in mutual_guilds:
                member = guild.get_member(user.id)
                time_delta =  (timedelta(days=28))
                if member:
                    try:
                        await member.edit(timed_out_until=discord.utils.utcnow() + time_delta, reason=reason)
                        success.append(guild.name)
                    except:
                        failure.append(guild.name)
            embed = discord.Embed(
                title="Success",
                description=f"Timed out the user in {len(success)} of {mutual_count} mutual guilds.",
                color=0xFF0000
            )
            embed.add_field(name="Success Count", value=f"{len(success)} Guilds")
            embed.add_field(name="Failure Count", value=f"{len(failure)} Guilds")
            success_button = Button(label="List Successful", style=discord.ButtonStyle.green)
            failure_button = Button(label="List Unsuccessful", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Timeouts [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Unsuccessful Timeouts [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)


    @global_command.command(name="nick", help="Changes the nickname of a user in all mutual guilds.")
    @commands.is_owner()
    async def global_nick(self, ctx: commands.Context, user: discord.User, *, name: str):
        if len(name) > 32:
            return await ctx.send("Nickname cannot exceed 32 characters. Please provide a shorter nickname.")

        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"Are you sure to Change {user.display_name}'s Nickname Globally?",
            description=f"The user is in **{mutual_count}** mutual guilds with the bot.\n\nGlobal Nick Requestor: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Processing global nickname change for {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=name)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Success",
                description=f"Set the nickname for {user.name} in {len(success)} of {mutual_count} mutual guilds.",
                color=0xFF0000
            )
            embed.add_field(name="Success Count", value=f"{len(success)} Guilds")
            embed.add_field(name="Failure Count", value=f"{len(failure)} Guilds")
            success_button = Button(label="List Successful", style=discord.ButtonStyle.green)
            failure_button = Button(label="List Unsuccessful", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Nickname Change [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Unsuccessful Nickname Change [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)


    @global_command.command(name="clearnick", help="Clears the nickname of a user in all mutual guilds.")
    @commands.is_owner()
    async def global_clearnick(self, ctx: commands.Context, user: discord.User):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"Are you sure to Clear {user.display_name}'s Nickname Globally?",
            description=f"The user is in **{mutual_count}** mutual guilds with the bot.\n\nGlobal Clearnick Requestor: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Processing global nickname clear for {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=None)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Success",
                description=f"Cleared the nickname for {user.name} in {len(success)} of {mutual_count} mutual guilds.",
                color=0xFF0000
            )
            embed.add_field(name="Success Count", value=f"{len(success)} Guilds")
            embed.add_field(name="Failure Count", value=f"{len(failure)} Guilds")
            success_button = Button(label="List Successful", style=discord.ButtonStyle.green)
            failure_button = Button(label="List Unsuccessful", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Nickname Clear [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Unsuccessful Nickname Clear [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)


    @global_command.command(name="freezenick", help="Freezes a user's nickname in all mutual guilds.")
    @commands.is_owner()
    async def global_freezenick(self, ctx: commands.Context, user: discord.User, *, name: str):
        if len(name) > 32:
            return await ctx.send("Nickname cannot exceed 32 characters. Please provide a shorter nickname.")

        if not hasattr(self.client, "frozen_nicknames"):
            self.client.frozen_nicknames = {}

        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"Are you sure to Freeze {user.display_name}'s Nickname Globally?",
            description=f"The user is in {mutual_count} mutual guilds with the bot.\n\nGlobal Freezenick Requestor: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=None)

            self.client.frozen_nicknames[user.id] = {
                "name": name,
                "guild_ids": [guild.id for guild in mutual_guilds],
            }

            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=name)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)

            embed = discord.Embed(
                title="Results",
                description=f"Frozen nickname for {user.name} in {len(success)} of {mutual_count} mutual guilds.",
                color=0xFF0000
            )
            embed.add_field(name="Success Count", value=f"{len(success)} Guilds")
            embed.add_field(name="Failure Count", value=f"{len(failure)} Guilds")

            success_button = Button(label="List Successful", style=discord.ButtonStyle.green)
            failure_button = Button(label="List Unsuccessful", style=discord.ButtonStyle.red)
            stop_button = Button(label="Stop Freezing", style=discord.ButtonStyle.red)
            result_view = View()
            result_view.add_item(success_button)
            result_view.add_item(failure_button)
            result_view.add_item(stop_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Freezes [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Unsuccessful Freezes [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def stop_freeze(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
                self.client.frozen_nicknames.pop(user.id, None)
                await interaction.response.send_message(f"Nickname freezing stopped for {user.name}.", ephemeral=True)

            success_button.callback = list_success
            failure_button.callback = list_failure
            stop_button.callback = stop_freeze

            await ctx.send(embed=embed, view=result_view)
            self.client.loop.create_task(self.nickname_freeze_task(user.id))

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()
            await ctx.send("Nickname freezing cancelled.")

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)

    async def nickname_freeze_task(self, user_id: int):
        while user_id in self.client.frozen_nicknames:
            user_data = self.client.frozen_nicknames[user_id]
            frozen_name = user_data["name"]
            guild_ids = user_data["guild_ids"]

            for guild_id in guild_ids:
                guild = self.client.get_guild(guild_id)
                if not guild:
                    continue
                member = guild.get_member(user_id)
                if member and member.nick != frozen_name:
                    try:
                        await member.edit(nick=frozen_name)
                    except:
                        pass

            await asyncio.sleep(10)

 

    @global_command.command(name="unfreezenick", help="Unfreezes a user's nickname in all mutual guilds.")
    @commands.is_owner()
    async def global_unfreezenick(self, ctx: commands.Context, user: discord.User):
        if not hasattr(self.client, "frozen_nicknames"):
            self.client.frozen_nicknames = {}

        if user.id not in self.client.frozen_nicknames:
            return await ctx.send(f"❌ | {user.name}'s nickname is not being frozen.")

        del self.client.frozen_nicknames[user.id]
        await ctx.send(f"✅ | Nickname freezing stopped for {user.name}.")


    @commands.command(name="freezenick", help="Freezes a member's nickname in the current server.")
    @commands.has_permissions(manage_nicknames=True)
    async def freeze_nickname(self, ctx: commands.Context, member: Member, *, nickname: str):
        guild_id = ctx.guild.id
        if guild_id not in self.local_frozen_nicks:
            self.local_frozen_nicks[guild_id] = {}

        if member.id in self.local_frozen_nicks[guild_id]:
            return await ctx.send(f"{member.mention}'s nickname is already being frozen.")

        
        try:
            await member.edit(nick=nickname)
            self.local_frozen_nicks[guild_id][member.id] = nickname
            await ctx.send(f"Freezing {member.mention}'s nickname as '{nickname}'.")
        except:
            return await ctx.send(f"Could not change {member.mention}'s nickname due to insufficient permissions.")

        async def monitor_nickname():
            while member.id in self.local_frozen_nicks.get(guild_id, {}):
                if member.nick != nickname:
                    try:
                        await member.edit(nick=nickname)
                    except:
                        self.local_frozen_nicks[guild_id].pop(member.id, None)
                        await ctx.send(f"Stopped monitoring {member.mention}'s nickname due to insufficient permissions.")
                        break
                await asyncio.sleep(10)

            if not self.local_frozen_nicks[guild_id]:
                del self.local_frozen_nicks[guild_id]

        self.client.loop.create_task(monitor_nickname())

    @commands.command(name="unfreezenick", help="Unfreezes a member's nickname in the current server.")
    @commands.has_permissions(manage_nicknames=True)
    async def unfreeze_nickname(self, ctx: commands.Context, member: Member):
        guild_id = ctx.guild.id
        if guild_id in self.local_frozen_nicks and member.id in self.local_frozen_nicks[guild_id]:
            self.local_frozen_nicks[guild_id].pop(member.id, None)
            if not self.local_frozen_nicks[guild_id]:
                del self.local_frozen_nicks[guild_id]
            await ctx.send(f"✅ | Stopped freezing {member.mention}'s nickname.")
        else:
            await ctx.send(f"❌ | {member.mention}'s nickname is not currently being frozen.")


