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
from deep_translator import GoogleTranslator
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.cv2 import CV2, build_container

class TranslateSuccess(LayoutView):
    def __init__(self, original, translated, author):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay("🌐 **Translation Complete**"),
                Separator(visible=True),
                TextDisplay(f"**Original (Hinglish):**\n{original}"),
                Separator(visible=True),
                TextDisplay(f"**Translated (English):**\n{translated}"),
                Separator(visible=True),
                TextDisplay(f"Requested by **{author.display_name}**")
            )
        )

class TranslateError(LayoutView):
    def __init__(self, error_msg):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay("❌ **Translation Failed**"),
                Separator(visible=True),
                TextDisplay(f"`{error_msg}`")
            )
        )

class TranslateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="hinglish",
        help="Translate informal Hinglish to proper English.",
        usage="!hinglish chlo udhr chat active krlo idhr nai"
    )
    async def hinglish(self, ctx: commands.Context, *, text: str = None):
        if not text:
            return await ctx.reply(
                "⚠️ Please provide some Hinglish text to translate.",
                ephemeral=True if ctx.interaction else False
            )

        msg = await ctx.reply(
            "🔄 Translating Hinglish...",
            ephemeral=True if ctx.interaction else False
        )

        try:
            # Translation using deep-translator (Google)
            translated = GoogleTranslator(source="auto", target="en").translate(text)
            
            view = TranslateSuccess(text, translated, ctx.author)
            await msg.edit(content=None, view=view, embed=None)

        except Exception as e:
            view = TranslateError(str(e))
            await msg.edit(content=None, view=view, embed=None)

async def setup(bot):
    await bot.add_cog(TranslateCog(bot))
