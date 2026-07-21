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
from discord.ui import LayoutView, MediaGallery, TextDisplay
import aiohttp
import os
import random
from utils.cv2 import CV2, build_container

PEXELS_API_KEY = "js24mfV1bCCvgV6KfnEFvo5UnCHnATFarFnAdDrpDbczl7f0yXpjDF8x"

class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_pexels_image(self, query):
        headers = {
            "Authorization": PEXELS_API_KEY
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.pexels.com/v1/search?query={query}&per_page=50", headers=headers) as resp:
                data = await resp.json()
                if data.get("photos"):
                    image = random.choice(data["photos"])
                    return image["src"]["original"]
                return None

    async def fetch_waifu_image(self, category="waifu"):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.waifu.pics/sfw/{category}") as resp:
                data = await resp.json()
                return data["url"]

    async def send_image_view(self, ctx, title, url):
        if url:
            view = LayoutView(timeout=None)
            gallery = MediaGallery()
            gallery.add_item(media=url)
            view.add_item(build_container(TextDisplay(f"**{title}**"), gallery))
            await ctx.send(view=view)
        else:
            await ctx.send(view=CV2("❌ Error", f"No image found for {title.lower()}."))

    @commands.command(name="boy")
    async def boy_image(self, ctx):
        url = await self.fetch_pexels_image("handsome boy")
        await self.send_image_view(ctx, "👦 Boy Pic", url)

    # @commands.command(name="girl")
    # async def girl_image(self, ctx):
    #     url = await self.fetch_pexels_image("beautiful girl")
    #     await self.send_image_view(ctx, "👧 Girl Pic", url)

    @commands.command(name="couple")
    async def couple_image(self, ctx):
        url = await self.fetch_pexels_image("romantic couple")
        await self.send_image_view(ctx, "💑 Couple Pic", url)

    @commands.command(name="anime")
    async def anime_image(self, ctx):
        url = await self.fetch_waifu_image("waifu")
        await self.send_image_view(ctx, "🧚 Anime Waifu", url)

async def setup(bot):
    await bot.add_cog(ImageCommands(bot))
