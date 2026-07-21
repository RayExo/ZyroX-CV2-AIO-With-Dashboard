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

from utils import getConfig
from utils.config import BotName
import discord
from utils.emoji import ARROWRED, CODEBASE, HEART3, INDEX, ZYROXLINKS
from discord.ui import LayoutView, TextDisplay, Separator, Container, ActionRow, Select
from discord.ext import commands
from utils.Tools import get_ignore_data
import aiosqlite


class MentionSelectView(LayoutView):
    def __init__(self, message, bot, prefix):
        super().__init__(timeout=300)
        self.message = message
        self.bot = bot
        self.prefix = prefix

        self.select = Select(
            placeholder=f"Start With {BotName}",
            options=[
                discord.SelectOption(
                    label="Home",
                    emoji=INDEX,
                    description="Go to the main menu",
                ),
                discord.SelectOption(
                    label="Developer Info",
                    emoji=CODEBASE,
                    description="See who created me",
                ),
                discord.SelectOption(
                    label="Links",
                    emoji=ZYROXLINKS,
                    description="Useful bot links",
                ),
            ],
        )
        self.select.callback = self.on_select

        self.add_item(
            Container(
                TextDisplay(f"**{message.guild.name}**"),
                Separator(visible=True),
                TextDisplay(
                    f"> {HEART3} **Hey {message.author.mention}**\n"
                    f"> {ARROWRED} **Prefix For This Server: `{prefix}`**\n\n"
                    f"___Type `{prefix}help` for more information.___"
                ),
                ActionRow(self.select),
            )
        )

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.message.author.id:
            await interaction.response.send_message(
                "This menu is not for you!", ephemeral=True
            )
            return

        selected = interaction.data.get("values", ["Home"])[0]

        if selected == "Home":
            content = (
                f"> {HEART3} **Hey {interaction.user.mention}**\n"
                f"> {ARROWRED} **Prefix For This Server: `{self.prefix}`**\n\n"
                f"___Type `{self.prefix}help` for more information.___"
            )
        elif selected == "Developer Info":
            content = (
                "There are only 2 Founders Who Created Me. Thanks You To Them 💞.\n\n"
                "**The Founder**\n"
                "**[01]. [Ray](https://discord.com/users/870179991462236170)**\n**[02]. [runxking](https://discord.com/users/767979794411028491)**"
            )
        elif selected == "Links":
            content = (
                f"**[Invite {BotName}](https://discord.com/oauth2/authorize?client_id=1396114795102470196)**\n"
                "**[Join Support Server](https://discord.gg/codexdev)**"
            )

        new_container = Container(
            TextDisplay(f"**{self.message.guild.name}**"),
            Separator(visible=True),
            TextDisplay(content),
            ActionRow(self.select),
        )

        self.clear_items()
        self.add_item(new_container)

        await interaction.response.edit_message(view=self)


class Mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xFF0000
        self.bot_name = BotName

    async def is_blacklisted(self, message):
        async with aiosqlite.connect("db/block.db") as db:
            cursor = await db.execute(
                "SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (message.guild.id,)
            )
            if await cursor.fetchone():
                return True
            cursor = await db.execute(
                "SELECT 1 FROM user_blacklist WHERE user_id = ?", (message.author.id,)
            )
            if await cursor.fetchone():
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if await self.is_blacklisted(message):
            return

        ignore_data = await get_ignore_data(message.guild.id)
        if (
            str(message.author.id) in ignore_data["user"]
            or str(message.channel.id) in ignore_data["channel"]
        ):
            return

        if (
            self.bot.user in message.mentions
            and len(message.content.strip().split()) == 1
        ):
            guild_id = message.guild.id
            data = await getConfig(guild_id)
            prefix = data["prefix"]

            view = MentionSelectView(message, self.bot, prefix)
            await message.channel.send(view=view)


def setup(bot):
    bot.add_cog(Mention(bot))
