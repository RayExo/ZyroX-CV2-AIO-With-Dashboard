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
from discord.ui import Button, View


class Nitro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions and (
            "nitro" in message.content.lower() or "$nitro" in message.content.lower()
        ):
            ctx = await self.bot.get_context(message)
            await self.bot.invoke(ctx)

    @commands.command(name="nitro")
    async def nitro(self, ctx):
        embed = discord.Embed(color=0x2B2D31)
        embed.add_field(
            name="A WILD NITRO GIFT APPEARS?",
            value="Expires in 12 hours\n\nClick the claim button for claiming Nitro",
            inline=False,
        )
        embed.set_image(
            url="https://media.tenor.com/ltVe8iMhgXcAAAAS/nitro-discord.gif"
        )

        claim_button = Button(
            style=discord.ButtonStyle.primary,
            label="Click me!",
            url="https://discord.gg/codexdev",
            disabled=False,
        )

        view = View()
        view.add_item(claim_button)

        await ctx.send(embed=embed, view=view)
