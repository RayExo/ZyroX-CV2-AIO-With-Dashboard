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
from utils.emoji import ICONS_CHANNEL, ICONS_PLUS, TICK, ZTICK
from discord.ext import commands
from discord.ui import View, Select, Button
import aiosqlite
import asyncio
import re
import json
from utils.Tools import *

class VariableButton(Button):
    def __init__(self, author):
        super().__init__(label="Variables", style=discord.ButtonStyle.secondary)
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("Only the command author can use this button.", ephemeral=True)
            return

        variables = {
            "{user}": "Mentions the user (e.g., @UserName).",
            "{user_avatar}": "The user's avatar URL.",
            "{user_name}": "The user's username.",
            "{user_id}": "The user's ID number.",
            "{user_nick}": "The user's nickname in the server.",
            "{user_joindate}": "The user's join date in the server (formatted as Day, Month Day, Year).",
            "{user_createdate}": "The user's account creation date (formatted as Day, Month Day, Year).",
            "{server_name}": "The server's name.",
            "{server_id}": "The server's ID number.",
            "{server_membercount}": "The server's total member count.",
            "{server_icon}": "The server's icon URL."
        }
        

        embed = discord.Embed(
            title="Available Placeholders",
            description="Use these placeholders in your welcome message:",
            color=discord.Color(0xFF0000)
        )

        for var, desc in variables.items():
            embed.add_field(name=var, value=desc, inline=False)

        embed.set_footer(text="Add placeholders directly in the welcome message or embed fields.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self._create_table())

    async def _create_table(self):
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS welcome (
                guild_id INTEGER PRIMARY KEY,
                welcome_type TEXT,
                welcome_message TEXT,
                channel_id INTEGER,
                embed_data TEXT,
                auto_delete_duration INTEGER
            )
            """)
            await db.commit()

    @commands.hybrid_group(invoke_without_command=True, name="greet", help="Shows all the greet commands.")
    @blacklist_check()
    @ignore_check()
    async def greet(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @greet.command(name="setup", help="Configures a welcome message for new members joining the server. ")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_setup(self, ctx):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT * FROM welcome WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()
        
        if row:
            error = discord.Embed(description=f"A welcome message has already been set in {ctx.guild.name}. Use `{ctx.prefix}greet reset` to reconfigure.", color=0xFF0000)
            error.set_author(name="Error", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            return await ctx.send(embed=error)
            
        options_view = View(timeout=600)

        async def option_callback(interaction: discord.Interaction, button: Button):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return
            await interaction.response.defer()

            if button.custom_id == "simple":
                await interaction.message.delete()
                await self.simple_setup(ctx)
                
            elif button.custom_id == "embed":
                await interaction.message.delete()
                await self.embed_setup(ctx)
            elif button.custom_id == "cancel":
                await interaction.message.delete()

        button_simple = Button(label="Simple", style=discord.ButtonStyle.success, custom_id="simple")
        button_simple.callback = lambda interaction: option_callback(interaction, button_simple)
        options_view.add_item(button_simple)

        button_embed = Button(label="Embed", style=discord.ButtonStyle.success, custom_id="embed")
        button_embed.callback = lambda interaction: option_callback(interaction, button_embed)
        options_view.add_item(button_embed)

        button_cancel = Button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel")
        button_cancel.callback = lambda interaction: option_callback(interaction, button_cancel)
        options_view.add_item(button_cancel)

        embed = discord.Embed(
            title="Welcome Message Setup",
            description="Choose the type of welcome message you want to create:",
            color=0xFF0000
        )

        embed.add_field(
            name=" Simple",
            value="Send a plain text welcome message. You can use placeholders to personalize it.\n\n",
            inline=False
        )
        embed.add_field(
            name=" Embed",
            value="Send a welcome message in an embed format. You can customize the embed with a title, description, image, etc.",
            inline=False
        )

        embed.set_footer(text="Click the buttons below to choose the welcome message type.", icon_url=self.bot.user.display_avatar.url)
        

        await ctx.send(embed=embed, view=options_view)

    async def simple_setup(self, ctx):
        setup_view = View(timeout=600)
        first = View(timeout=600)
        message_content = []

        placeholders = {
            "user": ctx.author.mention,
            "user_avatar": ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url,
            "user_name": ctx.author.name,
            "user_id": ctx.author.id,
            "user_nick": ctx.author.display_name,
            "user_joindate": ctx.author.joined_at.strftime("%a, %b %d, %Y"),
            "user_createdate": ctx.author.created_at.strftime("%a, %b %d, %Y"),
            "server_name": ctx.guild.name,
            "server_id": ctx.guild.id,
            "server_membercount": ctx.guild.member_count,
            "server_icon": ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png",
            "timestamp": discord.utils.format_dt(ctx.message.created_at)
        }

        def safe_format(text):
            placeholders_lower = {k.lower(): v for k, v in placeholders.items()}

            def replace_var(match):
                var_name = match.group(1).lower()
                return str(placeholders_lower.get(var_name, f"{{{var_name}}}"))

            return re.sub(r"\{(\w+)\}", replace_var, text or "")
            

        async def update_preview(content):
            preview = safe_format(content)
            await preview_message.edit(content=f"**Preview:** {preview}", view=setup_view)

        first.add_item(VariableButton(ctx.author))

        preview_message = await ctx.send("__**Simple Message Setup**__ \nEnter your welcome message here:", view=first)

        async def submit_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return
            if message_content:
                await self._save_welcome_data(ctx.guild.id, "simple", message_content[0])
                await interaction.response.send_message(f"{TICK}> Welcome message setup completed!")
                for item in setup_view.children:
                    item.disabled = True
                await preview_message.edit(view=setup_view)
            else:
                await interaction.response.send_message("No message entered to submit.", ephemeral=True)

        async def edit_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return
            await interaction.response.defer()
            await ctx.send("Enter the updated welcome message:")
            try:
                msg = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                message_content.clear()
                message_content.append(msg.content)
                await update_preview(msg.content)
            except asyncio.TimeoutError:
                await ctx.send("Editing timed out.")

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return
            await preview_message.delete()

        submit_button = Button(label="Submit", style=discord.ButtonStyle.success)
        submit_button.callback = submit_callback
        setup_view.add_item(submit_button)

        edit_button = Button(label="Edit", style=discord.ButtonStyle.primary)
        edit_button.callback = edit_callback
        setup_view.add_item(edit_button)
        setup_view.add_item(VariableButton(ctx.author))

        cancel_button = Button(emoji=ICONS_PLUS, style=discord.ButtonStyle.secondary)
        cancel_button.callback = cancel_callback
        setup_view.add_item(cancel_button)

        try:
            msg = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            message_content.append(msg.content)
            await update_preview(msg.content)
        except asyncio.TimeoutError:
            await ctx.send("Setup timed out.")

    
    async def _save_welcome_data(self, guild_id, welcome_type, message, embed_data=None):
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("""
            INSERT OR REPLACE INTO welcome (guild_id, welcome_type, welcome_message, embed_data)
            VALUES (?, ?, ?, ?)
            """, (guild_id, welcome_type, message, json.dumps(embed_data) if embed_data else None))
            await db.commit()

    


    async def embed_setup(self, ctx):
        setup_view = View(timeout=600)
        embed_data = {
            "message": None,
            "title": None,
            "description": None,
            "color": None,
            "footer_text": None,
            "footer_icon": None,
            "author_name": None,
            "author_icon": None,
            "thumbnail": None,
            "image": None,
        }

        placeholders = {
            "user": ctx.author.mention,
            "user_avatar": ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url,
            "user_name": ctx.author.name,
            "user_id": ctx.author.id,
            "user_nick": ctx.author.display_name,
            "user_joindate": ctx.author.joined_at.strftime("%a, %b %d, %Y"),
            "user_createdate": ctx.author.created_at.strftime("%a, %b %d, %Y"),
            "server_name": ctx.guild.name,
            "server_id": ctx.guild.id,
            "server_membercount": ctx.guild.member_count,
            "server_icon": ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png",
            "timestamp": discord.utils.format_dt(ctx.message.created_at)
        }

        def safe_format(text):
            placeholders_lower = {k.lower(): v for k, v in placeholders.items()}  

            def replace_var(match):
                var_name = match.group(1).lower()
                return str(placeholders_lower.get(var_name, f"{{{var_name}}}"))

            return re.sub(r"\{(\w+)\}", replace_var, text or "")
            

        async def update_preview():
            content = safe_format(embed_data["message"]) or "Message Content."
            embed = discord.Embed(
    title=safe_format(embed_data["title"]) or "",
    description=safe_format(embed_data["description"]) or "```Customize your welcome embed, take help of variables.```",
    color=discord.Color(embed_data["color"]) if embed_data["color"] else discord.Color(0x2f3136)
            )

            
            if embed_data["footer_text"]:
                embed.set_footer(text=safe_format(embed_data["footer_text"]), icon_url=safe_format(embed_data["footer_icon"]) or None)
            if embed_data["author_name"]:
                embed.set_author(name=safe_format(embed_data["author_name"]), icon_url=safe_format(embed_data["author_icon"]) or None)
            if embed_data["thumbnail"]:
                embed.set_thumbnail(url=safe_format(embed_data["thumbnail"]))
            if embed_data["image"]:
                embed.set_image(url=safe_format(embed_data["image"]))

            await preview_message.edit(content="**Embed Preview:** " + content, embed=embed, view=setup_view)

        preview_message = await ctx.send("Configuring embed welcome message...")

        async def handle_selection(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return

            selected_option = select_menu.values[0]
            await interaction.response.defer()

            try:
                if selected_option == "message":
                    await ctx.send("Enter the welcome message content:")
                    msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                    embed_data["message"] = msg.content

                elif selected_option == "title":
                    await ctx.send("Enter the embed title:")
                    msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                    embed_data["title"] = msg.content

                elif selected_option == "description":
                    await ctx.send("Enter the embed description:")
                    msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                    embed_data["description"] = msg.content

                elif selected_option == "color":
                    await ctx.send("Enter a hex color (e.g., #3498db or 3498db):")
                    msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                    color_code = msg.content.lstrip("#")
                    if all(c in "0123456789abcdefABCDEF" for c in color_code) and len(color_code) in {3, 6}:
                        embed_data["color"] = int(color_code.lstrip("#"), 16)
                    else:
                        await ctx.send("Invalid color code. Please enter a valid hex color.")

                elif selected_option in ["footer_text", "footer_icon", "author_name", "author_icon", "thumbnail", "image"]:
                    await ctx.send(f"Enter the URL or text for {selected_option.replace('_', ' ')}:")
                    msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                    url_or_text = msg.content
                    if selected_option in ["footer_icon", "author_icon", "thumbnail", "image"]:
                        if url_or_text.startswith("http") or url_or_text in ["{user_avatar}", "{server_icon}"]:
                            embed_data[selected_option] = url_or_text
                        else:
                            await ctx.send("Invalid URL. Please enter a valid image URL or a supported placeholder ({user_avatar} or {server_icon}).")
                    else:
                        embed_data[selected_option] = url_or_text

                await update_preview()
                await interaction.followup.send(f"{selected_option.capitalize()} updated.", ephemeral=True)
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. Please try again.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")

        select_menu = Select(
            placeholder="Choose an option to edit the Embed",
            options=[
                discord.SelectOption(label="Message Content", value="message"),
                discord.SelectOption(label="Title", value="title"),
                discord.SelectOption(label="Description", value="description"),
                discord.SelectOption(label="Color", value="color"),
                discord.SelectOption(label="Footer Text", value="footer_text"),
                discord.SelectOption(label="Footer Icon", value="footer_icon"),
                discord.SelectOption(label="Author Name", value="author_name"),
                discord.SelectOption(label="Author Icon", value="author_icon"),
                discord.SelectOption(label="Thumbnail", value="thumbnail"),
                discord.SelectOption(label="Image", value="image")
            ]
        )
        select_menu.callback = handle_selection
        setup_view.add_item(select_menu)

        async def submit_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return
            if not any(embed_data[key] for key in ["title", "description"]):
                await interaction.response.send_message("Please provide at least a title or an description before submitting.", ephemeral=True)
                return

            await self._save_welcome_data(ctx.guild.id, "embed", embed_data["message"] or "", embed_data)
            await interaction.response.send_message(f"{TICK}> Embed welcome message setup completed!")

            for item in setup_view.children:
                item.disabled = True
            await preview_message.edit(view=setup_view)

        submit_button = Button(label="Submit", style=discord.ButtonStyle.success)
        submit_button.callback = submit_callback
        setup_view.add_item(submit_button)
        setup_view.add_item(VariableButton(ctx.author))

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("You cannot interact with this setup.", ephemeral=True)
                return
            await preview_message.delete()
            await interaction.response.send_message("Embed setup cancelled.", ephemeral=True)

        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.danger)
        cancel_button.callback = cancel_callback
        setup_view.add_item(cancel_button)

        await update_preview()

    

    @greet.command(name="reset", aliases=["disable"], help="Resets and deletes the current welcome configuration for the server.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_reset(self, ctx):
        async with aiosqlite.connect("db/welcome.db") as db:
            cursor = await db.execute("SELECT 1 FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
            is_set_up = await cursor.fetchone()

        if not is_set_up: 
            error = discord.Embed(description=f"No welcome message has been set for {ctx.guild.name}! Please set a welcome message first using `{ctx.prefix}greet setup`", color=0xFF0000)
            error.set_author(name="Greet is not configured!", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            return await ctx.send(embed=error)
            
        embed = discord.Embed(
            title="Are you sure?",
            description="This will remove all welcome configurations & data related to welcome messages for this server!",
            color=0xFF0000
        )

        yes_button = Button(label="Confirm", style=discord.ButtonStyle.danger)
        no_button = Button(label="Cancel", style=discord.ButtonStyle.secondary)

        async def yes_button_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Only the command author can confirm this action.", ephemeral=True)
                return

            async with aiosqlite.connect("db/welcome.db") as db:
                await db.execute("DELETE FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
                await db.commit()

            embed.color = discord.Color(0xFF0000)
            embed.title = f"{TICK}> Success"
            embed.description = "Welcome message configuration has been successfully reset."
            await interaction.message.edit(embed=embed, view=None)

        async def no_button_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Only the command author can cancel this action.", ephemeral=True)
                return

            embed.color = discord.Color(0xFF0000)
            embed.title = "Cancelled"
            embed.description = "Greet Reset operation has been cancelled."
            await interaction.message.edit(embed=embed, view=None)

        yes_button.callback = yes_button_callback
        no_button.callback = no_button_callback

        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        await ctx.send(embed=embed, view=view)
        

    @greet.command(name="channel", help="Sets the channel where welcome messages will be sent.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_channel(self, ctx):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT welcome_type, channel_id FROM welcome WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                welcome_message = result[0] if result else None
                welcome_channel = ctx.guild.get_channel(result[1]) if result and result[1] else None

        if not welcome_message:
            error = discord.Embed(description=f"No welcome message has been set for {ctx.guild.name}! Please set a welcome message first using `{ctx.prefix}greet setup`", color=0xFF0000)
            error.set_author(name="Greet is not configured!", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            await ctx.send(embed=error)
            return

        channels = ctx.guild.text_channels
        chunk_size = 25
        chunks = [channels[i:i + chunk_size] for i in range(0, len(channels), chunk_size)]
        current_page = 0

        def generate_view(page):
            select_menu = Select(
                placeholder="Select a channel for welcome messages",
                options=[
                    discord.SelectOption(label=channel.name, emoji=ICONS_CHANNEL, value=str(channel.id))
                    for channel in chunks[page]
                ]
            )

            async def select_callback(interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to set the welcome channel.", ephemeral=True)
                    return

                selected_channel_id = int(select_menu.values[0])
                selected_channel = ctx.guild.get_channel(selected_channel_id)

                async with aiosqlite.connect("db/welcome.db") as db:
                    await db.execute("UPDATE welcome SET channel_id = ? WHERE guild_id = ?", (selected_channel_id, ctx.guild.id))
                    await db.commit()

                embed.description = f"Current Welcome Channel: {selected_channel.mention}"
                await interaction.response.edit_message(embed=embed, view=None)
                await ctx.send(f"{TICK}> Welcome channel has been set to {selected_channel.mention}")

            select_menu.callback = select_callback

            next_button = Button(label="Next List of Channels", style=discord.ButtonStyle.secondary, disabled=page >= len(chunks) - 1)
            previous_button = Button(label="Previous", style=discord.ButtonStyle.secondary, disabled=page <= 0)

            async def next_callback(interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to navigate these menus.", ephemeral=True)
                    return
                nonlocal current_page
                current_page += 1
                await interaction.response.edit_message(embed=embed, view=generate_view(current_page))

            async def previous_callback(interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to navigate these menus.", ephemeral=True)
                    return
                nonlocal current_page
                current_page -= 1
                await interaction.response.edit_message(embed=embed, view=generate_view(current_page))

            next_button.callback = next_callback
            previous_button.callback = previous_callback

            view = View()
            view.add_item(select_menu)
            view.add_item(previous_button)
            view.add_item(next_button)
            return view

        embed = discord.Embed(
            title=f"Welcome Channel for {ctx.guild.name}",
            description=f"Current Welcome Channel: {welcome_channel.mention if welcome_channel else 'None'}",
            color=0xFF0000
        )
        embed.set_footer(text="Use the dropdown menu to select a channel. Navigate pages if needed.")

        await ctx.send(embed=embed, view=generate_view(current_page))



    @greet.command(name="test", help="Sends a test welcome message to preview the setup.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_test(self, ctx):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT welcome_type, welcome_message, channel_id, embed_data FROM welcome WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()

        if row is None:
            error = discord.Embed(description=f"No welcome message has been set for {ctx.guild.name}! Please set a welcome message first using `{ctx.prefix}greet setup`", color=0xFF0000)
            error.set_author(name="Greet is not configured!", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            await ctx.send(embed=error)
            return

        welcome_type, welcome_message, channel_id, embed_data = row
        welcome_channel = self.bot.get_channel(channel_id)

        if not welcome_channel:
            error2 = discord.Embed(description=f"Welcome channel not set or invalid. Use `{ctx.prefix}greet channel` to set one.", color=0xFF0000)
            error2.set_author(name="Channel not set", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            await ctx.send(embed=error2)
            return

        placeholders = {
            "user": ctx.author.mention,
            "user_avatar": ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url,
            "user_name": ctx.author.name,
            "user_id": ctx.author.id,
            "user_nick": ctx.author.display_name,
            "user_joindate": ctx.author.joined_at.strftime("%a, %b %d, %Y"),
            "user_createdate": ctx.author.created_at.strftime("%a, %b %d, %Y"),
            "server_name": ctx.guild.name,
            "server_id": ctx.guild.id,
            "server_membercount": ctx.guild.member_count,
            "server_icon": ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png",
            "timestamp": discord.utils.format_dt(ctx.message.created_at)
        }

        def safe_format(text):
            placeholders_lower = {k.lower(): v for k, v in placeholders.items()}  

            def replace_var(match):
                var_name = match.group(1).lower()  
                return str(placeholders_lower.get(var_name, f"{{{var_name}}}"))

            return re.sub(r"\{(\w+)\}", replace_var, text or "")
            

        if welcome_type == "simple" and welcome_message:
            await welcome_channel.send(safe_format(welcome_message))

        elif welcome_type == "embed" and embed_data:
            try:
                embed_info = json.loads(embed_data) 
                color_value = embed_info.get("color", None)

                
                embed_color = 0x2f3136

                
                if color_value and isinstance(color_value, str) and color_value.startswith("#"):
                    embed_color = discord.Color(int(color_value.lstrip("#"), 16))
                elif isinstance(color_value, int): 
                    embed_color = discord.Color(color_value)

            except (ValueError, SyntaxError, json.JSONDecodeError):
                await ctx.send("Invalid embed data format. Please reconfigure.")
                return

            content = safe_format(embed_info.get("message", "")) or None
            embed = discord.Embed(
                title=safe_format(embed_info.get("title", "")),
                description=safe_format(embed_info.get("description", "")),
                color=embed_color
            )
            embed.timestamp = discord.utils.utcnow()


            if embed_info.get("footer_text"):
                embed.set_footer(
                    text=safe_format(embed_info["footer_text"]),
                    icon_url=safe_format(embed_info.get("footer_icon", ""))
                )
            if embed_info.get("author_name"):
                embed.set_author(
                    name=safe_format(embed_info["author_name"]),
                    icon_url=safe_format(embed_info.get("author_icon", ""))
                )
            if embed_info.get("thumbnail"):
                embed.set_thumbnail(url=safe_format(embed_info["thumbnail"]))
            if embed_info.get("image"):
                embed.set_image(url=safe_format(embed_info["image"]))

            await welcome_channel.send(content=content, embed=embed)



    @greet.command(name="config", help="Shows the current welcome configuration.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_config(self, ctx):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT * FROM welcome WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()

        if row:
            _, welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration = row
            response_type = "Simple" if welcome_type == "simple" else "Embed"

            embed = discord.Embed(
                title=f"Greet Configuration for {ctx.guild.name}",
                color=0xFF0000
            )

            embed.add_field(name="Response Type", value=response_type, inline=False)

            if welcome_type == "simple":
                details = f"Message Content: {welcome_message or 'None'}"
                embed.add_field(name="Details", value=details[:1024], inline=False)
            else:
                embed_details = json.loads(embed_data) if embed_data else {}
                formatted_embed_data = "\n".join(
                    f"{key.replace('_', ' ').title()}: {value or 'None'}" for key, value in embed_details.items()
                ) or "None"

                for i, chunk in enumerate([formatted_embed_data[i:i+1024] for i in range(0, len(formatted_embed_data), 1024)]):
                    embed.add_field(name=f"Embed Data Part {i+1}", value=chunk, inline=False)

            greet_channel = self.bot.get_channel(channel_id)
            channel_display = greet_channel.mention if greet_channel else "None"
            auto_delete_duration = f"{auto_delete_duration} seconds" if auto_delete_duration else "None"

            embed.add_field(name="Greet Channel", value=channel_display, inline=False)
            embed.add_field(name="Auto Delete Duration", value=auto_delete_duration, inline=False)
            await ctx.send(embed=embed)
        else:
            error = discord.Embed(
                description=f"No welcome message has been set for {ctx.guild.name}! Please set a welcome message first using `{ctx.prefix}greet setup`",
                color=0xFF0000
            )
            error.set_author(name="Greet is not configured!", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            await ctx.send(embed=error)


    @greet.command(name="autodelete", aliases=["autodel"], help="Sets the auto-delete duration for the welcome message.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_autodelete(self, ctx, time: str):
        
        if time.endswith("s"):
            seconds = int(time[:-1])
            if 3 <= seconds <= 300:
                auto_delete_duration = seconds
            else:
                await ctx.send("Auto delete time should be between 3 seconds and 300 seconds.")
                return
        elif time.endswith("m"):
            minutes = int(time[:-1])
            if 1 <= minutes <= 5:
                auto_delete_duration = minutes * 60  
            else:
                await ctx.send("Auto delete time should be between 1 minute and 5 minutes.")
                return
        else:
            await ctx.send("Invalid time format. Please use 's' for seconds and 'm' for minutes.")
            return

        
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("""
            UPDATE welcome
            SET auto_delete_duration = ?
            WHERE guild_id = ?
            """, (auto_delete_duration, ctx.guild.id))
            await db.commit()

        await ctx.send(f"{ZTICK} Auto delete duration has been set to **{auto_delete_duration}** seconds.")



    @greet.command(name="edit", help="Edits the current welcome message settings for the server.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_edit(self, ctx):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT welcome_type, welcome_message, embed_data FROM welcome WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()

        if row is None:
            error = discord.Embed(description=f"No welcome message has been set for {ctx.guild.name}! Please set a welcome message first using `{ctx.prefix}greet setup`", color=0xFF0000)
            error.set_author(name="Greet is not configured!", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            await ctx.send(embed=error)
            return

        welcome_type, welcome_message, embed_data = row

        cancel_flag = False  

        if welcome_type == "simple":
            embed = discord.Embed(
                title="Edit Welcome Message",
                description=f"**Response Type:** Simple\n**Message Content:** {welcome_message or 'None'}",
                color=0xFF0000
            )
            edit_button = Button(label="Edit", style=discord.ButtonStyle.primary)
            cancel_button = Button(label="Cancel", style=discord.ButtonStyle.danger)

            async def cancel_button_callback(interaction):
                nonlocal cancel_flag
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to cancel the setup.", ephemeral=True)
                    return
                await interaction.response.send_message("Setup has been canceled.", ephemeral=True)
                cancel_flag = True  
                view.clear_items()  
                await interaction.message.edit(embed=embed, view=view)

            cancel_button.callback = cancel_button_callback

            async def edit_button_callback(interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to edit the welcome message.", ephemeral=True)
                    return

                await interaction.response.send_message("Please provide the new welcome message:", ephemeral=True)
                try:
                    new_message = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                        timeout=600
                    )
                    if cancel_flag:  
                        await ctx.send("Setup was canceled. No changes were made.")
                        return
                    await new_message.delete()
                    async with aiosqlite.connect("db/welcome.db") as db:
                        await db.execute("UPDATE welcome SET welcome_message = ? WHERE guild_id = ?", (new_message.content, ctx.guild.id))
                        await db.commit()

                    embed.description = f"**Response Type:** Simple\n**Message Content:** {new_message.content}"
                    edit_button.disabled = True
                    cancel_button.disabled = True
                    await interaction.message.edit(embed=embed, view=view)
                    await ctx.send("Welcome message has been successfully updated.")
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond.")
                except Exception as e:
                    await ctx.send(f"An error occurred: {e}")

            edit_button.callback = edit_button_callback
            view = View()
            view.add_item(edit_button)
            view.add_item(VariableButton(ctx.author))
            view.add_item(cancel_button)
            
            await ctx.send(embed=embed, view=view)

        elif welcome_type == "embed":
            embed_data_json = json.loads(embed_data) if embed_data else {}
            formatted_embed_data = "\n".join(
                f"{key.replace('_', ' ').title()}: {value or 'None'}" for key, value in embed_data_json.items()
            ) or "None"
            embed = discord.Embed(
                title="Edit Welcome Message",
                description=f"**Response Type:** Embed\n**Embed Data:**\n```{formatted_embed_data}```",
                color=0xFF0000
            )

            select_menu = Select(
                placeholder="Select an embed field to edit",
                options=[
                    discord.SelectOption(label=field.replace('_', ' ').title(), value=field)
                    for field in embed_data_json.keys()
                ]
            )

            cancel_button = Button(label="Cancel", style=discord.ButtonStyle.danger)

            async def cancel_button_callback(interaction):
                nonlocal cancel_flag
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to cancel the setup.", ephemeral=True)
                    return
                await interaction.response.send_message("Setup has been canceled.", ephemeral=True)
                cancel_flag = True  
                view.clear_items()  
                await interaction.message.edit(embed=embed, view=view)

            cancel_button.callback = cancel_button_callback

            async def select_callback(interaction):
                nonlocal cancel_flag
                if interaction.user != ctx.author:
                    await interaction.response.send_message("You are not authorized to edit this embed.", ephemeral=True)
                    return

                selected_option = select_menu.values[0]
                await interaction.response.defer()

                while not cancel_flag:  
                    try:
                        if selected_option == "message":
                            await ctx.send("Enter the welcome message content:")
                            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                            embed_data_json["message"] = msg.content

                        elif selected_option == "title":
                            await ctx.send("Enter the embed title:")
                            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                            embed_data_json["title"] = msg.content

                        elif selected_option == "description":
                            await ctx.send("Enter the embed description:")
                            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                            embed_data_json["description"] = msg.content

                        elif selected_option == "color":
                            await ctx.send("Enter a hex color (e.g., #3498db or 3498db):")
                            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                            color_code = msg.content.lstrip("#")
                            if all(c in "0123456789abcdefABCDEF" for c in color_code) and len(color_code) in {3, 6}:
                                embed_data_json["color"] = int(color_code.lstrip("#"), 16)
                            else:
                                await ctx.send("Invalid color code. Please enter a valid hex color.")
                                continue  

                        elif selected_option in ["footer_text", "footer_icon", "author_name", "author_icon", "thumbnail", "image"]:
                            await ctx.send(f"Enter the URL or text for {selected_option.replace('_', ' ')}:")
                            msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                            url_or_text = msg.content
                            if selected_option in ["footer_icon", "author_icon", "thumbnail", "image"]:
                                if url_or_text.startswith("http") or url_or_text in ["{user_avatar}", "{server_icon}"]:
                                    embed_data_json[selected_option] = url_or_text
                                else:
                                    await ctx.send("Invalid URL. Please enter a valid image URL or a supported placeholder ({user_avatar} or {server_icon}).")
                                    continue  
                            else:
                                embed_data_json[selected_option] = url_or_text

                        async with aiosqlite.connect("db/welcome.db") as db:
                            await db.execute("UPDATE welcome SET embed_data = ? WHERE guild_id = ?", (json.dumps(embed_data_json), ctx.guild.id))
                            await db.commit()

                        embed.description = f"**Response Type:** Embed\n**Embed Data:**\n```{json.dumps(embed_data_json, indent=4)}```"
                        await interaction.message.edit(embed=embed, view=None)
                        await ctx.send("Embed data has been successfully updated.")
                        break 
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long to respond.")
                        break
                    except Exception as e:
                        await ctx.send(f"An error occurred: {e}")
                        break

            select_menu.callback = select_callback
            view = View()
            view.add_item(select_menu)
            view.add_item(VariableButton(ctx.author))
            view.add_item(cancel_button)
            
            await ctx.send(embed=embed, view=view)


