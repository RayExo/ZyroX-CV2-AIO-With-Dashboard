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
from utils.emoji import LOCK
from discord.ext import commands


class _encrypt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def help_custom(self):
        emoji = LOCK
        label = "Encryption Commands"
        description = "Encode & decode text in various formats"
        return emoji, label, description

    @commands.group(name="encryption", aliases=["encrypt"], invoke_without_command=True)
    async def _Encryption(self, ctx: commands.Context):
        """Show all available encryption commands"""
        embed = discord.Embed(
            title="Encryption Commands",
            description=f"Use `{ctx.prefix}encode <type>` to encode text, `{ctx.prefix}decode <type>` to decode.",
            color=0x000000,
        )

        embed.add_field(
            name="📝 Encode Commands",
            value=f"""
`{ctx.prefix}encode base32` / `{ctx.prefix}encode b32` - Encode to base32
`{ctx.prefix}encode base64` / `{ctx.prefix}encode b64` - Encode to base64
`{ctx.prefix}encode rot13` / `{ctx.prefix}encode r13` - Encode to rot13
`{ctx.prefix}encode hex` - Encode to hex
`{ctx.prefix}encode base85` / `{ctx.prefix}encode b85` - Encode to base85
`{ctx.prefix}encode ascii85` / `{ctx.prefix}encode a85` - Encode to ASCII85
""",
            inline=False,
        )

        embed.add_field(
            name="📄 Decode Commands",
            value=f"""
`{ctx.prefix}decode base32` / `{ctx.prefix}decode b32` - Decode from base32
`{ctx.prefix}decode base64` / `{ctx.prefix}decode b64` - Decode from base64
`{ctx.prefix}decode rot13` / `{ctx.prefix}decode r13` - Decode from rot13
`{ctx.prefix}decode hex` - Decode from hex
`{ctx.prefix}decode base85` / `{ctx.prefix}decode b85` - Decode from base85
`{ctx.prefix}decode ascii85` / `{ctx.prefix}decode a85` - Decode from ASCII85
""",
            inline=False,
        )

        embed.add_field(
            name="🔐 Utility",
            value=f"`{ctx.prefix}password` - Generate a random secure password (sent via DM)",
            inline=False,
        )

        embed.set_footer(
            text="Use encode/decode commands to encrypt or decrypt your text"
        )

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(_encrypt(bot))
