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
import discord
from utils.emoji import CROSS, TICK
from discord.ext import commands
from discord import ui
import asyncio
from utils.Tools import *
import re


class EmbedBuilder(ui.LayoutView):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.message = None
        self.embed_data = {
            "title": "Edit your Embed!",
            "description": "Select Options from the menu below to customize.",
            "color": 0xFF0000,
            "thumbnail": None,
            "image": None,
            "footer_text": None,
            "footer_icon": None,
            "author_text": None,
            "author_icon": None,
            "fields": []
        }
        self.container = ui.Container(accent_color=None)
        self._build_view()
        self.add_item(self.container)

    def _get_preview(self):
        d = self.embed_data
        lines = []
        if d["title"]:
            lines.append(f"**Title:** {d['title']}")
        if d["description"]:
            lines.append(f"**Description:** {d['description']}")
        if d["color"]:
            lines.append(f"**Color:** `#{d['color']:06X}`")
        if d["thumbnail"]:
            lines.append(f"**Thumbnail:** [Set]({d['thumbnail']})")
        if d["image"]:
            lines.append(f"**Image:** [Set]({d['image']})")
        if d["footer_text"]:
            lines.append(f"**Footer:** {d['footer_text']}")
        if d["footer_icon"]:
            lines.append(f"**Footer Icon:** [Set]({d['footer_icon']})")
        if d["author_text"]:
            lines.append(f"**Author:** {d['author_text']}")
        if d["author_icon"]:
            lines.append(f"**Author Icon:** [Set]({d['author_icon']})")
        if d["fields"]:
            for i, f in enumerate(d["fields"]):
                lines.append(f"**Field {i+1}:** {f['name']} — {f['value']}")
        return "\n".join(lines) if lines else "No properties set yet."

    def _build_view(self):
        self.container.clear_items()

        self.container.add_item(ui.TextDisplay("# Embed Builder"))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay(self._get_preview()))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay("*Select an option to edit. Respond within 30 seconds.*"))

        # Select menu
        select = ui.Select(
            placeholder="Choose an option to edit the Embed",
            min_values=1, max_values=1,
            options=[
                discord.SelectOption(label="Title", description="Edit the title"),
                discord.SelectOption(label="Description", description="Edit the description"),
                discord.SelectOption(label="Add Field", description="Add a field"),
                discord.SelectOption(label="Color", description="Edit the color (hex)"),
                discord.SelectOption(label="Thumbnail", description="Set thumbnail URL"),
                discord.SelectOption(label="Image", description="Set image URL"),
                discord.SelectOption(label="Footer Text", description="Edit footer text"),
                discord.SelectOption(label="Footer Icon", description="Set footer icon URL"),
                discord.SelectOption(label="Author Text", description="Edit author text"),
                discord.SelectOption(label="Author Icon", description="Set author icon URL"),
            ]
        )
        select.callback = self._select_callback
        self.container.add_item(ui.ActionRow(select))

        # Buttons
        send_btn = ui.Button(label="Send Embed", emoji=TICK, style=discord.ButtonStyle.success)
        send_btn.callback = self._send_callback
        cancel_btn = ui.Button(label="Cancel Setup", emoji=CROSS, style=discord.ButtonStyle.danger)
        cancel_btn.callback = self._cancel_callback
        self.container.add_item(ui.ActionRow(send_btn, cancel_btn))

    def _build_embed(self):
        """Build a real discord.Embed from stored data"""
        d = self.embed_data
        embed = discord.Embed(
            title=d["title"],
            description=d["description"],
            color=d["color"]
        )
        if d["thumbnail"]:
            embed.set_thumbnail(url=d["thumbnail"])
        if d["image"]:
            embed.set_image(url=d["image"])
        if d["footer_text"] or d["footer_icon"]:
            embed.set_footer(text=d["footer_text"] or "", icon_url=d["footer_icon"] or discord.Embed.Empty)
        if d["author_text"] or d["author_icon"]:
            embed.set_author(name=d["author_text"] or "", icon_url=d["author_icon"] or discord.Embed.Empty)
        for field in d["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=False)
        return embed

    async def _select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This builder doesn't belong to you.", ephemeral=True)
            return
        await interaction.response.defer()

        value = interaction.data["values"][0]

        def chk(m):
            return m.channel.id == self.ctx.channel.id and m.author.id == self.ctx.author.id

        prompts = {
            "Title": "Enter the **Title** of the embed:",
            "Description": "Enter the **Description** of the embed:",
            "Color": "Enter the color as a hex value (e.g., `#FF0000`):",
            "Thumbnail": "Enter the **Thumbnail URL**:",
            "Image": "Enter the **Image URL**:",
            "Footer Text": "Enter the **Footer text**:",
            "Footer Icon": "Enter the **Footer icon URL**:",
            "Author Text": "Enter the **Author text**:",
            "Author Icon": "Enter the **Author icon URL**:",
            "Add Field": "Enter the **Field title**:",
        }

        await self.ctx.send(prompts.get(value, "Enter a value:"))

        try:
            msg = await self.ctx.bot.wait_for("message", timeout=30, check=chk)

            if value == "Title":
                self.embed_data["title"] = msg.content
            elif value == "Description":
                self.embed_data["description"] = msg.content
            elif value == "Color":
                try:
                    self.embed_data["color"] = int(msg.content.strip("#"), 16)
                except ValueError:
                    await self.ctx.send("Invalid hex color. Please try again.")
                    return
            elif value == "Thumbnail":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Invalid URL format.")
                    return
                self.embed_data["thumbnail"] = msg.content
            elif value == "Image":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Invalid URL format.")
                    return
                self.embed_data["image"] = msg.content
            elif value == "Footer Text":
                self.embed_data["footer_text"] = msg.content
            elif value == "Footer Icon":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Invalid URL format.")
                    return
                self.embed_data["footer_icon"] = msg.content
            elif value == "Author Text":
                self.embed_data["author_text"] = msg.content
            elif value == "Author Icon":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Invalid URL format.")
                    return
                self.embed_data["author_icon"] = msg.content
            elif value == "Add Field":
                field_name = msg.content
                await self.ctx.send("Enter the **Field value**:")
                val_msg = await self.ctx.bot.wait_for("message", timeout=30, check=chk)
                self.embed_data["fields"].append({"name": field_name, "value": val_msg.content})

            # Rebuild and update
            self._build_view()
            await self.message.edit(view=self)

        except asyncio.TimeoutError:
            await self.ctx.send("Timed Out.")

    async def _send_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This builder doesn't belong to you.", ephemeral=True)
            return
        await interaction.response.defer()

        await self.ctx.send("Mention the **channel** where you want to send this embed:")

        def chk(m):
            return m.channel.id == self.ctx.channel.id and m.author.id == self.ctx.author.id

        try:
            msg = await self.ctx.bot.wait_for("message", timeout=30, check=chk)
            chnl = msg.channel_mentions[0]
            embed = self._build_embed()
            await chnl.send(embed=embed)

            # Show success
            self.container.clear_items()
            self.container.add_item(ui.TextDisplay(f"# {TICK} Embed Sent"))
            self.container.add_item(ui.Separator())
            self.container.add_item(ui.TextDisplay(f"Successfully sent the embed to {chnl.mention}"))
            await self.message.edit(view=self)

        except asyncio.TimeoutError:
            await self.ctx.send("Timed Out.")
        except (IndexError, AttributeError):
            await self.ctx.send("Please mention a valid channel.")

    async def _cancel_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This builder doesn't belong to you.", ephemeral=True)
            return
        self.container.clear_items()
        self.container.add_item(ui.TextDisplay("# Embed Builder"))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay(f"{CROSS} Embed setup cancelled."))
        await interaction.response.edit_message(view=self)
        self.stop()

    async def on_timeout(self):
        try:
            self.container.clear_items()
            self.container.add_item(ui.TextDisplay("# Embed Builder"))
            self.container.add_item(ui.Separator())
            self.container.add_item(ui.TextDisplay("⏰ Builder timed out. Use the command again."))
            await self.message.edit(view=self)
        except:
            pass


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="embed")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def _embed(self, ctx):
        view = EmbedBuilder(ctx)
        view.message = await ctx.send(view=view)