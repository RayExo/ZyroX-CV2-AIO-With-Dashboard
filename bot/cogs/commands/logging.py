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
from discord.ext import commands
from discord.ui import View, Select, Button
import logging
import time
import asyncio
import aiofiles
import json
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import os
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


LOG_CATEGORIES = [
    "message_events",
    "join_leave_events",
    "member_moderation",
    "voice_events",
    "channel_events",
    "role_events",
    "emoji_events",
    "reaction_events",
    "system_events",
]

CONFIG_FILE = "jsondb/logging_config.json"
LOGS_DIR = "logs"
MAX_AUDIT_CACHE_SIZE = 1000
AUDIT_CACHE_TTL = 300
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024
MAX_SEARCH_RESULTS = 100


Path(LOGS_DIR).mkdir(exist_ok=True)

from utils.cv2 import CV2, build_container
from discord.ui import TextDisplay, Separator, ActionRow, LayoutView, Container, Select


class LogSetupLayoutView(LayoutView):
    def __init__(self, bot, author, categories):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.categories = categories
        self.selected_channels = {cat: None for cat in LOG_CATEGORIES}

        self.select = Select(
            placeholder="Choose a logging category to configure...",
            options=[
                discord.SelectOption(
                    label=cat.replace("_", " ").title(),
                    value=cat,
                    description=f"Configure {cat.replace('_', ' ').lower()} logging",
                )
                for cat in LOG_CATEGORIES
            ],
        )
        self.select.callback = self.category_select_callback

        self.add_item(
            Container(
                TextDisplay("**Logging Setup**"),
                Separator(visible=True),
                TextDisplay(
                    f"Configure logging channels for different event categories.\n\nGuild ID: {author.guild.id}"
                ),
                ActionRow(self.select),
            )
        )

    async def category_select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "Only the command author can interact.", ephemeral=True
            )
            return

        category = interaction.data.get("values", [None])[0]
        if not category:
            return

        cog = self.bot.get_cog("Logging")
        if not cog:
            await interaction.response.send_message(
                "Logging cog not found.", ephemeral=True
            )
            return

        channel_view = ChannelSelectView(self.bot, self.author, category, None, None)

        layout_view = CV2(
            f"Select Channel for {category.replace('_', ' ').title()}",
            f"Choose where to log {category.replace('_', ' ').lower()} events.\n\nPage 1 of {channel_view.total_pages}",
        )

        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if channel_view.children:
                    add_action_rows(container, channel_view.children)
                break

        await interaction.response.edit_message(view=layout_view)

    @discord.ui.button(label="Finish Setup", style=discord.ButtonStyle.success)
    async def finish_button(self, interaction: discord.Interaction, button: Button):
        await self.finish_setup(interaction)

    async def finish_setup(self, interaction: discord.Interaction):
        try:
            log_enabled = {
                cat: bool(self.selected_channels.get(cat)) for cat in LOG_CATEGORIES
            }

            cog = self.bot.get_cog("Logging")
            if not cog:
                await interaction.response.send_message(
                    "Logging cog not found.", ephemeral=True
                )
                return

            await cog._save_log_config(
                interaction.guild.id,
                self.selected_channels,
                log_enabled,
                [],
                [],
                [],
                None,
            )

            configured_count = sum(
                1 for ch in self.selected_channels.values() if ch is not None
            )
            layout_view = CV2(
                "Setup Complete",
                f"Logging has been configured successfully.\n\n**Configuration Summary**\nConfigured {configured_count} out of {len(LOG_CATEGORIES)} categories",
            )

            for item in self.children:
                if hasattr(item, "disabled"):
                    item.disabled = True

            await interaction.response.edit_message(view=layout_view)
        except Exception as e:
            logger.error(f"Error finishing setup: {e}")
            pass


class CV2EmbedAdapter(CV2):
    def __init__(self, t, d="", **kwargs):
        self._title = t
        self._description = d or ""
        self._fields = []
        self._footer = None
        super().__init__(t, self._description)
        self.color = kwargs.get("color", 0xFF0000)

    def _rebuild(self):
        self.clear_items()
        sections = [self._description] if self._description else []
        for name, value in self._fields:
            sections.append(f"**{name}**\n{value}")

        if self._footer:
            sections.append(f"*{self._footer}*")

        container = build_container(
            TextDisplay(f"**{self._title}**"),
            *[
                item
                for s in sections
                for item in (Separator(visible=True), TextDisplay(str(s)))
            ],
        )
        self.add_item(container)

    def add_field(self, name, value, inline=False, **kwargs):
        self._fields.append((name, value))
        self._rebuild()
        return self

    def set_footer(self, text=None, icon_url=None, **kwargs):
        if text:
            self._footer = text
            self._rebuild()
        return self

    def set_thumbnail(self, url=None, **kwargs):
        return self

    def set_author(self, name=None, url=None, icon_url=None, **kwargs):
        return self

    def set_image(self, url=None, **kwargs):
        return self

    def to_dict(self):
        return {"title": self._title, "description": self._description}


def add_action_rows(container, components):
    from discord.ui import ActionRow

    current_row = []
    for item in components:
        # Check if it's a select menu or any other full-width component. Select Menu is type 3.
        # ChannelSelect is 8, RoleSelect is 6, UserSelect is 5, MentionableSelect is 7, Text Input is 4.
        # Generally, anything other than Button (type 2) takes a full row.
        if getattr(item, "type", None) and item.type.value != 2:
            if current_row:
                container.add_item(ActionRow(*current_row))
                current_row = []
            container.add_item(ActionRow(item))
        else:
            current_row.append(item)
            if len(current_row) == 5:
                container.add_item(ActionRow(*current_row))
                current_row = []
    if current_row:
        container.add_item(ActionRow(*current_row))


