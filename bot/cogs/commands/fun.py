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
from discord.ui import LayoutView, TextDisplay, Separator, MediaGallery
import random
import aiohttp
from discord import app_commands
from utils.Tools import blacklist_check, ignore_check
from utils.cv2 import CV2, build_container

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_api_key = "y3KcqQTdiS0RYcpNJrWn8hFGglKqX4is"

    async def fetch_giphy(self, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_api_key}&q={query}&limit=30&rating=pg") as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data['data']:
                    return random.choice(data['data'])['images']['original']['url']
                else:
                    return None

    def random_emoji(self):
        return random.choice(["😂", "🤣", "😆", "😳", "🥴", "🙃", "😜"])

    async def action_command(self, ctx, user: discord.Member, action: str):
        gif_url = await self.fetch_giphy(action)
        if not gif_url:
            await ctx.send(view=CV2("😒 Error", "GIPHY API is sleeping. Try later!"))
            return
        view = LayoutView(timeout=None)
        gallery = MediaGallery()
        gallery.add_item(media=gif_url)
        view.add_item(build_container(
            TextDisplay(f"**{ctx.author.mention} {action}s {user.mention} {self.random_emoji()}**"),
            gallery
        ))
        await ctx.send(view=view)

    async def meter_command(self, ctx, title, user, text):
        await ctx.send(view=CV2(title, text))

    @commands.command(name="shipp")
    @blacklist_check()
    @ignore_check()
    async def shipp(self, ctx, user1: discord.Member, user2: discord.Member):
        percentage = random.randint(0, 100)
        await ctx.send(view=CV2(f"{self.random_emoji()} Ship Result", f"**{user1.mention} x {user2.mention} = {percentage}% Love**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def hug(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "hug")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def kiss(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "kiss")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def pat(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "pat")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def slap(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "slap")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def tickle(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "tickle")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        await ctx.send(view=CV2("🪙 Coin Flip", f"**Result: {result}**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dice(self, ctx):
        result = random.randint(1, 6)
        await ctx.send(view=CV2("🎲 Dice Roll", f"**You rolled a {result}!**"))

    @commands.command(name="8ball")
    @blacklist_check()
    @ignore_check()
    async def eight_ball(self, ctx, *, question: str):
        responses = ["It is certain.", "Without a doubt.", "You may rely on it.",
                     "Ask again later.", "Better not tell you now.",
                     "Don't count on it.", "My sources say no.", "Very doubtful."]
        await ctx.send(view=CV2("🎱 Magic 8Ball", f"**Q:** {question}\n**A:** {random.choice(responses)}"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def roast(self, ctx, user: discord.Member):
        roasts = [
            f"{user.mention} you're the reason shampoo has instructions!",
            f"{user.mention} you have something on your chin... no, the third one down!",
            f"{user.mention} your secrets are safe with me. I never even listen when you tell me them."
        ]
        await ctx.send(view=CV2("🔥 Roast Time", random.choice(roasts)))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def iq(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 IQ Test", f"**{user.mention} has an IQ of {random.randint(50, 200)}!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dumb(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🤪 Dumbness Test", f"**{user.mention} is {random.randint(0, 100)}% dumb!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def simprate(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("😳 Simp Rate", f"**{user.mention} is {random.randint(0, 100)}% simp!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def toxic(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("☠️ Toxic Meter", f"**{user.mention} is {random.randint(0, 100)}% toxic!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def intelligence(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Intelligence Meter", f"**{user.mention} has {random.randint(0, 200)} IQ Points!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def genius(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🤓 Genius Rate", f"**{user.mention} is {random.randint(0, 100)}% genius!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def brainrate(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Brain Power", f"**{user.mention} is using {random.randint(0, 100)}% of their brain!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def howhot(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🔥 Hotness Meter", f"**{user.mention} is {random.randint(0, 100)}% hot!**"))

async def setup(bot):
    await bot.add_cog(Fun(bot))