class LogSetupView(View):
    """Enhanced view for configuring logging settings with improved UI."""

    def __init__(self, bot: commands.Bot, author: discord.Member, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author = author
        self.selected_channels: Dict[str, Optional[int]] = {
            cat: None for cat in LOG_CATEGORIES
        }
        self.message: Optional[discord.Message] = None
        self.current_step = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command author can interact."""
        if interaction.user != self.author:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "Only the command author can interact with this menu.",
                        ephemeral=True,
                    )
            except (discord.NotFound, discord.HTTPException):
                pass
            return False
        return True

    async def on_timeout(self):
        """Handle view timeout with proper cleanup."""
        if self.message:
            try:
                for item in self.children:
                    item.disabled = True
                await self.message.edit(view=self)
                logger.info(
                    f"Log setup timed out for {self.author} in {self.author.guild.name}"
                )
            except (discord.NotFound, discord.HTTPException):
                try:
                    await self.message.delete()
                except:
                    pass

    @discord.ui.select(placeholder="Choose a logging category to configure...")
    async def category_select(self, interaction: discord.Interaction, select: Select):
        """Handle category selection in setup."""
        try:
            if select.values[0] == "finish":
                await self.finish_setup(interaction)
                return

            category = select.values[0]
            guild = interaction.guild

            channel_view = ChannelSelectView(self.bot, self.author, category, self)

            from utils.cv2 import CV2
            from discord.ui import ActionRow

            layout_view = CV2(
                f"Select Channel for {category.replace('_', ' ').title()}",
                f"Choose where to log {category.replace('_', ' ').lower()} events.\n\n**Page 1 of {channel_view.total_pages}** - Showing {len(channel_view.all_channels[: channel_view.channels_per_page])} channels",
            )
            for container in layout_view.children:
                if type(container).__name__ == "Container":
                    if channel_view.children:
                        add_action_rows(container, channel_view.children)
                    break
            await interaction.response.edit_message(embed=None, view=layout_view)
        except Exception as e:
            logger.error(f"Error in category selection: {e}")
            pass

    @discord.ui.button(label="Finish Setup", style=discord.ButtonStyle.success)
    async def finish_button(self, interaction: discord.Interaction, button: Button):
        """Finish the setup process."""
        await self.finish_setup(interaction)

    async def finish_setup(self, interaction: discord.Interaction):
        """Complete the setup process."""
        try:
            log_enabled = {
                cat: bool(self.selected_channels.get(cat)) for cat in LOG_CATEGORIES
            }

            cog = self.bot.get_cog("Logging")
            if not cog:
                await interaction.response.send_message(
                    "Logging cog not found.", ephemeral=True
                )
                return

            await cog._save_log_config(
                interaction.guild.id,
                self.selected_channels,
                log_enabled,
                [],
                [],
                [],
                None,
            )

            from utils.cv2 import CV2
            from discord.ui import ActionRow

            configured_count = sum(
                1 for ch in self.selected_channels.values() if ch is not None
            )
            layout_view = CV2(
                "Setup Complete",
                "Logging has been configured successfully.",
                f"**Configuration Summary**\nConfigured {configured_count} out of {len(LOG_CATEGORIES)} categories\n\n*Use /log status to view your configuration*",
            )

            for item in self.children:
                item.disabled = True

            for container in layout_view.children:
                if type(container).__name__ == "Container":
                    if self.children:
                        add_action_rows(container, self.children)
                    break
            await interaction.response.edit_message(embed=None, view=layout_view)

        except Exception as e:
            logger.error(f"Error finishing setup: {e}")
            try:
                pass
            except:
                pass


class InteractiveConfigView(View):
    """Fully interactive configuration view for all logging settings."""

    def __init__(self, bot: commands.Bot, author: discord.Member, config: Dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.config = config
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command author can interact."""
        if interaction.user != self.author:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "Only the command author can interact with this menu.",
                        ephemeral=True,
                    )
            except (discord.NotFound, discord.HTTPException):
                pass
            return False
        return True

    @discord.ui.button(label="Change Channels", style=discord.ButtonStyle.primary)
    async def change_channels(self, interaction: discord.Interaction, button: Button):
        """Open channel configuration menu."""
        view = ChannelConfigView(self.bot, self.author, self.config)
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Channel Configuration",
            "Select a category to change its log channel.",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if view.children:
                    add_action_rows(container, view.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    @discord.ui.button(label="Toggle Categories", style=discord.ButtonStyle.secondary)
    async def toggle_categories(self, interaction: discord.Interaction, button: Button):
        """Open category toggle menu."""
        view = CategoryToggleView(self.bot, self.author, self.config)
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Toggle Categories",
            "Enable or disable logging categories.",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if view.children:
                    add_action_rows(container, view.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    @discord.ui.button(label="Manage Ignores", style=discord.ButtonStyle.secondary)
    async def manage_ignores(self, interaction: discord.Interaction, button: Button):
        """Open ignore management menu."""
        view = IgnoreManagementView(self.bot, self.author, self.config)
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Ignore Management",
            "Manage ignored channels, roles, and users.",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if view.children:
                    add_action_rows(container, view.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    @discord.ui.button(
        label="Auto-Delete Settings", style=discord.ButtonStyle.secondary
    )
    async def auto_delete_settings(
        self, interaction: discord.Interaction, button: Button
    ):
        """Configure auto-delete duration."""
        view = AutoDeleteView(self.bot, self.author, self.config)
        current_duration = self.config.get("auto_delete_duration")
        current_text = {
            None: "Disabled",
            3600: "1 Hour",
            86400: "24 Hours",
            604800: "7 Days",
        }.get(current_duration, f"{current_duration} seconds")

        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Auto-Delete Settings",
            f"Current Setting: {current_text}",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if view.children:
                    add_action_rows(container, view.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)


class ChannelConfigView(View):
    """View for configuring log channels."""

    def __init__(self, bot: commands.Bot, author: discord.Member, config: Dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.config = config
        self.add_item(self.create_category_select())

    def create_category_select(self) -> Select:
        """Create select menu for category selection."""
        options = []
        log_channels = self.config.get("log_channels", {})

        for category in LOG_CATEGORIES:
            channel_id = log_channels.get(category)
            channel = self.author.guild.get_channel(channel_id) if channel_id else None
            description = f"Currently: {channel.name}" if channel else "Not configured"

            options.append(
                discord.SelectOption(
                    label=category.replace("_", " ").title(),
                    value=category,
                    description=description[:100],
                )
            )

        select = Select(placeholder="Select category to configure...", options=options)
        select.callback = self.category_select_callback
        return select

    async def category_select_callback(self, interaction: discord.Interaction):
        """Handle category selection."""
        category = interaction.data["values"][0]
        view = ChannelSelectView(self.bot, self.author, category, None, self.config)

        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            f"Select Channel for {category.replace('_', ' ').title()}",
            f"Choose where to log {category.replace('_', ' ').lower()} events.\n\n**Page 1 of {view.total_pages}** - Showing {len(view.all_channels[: view.channels_per_page])} channels",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if view.children:
                    add_action_rows(container, view.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)


class CategoryToggleView(View):
    """View for toggling categories."""

    def __init__(self, bot: commands.Bot, author: discord.Member, config: Dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.config = config
        self.add_item(self.create_toggle_select())

    def create_toggle_select(self) -> Select:
        """Create select menu for toggling categories."""
        options = []
        log_enabled = self.config.get("log_enabled", {})

        for category in LOG_CATEGORIES:
            enabled = log_enabled.get(category, False)
            status = "Enabled" if enabled else "Disabled"

            options.append(
                discord.SelectOption(
                    label=category.replace("_", " ").title(),
                    value=category,
                    description=f"Currently: {status}",
                )
            )

        select = Select(placeholder="Select category to toggle...", options=options)
        select.callback = self.toggle_callback
        return select

    async def toggle_callback(self, interaction: discord.Interaction):
        """Handle category toggle."""
        category = interaction.data["values"][0]
        log_enabled = self.config.get("log_enabled", {})
        current_state = log_enabled.get(category, False)
        new_state = not current_state
        log_enabled[category] = new_state

        cog = self.bot.get_cog("Logging")
        await cog._save_log_config(
            interaction.guild.id,
            self.config.get("log_channels", {}),
            log_enabled,
            self.config.get("ignore_channels", []),
            self.config.get("ignore_roles", []),
            self.config.get("ignore_users", []),
            self.config.get("auto_delete_duration"),
        )

        self.config["log_enabled"] = log_enabled

        status = "enabled" if new_state else "disabled"
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        self.clear_items()
        self.add_item(self.create_toggle_select())
        layout_view = CV2(
            "Category Updated",
            f"{category.replace('_', ' ').title()} logging has been {status}.",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)


class IgnoreManagementView(View):
    """View for managing ignore lists."""

    def __init__(self, bot: commands.Bot, author: discord.Member, config: Dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.config = config

    @discord.ui.button(label="View Ignored", style=discord.ButtonStyle.secondary)
    async def view_ignored(self, interaction: discord.Interaction, button: Button):
        """Show current ignore lists."""
        ignore_channels = self.config.get("ignore_channels", [])
        ignore_roles = self.config.get("ignore_roles", [])
        ignore_users = self.config.get("ignore_users", [])

        channels_text = (
            "\n".join(
                [
                    f"<#{cid}>"
                    for cid in ignore_channels
                    if interaction.guild.get_channel(cid)
                ]
            )
            or "None"
        )
        roles_text = (
            "\n".join(
                [
                    f"<@&{rid}>"
                    for rid in ignore_roles
                    if interaction.guild.get_role(rid)
                ]
            )
            or "None"
        )
        users_text = (
            "\n".join(
                [
                    f"<@{uid}>"
                    for uid in ignore_users
                    if interaction.guild.get_member(uid)
                ]
            )
            or "None"
        )

        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Current Ignore Lists",
            f"**Ignored Channels**\n{channels_text[:1024]}",
            f"**Ignored Roles**\n{roles_text[:1024]}",
            f"**Ignored Users**\n{users_text[:1024]}",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    @discord.ui.button(label="Manage Channels", style=discord.ButtonStyle.primary)
    async def manage_channels(self, interaction: discord.Interaction, button: Button):
        """Manage ignored channels."""
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Manage Ignored Channels",
            "Use /log ignore add channel #channel or /log ignore remove channel #channel",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    @discord.ui.button(label="Manage Roles", style=discord.ButtonStyle.primary)
    async def manage_roles(self, interaction: discord.Interaction, button: Button):
        """Manage ignored roles."""
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Manage Ignored Roles",
            "Use /log ignore add role @role or /log ignore remove role @role",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    @discord.ui.button(label="Manage Users", style=discord.ButtonStyle.primary)
    async def manage_users(self, interaction: discord.Interaction, button: Button):
        """Manage ignored users."""
        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Manage Ignored Users",
            "Use /log ignore add user @user or /log ignore remove user @user",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)


class AutoDeleteView(View):
    """View for configuring auto-delete duration."""

    def __init__(self, bot: commands.Bot, author: discord.Member, config: Dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.config = config
        self.add_item(self.create_duration_select())

    def create_duration_select(self) -> Select:
        """Create select menu for auto-delete duration."""
        options = [
            discord.SelectOption(
                label="Disabled", value="None", description="Never auto-delete logs"
            ),
            discord.SelectOption(
                label="1 Hour", value="3600", description="Delete logs after 1 hour"
            ),
            discord.SelectOption(
                label="24 Hours",
                value="86400",
                description="Delete logs after 24 hours",
            ),
            discord.SelectOption(
                label="7 Days", value="604800", description="Delete logs after 7 days"
            ),
        ]

        select = Select(placeholder="Select auto-delete duration...", options=options)
        select.callback = self.duration_callback
        return select

    async def duration_callback(self, interaction: discord.Interaction):
        """Handle duration selection."""
        duration_str = interaction.data["values"][0]
        duration = None if duration_str == "None" else int(duration_str)

        cog = self.bot.get_cog("Logging")
        await cog._save_log_config(
            interaction.guild.id,
            self.config.get("log_channels", {}),
            self.config.get("log_enabled", {}),
            self.config.get("ignore_channels", []),
            self.config.get("ignore_roles", []),
            self.config.get("ignore_users", []),
            duration,
        )

        self.config["auto_delete_duration"] = duration

        duration_text = {
            None: "Disabled",
            3600: "1 Hour",
            86400: "24 Hours",
            604800: "7 Days",
        }.get(duration, f"{duration} seconds")

        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            "Auto-Delete Updated",
            f"Auto-delete duration set to: {duration_text}",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)


class ChannelSelectView(View):
    """View for selecting channels for specific categories with pagination."""

    def __init__(
        self,
        bot: commands.Bot,
        author: discord.Member,
        category: str,
        parent_view: LogSetupView,
        config: Dict = None,
    ):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.category = category
        self.parent_view = parent_view
        self.config = config
        self.current_page = 0
        self.channels_per_page = 24

        self.all_channels = [
            ch
            for ch in author.guild.text_channels
            if ch.permissions_for(author.guild.me).send_messages
        ]
        self.total_pages = max(
            1,
            (len(self.all_channels) + self.channels_per_page - 1)
            // self.channels_per_page,
        )

        self.add_item(self.create_channel_select())
        if self.total_pages > 1:
            self.add_navigation_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command author can interact."""
        if interaction.user != self.author:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "Only the command author can interact with this menu.",
                        ephemeral=True,
                    )
            except (discord.NotFound, discord.HTTPException):
                pass
            return False
        return True

    def create_channel_select(self) -> Select:
        """Create select menu for channel selection with pagination."""
        start_idx = self.current_page * self.channels_per_page
        end_idx = start_idx + self.channels_per_page
        current_channels = self.all_channels[start_idx:end_idx]

        options = [
            discord.SelectOption(
                label=channel.name[:100],
                value=str(channel.id),
                description=f"#{channel.name} in {channel.category.name if channel.category else 'No Category'}"[
                    :100
                ],
            )
            for channel in current_channels
        ]

        options.append(
            discord.SelectOption(
                label="Skip this category",
                value="skip",
                description="Don't configure this category",
            )
        )

        select = Select(
            placeholder=f"Select channel for {self.category.replace('_', ' ').title()} (Page {self.current_page + 1}/{self.total_pages})",
            options=options,
            custom_id="channel_select",
        )
        select.callback = self.channel_select_callback
        return select

    def add_navigation_buttons(self):
        """Add navigation buttons for pagination."""
        if self.total_pages > 1:
            prev_button = Button(
                label="◀ Previous",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0,
                custom_id="prev_page",
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)

            next_button = Button(
                label="Next ▶",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= self.total_pages - 1,
                custom_id="next_page",
            )
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def previous_page(self, interaction: discord.Interaction):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_view(interaction)

    async def next_page(self, interaction: discord.Interaction):
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        """Update the view with new page content."""
        self.clear_items()
        self.add_item(self.create_channel_select())
        if self.total_pages > 1:
            self.add_navigation_buttons()

        from utils.cv2 import CV2
        from discord.ui import ActionRow

        layout_view = CV2(
            f"Select Channel for {self.category.replace('_', ' ').title()}",
            f"Choose where to log {self.category.replace('_', ' ').lower()} events.\n\n**Page {self.current_page + 1} of {self.total_pages}** - Showing {len(self.all_channels[self.current_page * self.channels_per_page : (self.current_page + 1) * self.channels_per_page])} channels",
            f"Guild ID: {interaction.guild.id}",
        )
        for container in layout_view.children:
            if type(container).__name__ == "Container":
                if self.children:
                    add_action_rows(container, self.children)
                break
        await interaction.response.edit_message(embed=None, view=layout_view)

    async def channel_select_callback(self, interaction: discord.Interaction):
        """Handle channel selection."""
        try:
            select = [item for item in self.children if isinstance(item, Select)][0]

            if self.config:
                if select.values[0] == "skip":
                    channel_id = None
                else:
                    channel_id = int(select.values[0])

                log_channels = self.config.get("log_channels", {})
                if channel_id:
                    log_channels[self.category] = channel_id
                elif self.category in log_channels:
                    del log_channels[self.category]

                cog = self.bot.get_cog("Logging")
                await cog._save_log_config(
                    interaction.guild.id,
                    log_channels,
                    self.config.get("log_enabled", {}),
                    self.config.get("ignore_channels", []),
                    self.config.get("ignore_roles", []),
                    self.config.get("ignore_users", []),
                    self.config.get("auto_delete_duration"),
                )

                self.config["log_channels"] = log_channels

                channel = (
                    interaction.guild.get_channel(channel_id) if channel_id else None
                )
                channel_text = channel.mention if channel else "None"

                config_view = InteractiveConfigView(self.bot, self.author, self.config)
                from utils.cv2 import CV2
                from discord.ui import ActionRow

                layout_view = CV2(
                    "Channel Updated",
                    f"{self.category.replace('_', ' ').title()} logs will be sent to: {channel_text}",
                    f"Guild ID: {interaction.guild.id}",
                )
                for container in layout_view.children:
                    if type(container).__name__ == "Container":
                        if config_view.children:
                            add_action_rows(container, config_view.children)
                        break
                await interaction.response.edit_message(embed=None, view=layout_view)

            else:
                if self.parent_view is None:
                    cog = self.bot.get_cog("Logging")
                    if not cog:
                        await interaction.response.send_message(
                            "Logging cog not found.", ephemeral=True
                        )
                        return

                    channel_id = (
                        None if select.values[0] == "skip" else int(select.values[0])
                    )

                    log_channels = {self.category: channel_id}
                    log_enabled = {cat: bool(channel_id) for cat in LOG_CATEGORIES}

                    await cog._save_log_config(
                        interaction.guild.id,
                        log_channels,
                        log_enabled,
                        [],
                        [],
                        [],
                        None,
                    )

                    channel = (
                        interaction.guild.get_channel(channel_id)
                        if channel_id
                        else None
                    )
                    channel_text = channel.mention if channel else "None"

                    from utils.cv2 import CV2

                    layout_view = CV2(
                        "Channel Updated",
                        f"{self.category.replace('_', ' ').title()} logs will be sent to: {channel_text}",
                        f"Guild ID: {interaction.guild.id}",
                    )
                    await interaction.response.edit_message(view=layout_view)
                else:
                    if select.values[0] == "skip":
                        self.parent_view.selected_channels[self.category] = None
                    else:
                        self.parent_view.selected_channels[self.category] = int(
                            select.values[0]
                        )

                    await self.return_to_setup(interaction)
        except Exception as e:
            logger.error(f"Error in channel selection callback: {e}")
            pass

    @discord.ui.button(label="Back to Setup", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: Button):
        """Return to main setup view."""
        if self.config:
            config_view = InteractiveConfigView(self.bot, self.author, self.config)
            from utils.cv2 import CV2
            from discord.ui import ActionRow

            layout_view = CV2(
                "Logging Configuration",
                "Use the buttons below to modify your logging settings.",
                f"Guild ID: {interaction.guild.id}",
            )
            for container in layout_view.children:
                if type(container).__name__ == "Container":
                    if config_view.children:
                        add_action_rows(container, config_view.children)
                    break
            await interaction.response.edit_message(embed=None, view=layout_view)
        else:
            await self.return_to_setup(interaction)

    async def return_to_setup(self, interaction: discord.Interaction):
        """Return to the main setup view."""
        try:
            embed = CV2EmbedAdapter(
                "Logging Setup",
                "Configure logging channels for different event categories.",
            )

            for category in LOG_CATEGORIES:
                channel_id = self.parent_view.selected_channels.get(category)
                if channel_id:
                    channel = interaction.guild.get_channel(channel_id)
                    status = channel.mention if channel else "Configured"
                else:
                    status = "Not configured"

                embed.add_field(
                    name=category.replace("_", " ").title(), value=status, inline=True
                )

            embed.set_footer(text=f"Guild ID: {interaction.guild.id}")

            options = []
            for category in LOG_CATEGORIES:
                configured = bool(self.parent_view.selected_channels.get(category))
                options.append(
                    discord.SelectOption(
                        label=category.replace("_", " ").title(),
                        value=category,
                        description=f"Configure {category.replace('_', ' ').lower()} logging",
                    )
                )

            options.append(
                discord.SelectOption(
                    label="Finish Setup",
                    value="finish",
                    description="Complete the setup process",
                )
            )

            self.parent_view.category_select.options = options

            from discord.ui import ActionRow

            add_action_rows(embed, self.parent_view.children)

            await interaction.response.edit_message(embed=None, view=embed)
        except Exception as e:
            logger.error(f"Error returning to setup: {e}")
            pass


class Logging(commands.Cog):
    """Comprehensive logging cog with modern UI and expanded event coverage."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_cache: Dict[int, Dict[str, Any]] = {}
        self.audit_cache: Dict[tuple, tuple[Any, float]] = {}
        self.config_lock = asyncio.Lock()
        self.log_queue: Dict[int, List[Dict]] = {}

        asyncio.create_task(self._load_config())

        asyncio.create_task(self._periodic_cache_cleanup())

    async def _periodic_cache_cleanup(self):
        """Periodically clean up audit cache to prevent memory leaks."""
        while True:
            try:
                await asyncio.sleep(AUDIT_CACHE_TTL)
                current_time = time.time()

                expired_keys = [
                    key
                    for key, (_, timestamp) in self.audit_cache.items()
                    if current_time - timestamp > AUDIT_CACHE_TTL
                ]

                for key in expired_keys:
                    del self.audit_cache[key]

                if len(self.audit_cache) > MAX_AUDIT_CACHE_SIZE:
                    sorted_items = sorted(
                        self.audit_cache.items(), key=lambda x: x[1][1]
                    )

                    for key, _ in sorted_items[
                        : len(self.audit_cache) - MAX_AUDIT_CACHE_SIZE
                    ]:
                        del self.audit_cache[key]

                logger.debug(
                    f"Cache cleanup: {len(self.audit_cache)} entries remaining"
                )
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")

    async def _load_config(self):
        """Load configuration from JSON file with error handling."""
        try:
            if os.path.exists(CONFIG_FILE):
                try:
                    async with aiofiles.open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        content = await f.read()
                        if content.strip():
                            data = await asyncio.to_thread(json.loads, content)
                            for guild_id_str, config in data.items():
                                try:
                                    guild_id = int(guild_id_str)

                                    if isinstance(config, dict):
                                        self.config_cache[guild_id] = config
                                except (ValueError, TypeError) as e:
                                    logger.warning(
                                        f"Invalid guild ID or config in file: {guild_id_str}, {e}"
                                    )
                            pass
                        else:
                            pass
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in config file: {e}")

                    backup_file = f"{CONFIG_FILE}.backup.{int(time.time())}"
                    await asyncio.to_thread(os.rename, CONFIG_FILE, backup_file)
                    logger.info(f"Corrupted config backed up to {backup_file}")
            else:
                pass
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config_cache = {}

    async def _save_config(self):
        """Save configuration to JSON file with atomic writes and error handling."""
        async with self.config_lock:
            try:
                data = {
                    str(guild_id): config
                    for guild_id, config in self.config_cache.items()
                }
                content = await asyncio.to_thread(json.dumps, data, indent=2)

                temp_file = f"{CONFIG_FILE}.tmp"
                async with aiofiles.open(temp_file, "w", encoding="utf-8") as f:
                    await f.write(content)

                await asyncio.to_thread(os.replace, temp_file, CONFIG_FILE)
                pass
            except Exception as e:
                logger.error(f"Error saving config: {e}")

                try:
                    if os.path.exists(f"{CONFIG_FILE}.tmp"):
                        await asyncio.to_thread(os.remove, f"{CONFIG_FILE}.tmp")
                except:
                    pass
                raise

    async def _save_log_entry(self, guild_id: int, category: str, log_data: Dict):
        """Save individual log entries to JSON files with size limits and error handling."""
        try:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            log_file = Path(LOGS_DIR) / f"{guild_id}_{category}_{date_str}.json"

            if log_file.exists():
                file_size = log_file.stat().st_size
                if file_size > MAX_LOG_FILE_SIZE:
                    timestamp = datetime.utcnow().strftime("%H%M%S")
                    log_file = (
                        Path(LOGS_DIR)
                        / f"{guild_id}_{category}_{date_str}_{timestamp}.json"
                    )

            logs = []
            if log_file.exists():
                try:
                    async with aiofiles.open(log_file, "r", encoding="utf-8") as f:
                        content = await f.read()
                        if content.strip():
                            logs = await asyncio.to_thread(json.loads, content)
                            if not isinstance(logs, list):
                                logs = []
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning(f"Error reading existing log file {log_file}: {e}")

                    backup_file = f"{log_file}.backup.{int(time.time())}"
                    await asyncio.to_thread(os.rename, log_file, backup_file)

            logs.append(log_data)

            if len(logs) > 1000:
                logs = logs[-1000:]

            temp_file = f"{log_file}.tmp"
            try:
                content = await asyncio.to_thread(
                    json.dumps, logs, indent=2, default=str
                )
                async with aiofiles.open(temp_file, "w", encoding="utf-8") as f:
                    await f.write(content)

                await asyncio.to_thread(os.replace, temp_file, log_file)
            except Exception as e:
                logger.error(f"Error writing log file {log_file}: {e}")

                try:
                    if os.path.exists(temp_file):
                        await asyncio.to_thread(os.remove, temp_file)
                except:
                    pass
                raise

        except Exception as e:
            logger.error(f"Error saving log entry: {e}")

    async def _save_log_config(
        self,
        guild_id: int,
        log_channels: Dict[str, Optional[int]],
        log_enabled: Dict[str, bool],
        ignore_channels: List[int],
        ignore_roles: List[int],
        ignore_users: List[int],
        auto_delete_duration: Optional[int],
    ):
        """Save logging configuration with validation and error handling."""
        try:
            if not isinstance(guild_id, int) or guild_id <= 0:
                raise ValueError(f"Invalid guild_id: {guild_id}")

            if not isinstance(log_channels, dict):
                log_channels = {}

            if not isinstance(log_enabled, dict):
                log_enabled = {}

            ignore_channels = [
                int(x)
                for x in ignore_channels
                if isinstance(x, (int, str)) and str(x).isdigit()
            ]
            ignore_roles = [
                int(x)
                for x in ignore_roles
                if isinstance(x, (int, str)) and str(x).isdigit()
            ]
            ignore_users = [
                int(x)
                for x in ignore_users
                if isinstance(x, (int, str)) and str(x).isdigit()
            ]

            guild = self.bot.get_guild(guild_id)
            if guild:
                ignore_channels = [
                    cid for cid in ignore_channels if guild.get_channel(cid)
                ]
                ignore_roles = [rid for rid in ignore_roles if guild.get_role(rid)]
                ignore_users = [uid for uid in ignore_users if guild.get_member(uid)]

            config = {
                "guild_id": str(guild_id),
                "log_channels": {
                    k: v
                    for k, v in log_channels.items()
                    if v is not None and isinstance(v, int)
                },
                "log_enabled": {k: bool(v) for k, v in log_enabled.items()},
                "ignore_channels": list(set(ignore_channels)),
                "ignore_roles": list(set(ignore_roles)),
                "ignore_users": list(set(ignore_users)),
                "auto_delete_duration": auto_delete_duration
                if isinstance(auto_delete_duration, int)
                else None,
                "last_updated": datetime.utcnow().isoformat(),
            }

            self.config_cache[guild_id] = config
            await self._save_config()
            pass
        except Exception as e:
            logger.error(f"Error saving config for guild {guild_id}: {e}")
            raise

    async def _get_log_config(self, guild_id: int) -> Optional[Dict]:
        """Retrieve logging configuration from cache with validation."""
        try:
            config = self.config_cache.get(guild_id)
            if config and isinstance(config, dict):
                return config
            return None
        except Exception as e:
            logger.error(f"Error retrieving config for guild {guild_id}: {e}")
            return None

    async def _get_audit_log(
        self,
        guild: discord.Guild,
        action: discord.AuditLogAction,
        target_id: Optional[int] = None,
    ) -> Optional[discord.AuditLogEntry]:
        """Fetch audit log entry with caching and proper error handling."""
        if not guild.me.guild_permissions.view_audit_log:
            return None

        cache_key = (guild.id, action.value, target_id)
        if cache_key in self.audit_cache:
            entry, timestamp = self.audit_cache[cache_key]
            if time.time() - timestamp < 10:
                return entry

        try:
            async for entry in guild.audit_logs(limit=5, action=action):
                if target_id is None or (
                    hasattr(entry.target, "id") and entry.target.id == target_id
                ):
                    self.audit_cache[cache_key] = (entry, time.time())
                    return entry
        except (discord.Forbidden, discord.HTTPException, discord.NotFound) as e:
            logger.warning(f"Failed to fetch audit log for guild {guild.id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching audit log: {e}")

        return None

    async def _send_log(
        self,
        guild: discord.Guild,
        category: str,
        embed: discord.Embed,
        channel_id: Optional[int] = None,
        author_id: Optional[int] = None,
    ):
        """Send log embed with comprehensive filtering and error handling."""
        try:
            config = await self._get_log_config(guild.id)
            if not config or not config.get("log_enabled", {}).get(category, False):
                return

            log_channel_id = config.get("log_channels", {}).get(category)
            if not log_channel_id:
                return

            channel = guild.get_channel(log_channel_id)
            if not channel:
                logger.warning(
                    f"Log channel {log_channel_id} not found in guild {guild.id}"
                )
                return

            if not channel.permissions_for(guild.me).send_messages:
                logger.warning(
                    f"No permission to send messages in log channel {log_channel_id}"
                )
                return

            ignore_channels = config.get("ignore_channels", [])
            ignore_roles = config.get("ignore_roles", [])
            ignore_users = config.get("ignore_users", [])
            auto_delete_duration = config.get("auto_delete_duration")

            if author_id and author_id in ignore_users:
                return

            if author_id:
                member = guild.get_member(author_id)
                if member and any(role.id in ignore_roles for role in member.roles):
                    return

            if channel_id and channel_id in ignore_channels:
                return

            embed.color = 0xFF0000

            delete_after = (
                auto_delete_duration
                if auto_delete_duration and auto_delete_duration > 0
                else None
            )
            message = await channel.send(
                view=embed, delete_after=delete_after, allowed_mentions=None
            )

            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "guild_id": guild.id,
                "channel_id": channel_id,
                "author_id": author_id,
                "embed_data": getattr(
                    embed,
                    "to_dict",
                    lambda: {"title": "Log", "description": "CV2 Container"},
                )(),
                "message_id": message.id,
            }
            await self._save_log_entry(guild.id, category, log_data)

            logger.debug(
                f"Sent {category} log to channel {log_channel_id} in guild {guild.id}"
            )
        except discord.Forbidden:
            logger.error(f"Missing permissions to send log to channel {log_channel_id}")
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending log: {e}")
        except Exception as e:
            logger.error(
                f"Failed to send {category} log to channel {log_channel_id}: {e}"
            )

    def _create_modern_embed(
        self, title: str, description: str = None, color: int = 0xFF0000
    ):
        """Create a modern CV2 container representation that supports Embed methods."""
        embed = CV2EmbedAdapter(title, description)
        embed.color = color
        return embed

    def _create_status_embeds(
        self, guild: discord.Guild, config: Dict
    ) -> List[discord.Embed]:
        """Create comprehensive status embeds with minimal styling."""
        embeds = []

        main_embed = self._create_modern_embed(
            "Logging Configuration Status", f"Complete logging setup for {guild.name}"
        )

        log_channels = config.get("log_channels", {})
        log_enabled = config.get("log_enabled", {})

        category_info = {
            "message_events": ("Message Events", "Message edits, deletions"),
            "join_leave_events": ("Join/Leave Events", "Member joins and leaves"),
            "member_moderation": ("Member Moderation", "Bans, timeouts, kicks"),
            "voice_events": ("Voice Events", "Voice channel activity"),
            "channel_events": ("Channel Events", "Channel create/delete/update"),
            "role_events": ("Role Events", "Role create/delete/update"),
            "emoji_events": ("Emoji Events", "Custom emoji changes"),
            "reaction_events": ("Reaction Events", "Message reactions"),
            "system_events": ("System Events", "Server updates"),
        }

        field_count = 0
        for category, (name, desc) in category_info.items():
            if field_count >= 25:
                embeds.append(main_embed)
                main_embed = self._create_modern_embed("Logging Status (Continued)")
                field_count = 0

            channel = (
                guild.get_channel(log_channels.get(category))
                if log_channels.get(category)
                else None
            )
            status = f"{channel.mention if channel else 'Not configured'}"
            status += (
                f" {'(Enabled)' if log_enabled.get(category, False) else '(Disabled)'}"
            )

            main_embed.add_field(name=name, value=status, inline=True)
            field_count += 1

        main_embed.set_footer(text=f"Guild ID: {guild.id}")

        config_embed = self._create_modern_embed("Configuration Details")

        ignore_channels = config.get("ignore_channels", [])
        ignore_roles = config.get("ignore_roles", [])
        ignore_users = config.get("ignore_users", [])
        auto_delete = config.get("auto_delete_duration")

        ignored_ch = [f"<#{cid}>" for cid in ignore_channels if guild.get_channel(cid)]
        config_embed.add_field(
            name="Ignored Channels",
            value=", ".join(ignored_ch[:10])[:1024] if ignored_ch else "None",
            inline=False,
        )

        ignored_roles_mentions = [
            f"<@&{rid}>" for rid in ignore_roles if guild.get_role(rid)
        ]
        config_embed.add_field(
            name="Ignored Roles",
            value=", ".join(ignored_roles_mentions[:10])[:1024]
            if ignored_roles_mentions
            else "None",
            inline=False,
        )

        ignored_users_mentions = [
            f"<@{uid}>" for uid in ignore_users if guild.get_member(uid)
        ]
        config_embed.add_field(
            name="Ignored Users",
            value=", ".join(ignored_users_mentions[:10])[:1024]
            if ignored_users_mentions
            else "None",
            inline=False,
        )

        duration_text = {
            None: "Disabled",
            3600: "1 Hour",
            86400: "24 Hours",
            604800: "7 Days",
        }.get(auto_delete, f"{auto_delete} seconds")

        config_embed.add_field(
            name="Auto-Delete Duration", value=duration_text, inline=True
        )

        last_updated = config.get("last_updated")
        if last_updated:
            try:
                dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                config_embed.add_field(
                    name="Last Updated",
                    value=discord.utils.format_dt(dt, "R"),
                    inline=True,
                )
            except Exception as e:
                pass

        config_embed.set_footer(text=f"Guild ID: {guild.id}")

        embeds.append(main_embed)
        embeds.append(config_embed)
        return embeds

    @commands.hybrid_group(invoke_without_command=True, name="log")
    async def log(self, ctx: commands.Context):
        """Main logging command group. Works with both slash (/) and prefix (!) commands."""

        await ctx.send_help(ctx.command)

    @log.command(
        name="setup", description="Run the interactive setup for logging channels."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.max_concurrency(1, per=commands.BucketType.guild, wait=False)
    async def log_setup(self, ctx: commands.Context):
        """Enhanced interactive setup with improved user experience."""
        try:
            config = await self._get_log_config(ctx.guild.id)
            if config:
                embed = self._create_modern_embed(
                    "Configuration Exists",
                    "Logging is already configured. Use /log config to modify or /log reset to start over.",
                )
                await ctx.send(view=embed, ephemeral=True)
                return

            view = LogSetupLayoutView(self.bot, ctx.author, LOG_CATEGORIES)
            message = await ctx.send(view=view)
        except Exception as e:
            logger.error(f"Error in log setup: {e}")
            embed = self._create_modern_embed(
                "Setup Error", "An error occurred during setup. Please try again."
            )
            await ctx.send(view=embed)

    @log.command(name="status", description="View the current logging configuration.")
    @commands.has_permissions(manage_guild=True)
    async def log_status(self, ctx: commands.Context):
        """Display comprehensive logging status."""
        try:
            config = await self._get_log_config(ctx.guild.id)
            if not config:
                embed = self._create_modern_embed(
                    "No Configuration Found",
                    "Logging is not configured for this server. Use /log setup to get started.",
                    f"Guild ID: {ctx.guild.id}",
                )
                await ctx.send(view=embed)
                return

            embeds = self._create_status_embeds(ctx.guild, config)
            for embed in embeds:
                await ctx.send(view=embed)
        except Exception as e:
            logger.error(f"Error in log status: {e}")
            embed = self._create_modern_embed(
                "Status Error", "An error occurred while retrieving status."
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

    @log.command(
        name="search", description="Search through logged events with filters."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def log_search(
        self,
        ctx: commands.Context,
        user: Optional[discord.Member] = None,
        category: Optional[str] = None,
        hours: Optional[int] = 24,
    ):
        """Search through logs with comprehensive filtering options."""
        try:
            if hours and (hours < 1 or hours > 168):
                embed = self._create_modern_embed(
                    "Invalid Hours", "Hours must be between 1 and 168 (1 week)."
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            if category and category not in LOG_CATEGORIES:
                embed = self._create_modern_embed(
                    "Invalid Category", f"Valid categories: {', '.join(LOG_CATEGORIES)}"
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            await ctx.defer()

            results = []
            search_date = datetime.utcnow() - timedelta(hours=hours or 24)

            for days_back in range((hours or 24) // 24 + 1):
                search_day = search_date + timedelta(days=days_back)
                date_str = search_day.strftime("%Y-%m-%d")

                categories_to_search = [category] if category else LOG_CATEGORIES

                for cat in categories_to_search:
                    base_pattern = f"{ctx.guild.id}_{cat}_{date_str}"
                    log_files = [
                        f
                        for f in Path(LOGS_DIR).iterdir()
                        if f.name.startswith(base_pattern)
                    ]

                    for log_file in log_files:
                        if log_file.exists():
                            try:
                                file_size = await asyncio.to_thread(
                                    log_file.stat().st_size
                                )
                                if file_size > MAX_LOG_FILE_SIZE:
                                    logger.warning(
                                        f"Log file {log_file} is too large to search"
                                    )
                                    continue

                                async with aiofiles.open(
                                    log_file, "r", encoding="utf-8"
                                ) as f:
                                    content = await f.read()
                                    if content.strip():
                                        logs = await asyncio.to_thread(
                                            json.loads, content
                                        )
                                        if isinstance(logs, list):
                                            for log_entry in logs:
                                                if not isinstance(log_entry, dict):
                                                    continue

                                                try:
                                                    log_time = datetime.fromisoformat(
                                                        log_entry["timestamp"].replace(
                                                            "Z", "+00:00"
                                                        )
                                                    )
                                                    if log_time >= search_date:
                                                        if (
                                                            not user
                                                            or log_entry.get(
                                                                "author_id"
                                                            )
                                                            == user.id
                                                        ):
                                                            results.append(log_entry)
                                                            if (
                                                                len(results)
                                                                >= MAX_SEARCH_RESULTS
                                                            ):
                                                                break
                                                except (KeyError, ValueError):
                                                    continue
                            except Exception as e:
                                logger.error(f"Error reading log file {log_file}: {e}")
                                continue

                    if len(results) >= MAX_SEARCH_RESULTS:
                        break
                if len(results) >= MAX_SEARCH_RESULTS:
                    break

            if not results:
                embed = self._create_modern_embed(
                    "No Results Found", "No log entries match your search criteria."
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.followup.send(view=embed)
                return

            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            results = results[:50]

            embed = self._create_modern_embed(
                f"Search Results ({len(results)} found)",
                f"Showing logs from the last {hours} hours",
            )

            if user:
                embed.description += f" for {user.mention}"
            if category:
                embed.description += f" in category {category}"

            for i, result in enumerate(results[:10]):
                try:
                    timestamp = datetime.fromisoformat(
                        result["timestamp"].replace("Z", "+00:00")
                    )
                    category_name = (
                        result.get("category", "Unknown").replace("_", " ").title()
                    )
                    channel_id = result.get("channel_id")
                    channel_text = f"<#{channel_id}>" if channel_id else "Unknown"

                    embed.add_field(
                        name=f"{i + 1}. {category_name}",
                        value=f"{discord.utils.format_dt(timestamp, 'R')} • {channel_text}",
                        inline=False,
                    )
                except Exception as e:
                    continue

            if len(results) > 10:
                embed.set_footer(
                    text=f"Showing 10 of {len(results)} results • Guild ID: {ctx.guild.id}"
                )
            else:
                pass
            await ctx.followup.send(view=embed)

        except Exception as e:
            logger.error(f"Error in log search: {e}")
            embed = self._create_modern_embed(
                "Search Error", "An error occurred while searching logs."
            )
            # embed.set_footer removed - CV2 doesn't support it
            try:
                await ctx.followup.send(view=embed)
            except:
                await ctx.send(view=embed, ephemeral=True)

    @log.command(name="reset", description="Reset all logging configuration.")
    @commands.has_permissions(manage_guild=True)
    async def log_reset(self, ctx: commands.Context):
        """Reset logging configuration for the guild."""
        try:
            if ctx.guild.id in self.config_cache:
                del self.config_cache[ctx.guild.id]
                await self._save_config()

                embed = self._create_modern_embed(
                    "Configuration Reset",
                    "All logging configuration has been cleared. Use /log setup to reconfigure.",
                )
            else:
                embed = self._create_modern_embed(
                    "No Configuration Found",
                    "There is no logging configuration to reset.",
                )

            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)
        except Exception as e:
            logger.error(f"Error in log reset: {e}")
            embed = self._create_modern_embed(
                "Reset Error", "An error occurred while resetting configuration."
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

    @log.command(
        name="toggle", description="Enable or disable specific logging categories."
    )
    @commands.has_permissions(manage_guild=True)
    async def log_toggle(self, ctx: commands.Context, category: str, enabled: bool):
        """Toggle logging categories on/off."""
        try:
            if category not in LOG_CATEGORIES:
                embed = self._create_modern_embed(
                    "Invalid Category", f"Valid categories: {', '.join(LOG_CATEGORIES)}"
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            config = await self._get_log_config(ctx.guild.id)
            if not config:
                embed = self._create_modern_embed(
                    "No Configuration Found",
                    "Please run /log setup first to configure logging.",
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed)
                return

            log_enabled = config.get("log_enabled", {})
            log_enabled[category] = enabled

            await self._save_log_config(
                ctx.guild.id,
                config.get("log_channels", {}),
                log_enabled,
                config.get("ignore_channels", []),
                config.get("ignore_roles", []),
                config.get("ignore_users", []),
                config.get("auto_delete_duration"),
            )

            status = "enabled" if enabled else "disabled"
            embed = self._create_modern_embed(
                f"Category {status.title()}",
                f"{category.replace('_', ' ').title()} logging has been {status}.",
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)
        except Exception as e:
            logger.error(f"Error in log toggle: {e}")
            embed = self._create_modern_embed(
                "Toggle Error", "An error occurred while toggling category."
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

    @log.command(
        name="config", description="Open interactive config menu for logging settings."
    )
    @commands.has_permissions(manage_guild=True)
    async def log_config(self, ctx: commands.Context):
        """Fully interactive configuration menu."""
        try:
            config = await self._get_log_config(ctx.guild.id)
            if not config:
                embed = self._create_modern_embed(
                    "No Configuration Found",
                    "Please run /log setup first to configure logging.",
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed)
                return

            view = InteractiveConfigView(self.bot, ctx.author, config)
            embed = self._create_modern_embed(
                "Logging Configuration",
                "Use the buttons below to modify your logging settings.",
            )

            embed.add_field(
                name="Available Options",
                value=(
                    "Change Channels - Configure log channels for categories\n"
                    "Toggle Categories - Enable/disable logging categories\n"
                    "Manage Ignores - Manage ignore lists\n"
                    "Auto-Delete Settings - Set auto-delete duration"
                ),
                inline=False,
            )

            # embed.set_footer removed - CV2 doesn't support it

            from discord.ui import ActionRow

            add_action_rows(embed, view.children)
            message = await ctx.send(view=embed)
            view.message = message
        except Exception as e:
            logger.error(f"Error in log config: {e}")
            embed = self._create_modern_embed(
                "Config Error", "An error occurred while loading configuration."
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

    @log.command(name="ignore", description="Manage ignored channels, roles, or users.")
    @commands.has_permissions(manage_guild=True)
    async def log_ignore(
        self,
        ctx: commands.Context,
        action: str = "list",
        target_type: str = None,
        target: str = None,
    ):
        """Manage ignore lists."""
        try:
            if action not in ["add", "remove", "list", "clear"]:
                embed = self._create_modern_embed(
                    "Invalid Action", "Valid actions: add, remove, list, clear"
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            config = await self._get_log_config(ctx.guild.id)
            if not config:
                embed = self._create_modern_embed(
                    "No Configuration Found",
                    "Please run /log setup first to configure logging.",
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed)
                return

            if action == "list":
                embed = self._create_modern_embed("Current Ignore Lists")

                ignore_channels = config.get("ignore_channels", [])
                ignore_roles = config.get("ignore_roles", [])
                ignore_users = config.get("ignore_users", [])

                channels_text = (
                    "\n".join(
                        [
                            f"<#{cid}>"
                            for cid in ignore_channels
                            if ctx.guild.get_channel(cid)
                        ]
                    )
                    or "None"
                )
                roles_text = (
                    "\n".join(
                        [
                            f"<@&{rid}>"
                            for rid in ignore_roles
                            if ctx.guild.get_role(rid)
                        ]
                    )
                    or "None"
                )
                users_text = (
                    "\n".join(
                        [
                            f"<@{uid}>"
                            for uid in ignore_users
                            if ctx.guild.get_member(uid)
                        ]
                    )
                    or "None"
                )

                embed.add_field(
                    name="Ignored Channels", value=channels_text[:1024], inline=False
                )
                embed.add_field(
                    name="Ignored Roles", value=roles_text[:1024], inline=False
                )
                embed.add_field(
                    name="Ignored Users", value=users_text[:1024], inline=False
                )
                # embed.set_footer removed - CV2 doesn't support it

                await ctx.send(view=embed)
                return

            if not target_type or not target:
                embed = self._create_modern_embed(
                    "Missing Parameters",
                    f"Usage: /log ignore {action} <channel|role|user> <target>",
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            ignore_channels = config.get("ignore_channels", [])
            ignore_roles = config.get("ignore_roles", [])
            ignore_users = config.get("ignore_users", [])

            target_obj = None
            target_id = None

            if target_type.lower() == "channel":
                if target.startswith("<#") and target.endswith(">"):
                    target_id = int(target[2:-1])
                    target_obj = ctx.guild.get_channel(target_id)
                elif target.isdigit():
                    target_id = int(target)
                    target_obj = ctx.guild.get_channel(target_id)
                else:
                    target_obj = discord.utils.get(ctx.guild.text_channels, name=target)
                    target_id = target_obj.id if target_obj else None

                if not target_obj:
                    embed = self._create_modern_embed(
                        "Channel Not Found", "Could not find the specified channel."
                    )
                    # embed.set_footer removed - CV2 doesn't support it
                    await ctx.send(view=embed, ephemeral=True)
                    return

                target_list = ignore_channels
                target_name = f"#{target_obj.name}"

            elif target_type.lower() == "role":
                if target.startswith("<@&") and target.endswith(">"):
                    target_id = int(target[3:-1])
                    target_obj = ctx.guild.get_role(target_id)
                elif target.isdigit():
                    target_id = int(target)
                    target_obj = ctx.guild.get_role(target_id)
                else:
                    target_obj = discord.utils.get(ctx.guild.roles, name=target)
                    target_id = target_obj.id if target_obj else None

                if not target_obj:
                    embed = self._create_modern_embed(
                        "Role Not Found", "Could not find the specified role."
                    )
                    # embed.set_footer removed - CV2 doesn't support it
                    await ctx.send(view=embed, ephemeral=True)
                    return

                target_list = ignore_roles
                target_name = f"@{target_obj.name}"

            elif target_type.lower() == "user":
                if target.startswith("<@") and target.endswith(">"):
                    target_id = int(target[2:-1].replace("!", ""))
                    target_obj = ctx.guild.get_member(target_id)
                elif target.isdigit():
                    target_id = int(target)
                    target_obj = ctx.guild.get_member(target_id)
                else:
                    target_obj = discord.utils.get(
                        ctx.guild.members, display_name=target
                    )
                    if not target_obj:
                        target_obj = discord.utils.get(ctx.guild.members, name=target)
                    target_id = target_obj.id if target_obj else None

                if not target_obj:
                    embed = self._create_modern_embed(
                        "User Not Found", "Could not find the specified user."
                    )
                    # embed.set_footer removed - CV2 doesn't support it
                    await ctx.send(view=embed, ephemeral=True)
                    return

                target_list = ignore_users
                target_name = f"{target_obj.display_name}"

            else:
                embed = self._create_modern_embed(
                    "Invalid Target Type",
                    "Target type must be 'channel', 'role', or 'user'.",
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            if action == "add":
                if target_id not in target_list:
                    target_list.append(target_id)
                    message = f"Added {target_name} to ignore list."
                else:
                    message = f"{target_name} is already in the ignore list."
            elif action == "remove":
                if target_id in target_list:
                    target_list.remove(target_id)
                    message = f"Removed {target_name} from ignore list."
                else:
                    message = f"{target_name} is not in the ignore list."

            await self._save_log_config(
                ctx.guild.id,
                config.get("log_channels", {}),
                config.get("log_enabled", {}),
                ignore_channels,
                ignore_roles,
                ignore_users,
                config.get("auto_delete_duration"),
            )

            embed = self._create_modern_embed("Ignore List Updated", message)
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

        except Exception as e:
            logger.error(f"Error in log ignore: {e}")
            embed = self._create_modern_embed(
                "Ignore Error", "An error occurred while managing ignore lists."
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

    @log.command(
        name="test", description="Send test log messages to configured channels."
    )
    @commands.has_permissions(manage_guild=True)
    async def log_test(self, ctx: commands.Context, category: str = None):
        """Send test log messages."""
        try:
            config = await self._get_log_config(ctx.guild.id)
            if not config:
                embed = self._create_modern_embed(
                    "No Configuration Found",
                    "Please run /log setup first to configure logging.",
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed)
                return

            if category and category not in LOG_CATEGORIES:
                embed = self._create_modern_embed(
                    "Invalid Category", f"Valid categories: {', '.join(LOG_CATEGORIES)}"
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            categories_to_test = (
                [category]
                if category and category in LOG_CATEGORIES
                else LOG_CATEGORIES
            )

            sent_count = 0
            for cat in categories_to_test:
                if config.get("log_enabled", {}).get(cat, False):
                    embed = self._create_modern_embed(
                        f"Test Log - {cat.replace('_', ' ').title()}"
                    )
                    embed.add_field(name="Category", value=cat, inline=True)
                    embed.add_field(
                        name="Test User", value=ctx.author.mention, inline=True
                    )
                    embed.add_field(
                        name="Timestamp",
                        value=discord.utils.format_dt(datetime.utcnow(), "f"),
                        inline=True,
                    )
                    embed.set_footer(text=f"Test message • User ID: {ctx.author.id}")

                    await self._send_log(
                        ctx.guild, cat, embed, ctx.channel.id, ctx.author.id
                    )
                    sent_count += 1

            if sent_count > 0:
                embed = self._create_modern_embed(
                    "Test Messages Sent",
                    f"Sent {sent_count} test log messages to configured channels.",
                )
            else:
                embed = self._create_modern_embed(
                    "No Test Messages Sent",
                    "No logging categories are enabled or configured.",
                )

            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)
        except Exception as e:
            logger.error(f"Error in log test: {e}")
            embed = self._create_modern_embed(
                "Test Error", "An error occurred while sending test messages."
            )
            # embed.set_footer removed - CV2 doesn't support it
            await ctx.send(view=embed)

    @log.command(name="export", description="Export log data as a JSON file.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def log_export(self, ctx: commands.Context, days: int = 7):
        """Export log data for the specified number of days."""
        try:
            if days < 1 or days > 30:
                embed = self._create_modern_embed(
                    "Invalid Range", "Days must be between 1 and 30."
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.send(view=embed, ephemeral=True)
                return

            await ctx.defer()

            exported_data = {}
            total_entries = 0

            for day_offset in range(days):
                date = datetime.utcnow() - timedelta(days=day_offset)
                date_str = date.strftime("%Y-%m-%d")

                for category in LOG_CATEGORIES:
                    base_pattern = f"{ctx.guild.id}_{category}_{date_str}"
                    log_files = [
                        f
                        for f in Path(LOGS_DIR).iterdir()
                        if f.name.startswith(base_pattern)
                    ]

                    for log_file in log_files:
                        if log_file.exists():
                            try:
                                async with aiofiles.open(
                                    log_file, "r", encoding="utf-8"
                                ) as f:
                                    content = await f.read()
                                    if content.strip():
                                        logs = await asyncio.to_thread(
                                            json.loads, content
                                        )
                                        if isinstance(logs, list) and logs:
                                            key = f"{date_str}_{category}_{log_file.name.split('_')[-1].split('.')[0]}"
                                            exported_data[key] = logs
                                            total_entries += len(logs)
                            except Exception as e:
                                logger.error(f"Error reading log file {log_file}: {e}")

            if not exported_data:
                embed = self._create_modern_embed(
                    "No Data Found", f"No log data found for the last {days} days."
                )
                # embed.set_footer removed - CV2 doesn't support it
                await ctx.followup.send(view=embed)
                return

            export_filename = f"logs_export_{ctx.guild.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            export_data = {
                "guild_id": ctx.guild.id,
                "guild_name": ctx.guild.name,
                "export_date": datetime.utcnow().isoformat(),
                "days_exported": days,
                "total_entries": total_entries,
                "data": exported_data,
            }

            temp_path = Path(LOGS_DIR) / export_filename
            content = await asyncio.to_thread(
                json.dumps, export_data, indent=2, default=str
            )
            async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                await f.write(content)

            embed = self._create_modern_embed(
                "Export Complete",
                f"Exported {total_entries} log entries from the last {days} days.",
            )
            embed.add_field(
                name="File Size",
                value=f"{len(content.encode('utf-8')) / 1024:.2f} KB",
                inline=True,
            )
            embed.add_field(
                name="Categories",
                value=str(len(set(k.split("_", 1)[1] for k in exported_data.keys()))),
                inline=True,
            )
            # embed.set_footer removed - CV2 doesn't support it

            with open(temp_path, "rb") as f:
                file = discord.File(f, filename=export_filename)
                await ctx.followup.send(view=embed, file=file)

            await asyncio.to_thread(temp_path.unlink)

        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            embed = self._create_modern_embed(
                "Export Failed", "An error occurred while exporting log data."
            )
            # embed.set_footer removed - CV2 doesn't support it
            try:
                await ctx.followup.send(view=embed)
            except:
                await ctx.send(view=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Enhanced message edit logging with content comparison."""
        try:
            if not before.guild or before.author.bot or before.content == after.content:
                return

            embed = self._create_modern_embed("Message Edited")
            embed.set_author(
                name=before.author.display_name,
                icon_url=before.author.display_avatar.url,
            )

            before_content = before.content[:1000] if before.content else "No content"
            after_content = after.content[:1000] if after.content else "No content"

            embed.add_field(
                name="Before", value=f"```{before_content}```", inline=False
            )
            embed.add_field(name="After", value=f"```{after_content}```", inline=False)
            embed.add_field(name="Channel", value=before.channel.mention, inline=True)
            embed.add_field(name="User", value=f"{before.author.mention}", inline=True)
            embed.add_field(
                name="Jump to Message",
                value=f"[Click here]({after.jump_url})",
                inline=True,
            )
            embed.set_footer(
                text=f"User ID: {before.author.id} • Message ID: {before.id}"
            )

            await self._send_log(
                before.guild,
                "message_events",
                embed,
                before.channel.id,
                before.author.id,
            )
        except Exception as e:
            logger.error(f"Error in on_message_edit: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Enhanced message deletion logging with attachment info."""
        try:
            if not message.guild or message.author.bot:
                return

            embed = self._create_modern_embed("Message Deleted")
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url,
            )

            content = message.content[:1000] if message.content else "No content"
            embed.add_field(name="Content", value=f"```{content}```", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="User", value=message.author.mention, inline=True)

            if message.attachments:
                attachments = "\n".join(
                    [f"• {att.filename}" for att in message.attachments[:5]]
                )
                embed.add_field(name="Attachments", value=attachments, inline=False)

            embed.set_footer(
                text=f"User ID: {message.author.id} • Message ID: {message.id}"
            )

            await self._send_log(
                message.guild,
                "message_events",
                embed,
                message.channel.id,
                message.author.id,
            )
        except Exception as e:
            logger.error(f"Error in on_message_delete: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log member joins with comprehensive information."""
        try:
            embed = self._create_modern_embed("Member Joined")
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )

            embed.add_field(name="User", value=member.mention, inline=True)
            embed.add_field(
                name="Account Created",
                value=discord.utils.format_dt(member.created_at, "R"),
                inline=True,
            )
            embed.add_field(
                name="Member Count", value=str(member.guild.member_count), inline=True
            )

            embed.set_footer(text=f"User ID: {member.id}")
            embed.set_thumbnail(url=member.display_avatar.url)

            await self._send_log(
                member.guild, "join_leave_events", embed, None, member.id
            )
        except Exception as e:
            logger.error(f"Error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member leaves with role information."""
        try:
            embed = self._create_modern_embed("Member Left")
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )

            embed.add_field(
                name="User", value=f"{member.mention} ({member})", inline=True
            )
            embed.add_field(
                name="Joined",
                value=discord.utils.format_dt(member.joined_at, "R")
                if member.joined_at
                else "Unknown",
                inline=True,
            )
            embed.add_field(
                name="Member Count", value=str(member.guild.member_count), inline=True
            )

            if member.roles[1:]:
                roles = ", ".join([role.mention for role in member.roles[1:][:10]])
                embed.add_field(name="Roles", value=roles, inline=False)

            embed.set_footer(text=f"User ID: {member.id}")
            embed.set_thumbnail(url=member.display_avatar.url)

            await self._send_log(
                member.guild, "join_leave_events", embed, None, member.id
            )
        except Exception as e:
            logger.error(f"Error in on_member_remove: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log member updates including role changes."""
        try:
            if before.roles != after.roles:
                embed = self._create_modern_embed("Member Roles Updated")
                embed.set_author(
                    name=after.display_name, icon_url=after.display_avatar.url
                )

                embed.add_field(name="User", value=after.mention, inline=True)

                added_roles = set(after.roles) - set(before.roles)
                removed_roles = set(before.roles) - set(after.roles)

                if added_roles:
                    roles_added = ", ".join([role.mention for role in added_roles])
                    embed.add_field(name="Roles Added", value=roles_added, inline=False)

                if removed_roles:
                    roles_removed = ", ".join([role.mention for role in removed_roles])
                    embed.add_field(
                        name="Roles Removed", value=roles_removed, inline=False
                    )

                embed.set_footer(text=f"User ID: {after.id}")

                await self._send_log(
                    after.guild, "member_moderation", embed, None, after.id
                )

            if before.nick != after.nick:
                embed = self._create_modern_embed("Nickname Changed")
                embed.set_author(
                    name=after.display_name, icon_url=after.display_avatar.url
                )

                embed.add_field(name="User", value=after.mention, inline=True)
                embed.add_field(
                    name="Before", value=before.nick or "No nickname", inline=True
                )
                embed.add_field(
                    name="After", value=after.nick or "No nickname", inline=True
                )

                embed.set_footer(text=f"User ID: {after.id}")

                await self._send_log(
                    after.guild, "member_moderation", embed, None, after.id
                )
        except Exception as e:
            logger.error(f"Error in on_member_update: {e}")

    @commands.Cog.listener()
    async def on_member_ban(
        self, guild: discord.Guild, user: Union[discord.User, discord.Member]
    ):
        """Log member bans with audit log information."""
        try:
            embed = self._create_modern_embed("Member Banned")
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

            embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)

            audit_entry = await self._get_audit_log(
                guild, discord.AuditLogAction.ban, user.id
            )
            if audit_entry:
                embed.add_field(
                    name="Banned by", value=audit_entry.user.mention, inline=True
                )
                if audit_entry.reason:
                    embed.add_field(
                        name="Reason", value=audit_entry.reason[:1024], inline=False
                    )

            embed.set_footer(text=f"User ID: {user.id}")
            embed.set_thumbnail(url=user.display_avatar.url)

            await self._send_log(guild, "member_moderation", embed, None, user.id)
        except Exception as e:
            logger.error(f"Error in on_member_ban: {e}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log member unbans."""
        try:
            embed = self._create_modern_embed("Member Unbanned")
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

            embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)

            audit_entry = await self._get_audit_log(
                guild, discord.AuditLogAction.unban, user.id
            )
            if audit_entry:
                embed.add_field(
                    name="Unbanned by", value=audit_entry.user.mention, inline=True
                )
                if audit_entry.reason:
                    embed.add_field(
                        name="Reason", value=audit_entry.reason[:1024], inline=False
                    )

            embed.set_footer(text=f"User ID: {user.id}")
            embed.set_thumbnail(url=user.display_avatar.url)

            await self._send_log(guild, "member_moderation", embed, None, user.id)
        except Exception as e:
            logger.error(f"Error in on_member_unban: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Log voice state changes."""
        try:
            if before.channel == after.channel:
                return

            embed = self._create_modern_embed("Voice State Changed")
            embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )

            embed.add_field(name="User", value=member.mention, inline=True)

            if before.channel and after.channel:
                embed.add_field(name="Action", value="Moved channels", inline=True)
                embed.add_field(name="From", value=before.channel.mention, inline=True)
                embed.add_field(name="To", value=after.channel.mention, inline=True)
            elif after.channel:
                embed.add_field(name="Action", value="Joined voice", inline=True)
                embed.add_field(
                    name="Channel", value=after.channel.mention, inline=True
                )
            elif before.channel:
                embed.add_field(name="Action", value="Left voice", inline=True)
                embed.add_field(
                    name="Channel", value=before.channel.mention, inline=True
                )

            embed.set_footer(text=f"User ID: {member.id}")

            await self._send_log(member.guild, "voice_events", embed, None, member.id)
        except Exception as e:
            logger.error(f"Error in on_voice_state_update: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log channel creation."""
        try:
            embed = self._create_modern_embed("Channel Created")

            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Type", value=str(channel.type).title(), inline=True)
            embed.add_field(
                name="Category",
                value=channel.category.name if channel.category else "None",
                inline=True,
            )

            audit_entry = await self._get_audit_log(
                channel.guild, discord.AuditLogAction.channel_create, channel.id
            )
            if audit_entry:
                embed.add_field(
                    name="Created by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Channel ID: {channel.id}")

            await self._send_log(channel.guild, "channel_events", embed, channel.id)
        except Exception as e:
            logger.error(f"Error in on_guild_channel_create: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log channel deletion."""
        try:
            embed = self._create_modern_embed("Channel Deleted")

            embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
            embed.add_field(name="Type", value=str(channel.type).title(), inline=True)
            embed.add_field(
                name="Category",
                value=channel.category.name if channel.category else "None",
                inline=True,
            )

            audit_entry = await self._get_audit_log(
                channel.guild, discord.AuditLogAction.channel_delete, channel.id
            )
            if audit_entry:
                embed.add_field(
                    name="Deleted by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Channel ID: {channel.id}")

            await self._send_log(channel.guild, "channel_events", embed, channel.id)
        except Exception as e:
            logger.error(f"Error in on_guild_channel_delete: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Log channel updates."""
        try:
            changes = []

            if before.name != after.name:
                changes.append(f"Name: {before.name} → {after.name}")

            if getattr(before, "topic", None) != getattr(after, "topic", None):
                changes.append(
                    f"Topic: {before.topic or 'None'} → {after.topic or 'None'}"
                )

            if before.category != after.category:
                before_cat = before.category.name if before.category else "None"
                after_cat = after.category.name if after.category else "None"
                changes.append(f"Category: {before_cat} → {after_cat}")

            if not changes:
                return

            embed = self._create_modern_embed("Channel Updated")
            embed.add_field(name="Channel", value=after.mention, inline=True)
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)

            audit_entry = await self._get_audit_log(
                after.guild, discord.AuditLogAction.channel_update, after.id
            )
            if audit_entry:
                embed.add_field(
                    name="Updated by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Channel ID: {after.id}")

            await self._send_log(after.guild, "channel_events", embed, after.id)
        except Exception as e:
            logger.error(f"Error in on_guild_channel_update: {e}")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Log role creation."""
        try:
            embed = self._create_modern_embed("Role Created")

            embed.add_field(name="Role", value=role.mention, inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(
                name="Mentionable",
                value="Yes" if role.mentionable else "No",
                inline=True,
            )

            audit_entry = await self._get_audit_log(
                role.guild, discord.AuditLogAction.role_create, role.id
            )
            if audit_entry:
                embed.add_field(
                    name="Created by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Role ID: {role.id}")

            await self._send_log(role.guild, "role_events", embed)
        except Exception as e:
            logger.error(f"Error in on_guild_role_create: {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Log role deletion."""
        try:
            embed = self._create_modern_embed("Role Deleted")

            embed.add_field(name="Role", value=f"@{role.name}", inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(name="Members", value=str(len(role.members)), inline=True)

            audit_entry = await self._get_audit_log(
                role.guild, discord.AuditLogAction.role_delete, role.id
            )
            if audit_entry:
                embed.add_field(
                    name="Deleted by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Role ID: {role.id}")

            await self._send_log(role.guild, "role_events", embed)
        except Exception as e:
            logger.error(f"Error in on_guild_role_delete: {e}")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """Log role updates."""
        try:
            changes = []

            if before.name != after.name:
                changes.append(f"Name: {before.name} → {after.name}")

            if before.color != after.color:
                changes.append(f"Color: {before.color} → {after.color}")

            if before.mentionable != after.mentionable:
                changes.append(
                    f"Mentionable: {before.mentionable} → {after.mentionable}"
                )

            if before.permissions != after.permissions:
                changes.append("Permissions updated")

            if not changes:
                return

            embed = self._create_modern_embed("Role Updated")
            embed.add_field(name="Role", value=after.mention, inline=True)
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)

            audit_entry = await self._get_audit_log(
                after.guild, discord.AuditLogAction.role_update, after.id
            )
            if audit_entry:
                embed.add_field(
                    name="Updated by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Role ID: {after.id}")

            await self._send_log(after.guild, "role_events", embed)
        except Exception as e:
            logger.error(f"Error in on_guild_role_update: {e}")

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """Log guild/server updates."""
        try:
            changes = []

            if before.name != after.name:
                changes.append(f"Name: {before.name} → {after.name}")

            if before.description != after.description:
                changes.append(f"Description updated")

            if before.verification_level != after.verification_level:
                changes.append(
                    f"Verification Level: {before.verification_level} → {after.verification_level}"
                )

            if not changes:
                return

            embed = self._create_modern_embed("Server Updated")
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)

            audit_entry = await self._get_audit_log(
                after, discord.AuditLogAction.guild_update
            )
            if audit_entry:
                embed.add_field(
                    name="Updated by", value=audit_entry.user.mention, inline=True
                )

            embed.set_footer(text=f"Guild ID: {after.id}")

            await self._send_log(after, "system_events", embed)
        except Exception as e:
            logger.error(f"Error in on_guild_update: {e}")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """Log emoji updates."""
        try:
            added_emojis = set(after) - set(before)
            removed_emojis = set(before) - set(after)

            if added_emojis:
                for emoji in added_emojis:
                    embed = self._create_modern_embed("Emoji Added")
                    embed.add_field(
                        name="Emoji", value=f"{emoji} :{emoji.name}:", inline=True
                    )
                    embed.add_field(name="ID", value=str(emoji.id), inline=True)
                    embed.add_field(
                        name="Animated",
                        value="Yes" if emoji.animated else "No",
                        inline=True,
                    )

                    audit_entry = await self._get_audit_log(
                        guild, discord.AuditLogAction.emoji_create, emoji.id
                    )
                    if audit_entry:
                        embed.add_field(
                            name="Created by",
                            value=audit_entry.user.mention,
                            inline=True,
                        )

                    embed.set_footer(text=f"Emoji ID: {emoji.id}")
                    await self._send_log(guild, "emoji_events", embed)

            if removed_emojis:
                for emoji in removed_emojis:
                    embed = self._create_modern_embed("Emoji Removed")
                    embed.add_field(name="Emoji", value=f":{emoji.name}:", inline=True)
                    embed.add_field(name="ID", value=str(emoji.id), inline=True)
                    embed.add_field(
                        name="Animated",
                        value="Yes" if emoji.animated else "No",
                        inline=True,
                    )

                    audit_entry = await self._get_audit_log(
                        guild, discord.AuditLogAction.emoji_delete, emoji.id
                    )
                    if audit_entry:
                        embed.add_field(
                            name="Deleted by",
                            value=audit_entry.user.mention,
                            inline=True,
                        )

                    embed.set_footer(text=f"Emoji ID: {emoji.id}")
                    await self._send_log(guild, "emoji_events", embed)
        except Exception as e:
            logger.error(f"Error in on_guild_emojis_update: {e}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Log reaction additions (optional)."""
        try:
            if not reaction.message.guild or user.bot:
                return

            embed = self._create_modern_embed("Reaction Added")
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

            embed.add_field(name="User", value=user.mention, inline=True)
            embed.add_field(name="Reaction", value=str(reaction.emoji), inline=True)
            embed.add_field(
                name="Message",
                value=f"[Jump to message]({reaction.message.jump_url})",
                inline=True,
            )
            embed.add_field(
                name="Channel", value=reaction.message.channel.mention, inline=True
            )

            embed.set_footer(
                text=f"User ID: {user.id} • Message ID: {reaction.message.id}"
            )

            await self._send_log(
                reaction.message.guild,
                "reaction_events",
                embed,
                reaction.message.channel.id,
                user.id,
            )
        except Exception as e:
            logger.error(f"Error in on_reaction_add: {e}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """Log reaction removals (optional)."""
        try:
            if not reaction.message.guild or user.bot:
                return

            embed = self._create_modern_embed("Reaction Removed")
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

            embed.add_field(name="User", value=user.mention, inline=True)
            embed.add_field(name="Reaction", value=str(reaction.emoji), inline=True)
            embed.add_field(
                name="Message",
                value=f"[Jump to message]({reaction.message.jump_url})",
                inline=True,
            )
            embed.add_field(
                name="Channel", value=reaction.message.channel.mention, inline=True
            )

            embed.set_footer(
                text=f"User ID: {user.id} • Message ID: {reaction.message.id}"
            )

            await self._send_log(
                reaction.message.guild,
                "reaction_events",
                embed,
                reaction.message.channel.id,
                user.id,
            )
        except Exception as e:
            logger.error(f"Error in on_reaction_remove: {e}")


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(Logging(bot))
