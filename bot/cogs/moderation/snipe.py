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
from utils.emoji import ERROR
from discord.ext import commands
from datetime import datetime

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # This dictionary will store the last deleted message for each channel.
        # Format: {channel_id: {'content': '...', 'author': '...', 'deleted_at': ...}}
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignore messages from bots or from DMs
        if message.author.bot or not message.guild:
            return
        
        # Store the message details
        self.sniped_messages[message.channel.id] = {
            'content': message.content,
            'author': message.author,
            'deleted_at': datetime.utcnow()
        }

    @commands.command(name='snipe', help="Shows the most recently deleted message in the channel.")
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx):
        # Check if there is a sniped message for the current channel
        if ctx.channel.id in self.sniped_messages:
            sniped_data = self.sniped_messages[ctx.channel.id]
            author = sniped_data['author']
            content = sniped_data['content']
            deleted_at = sniped_data['deleted_at']

            # If the deleted message had no text content (e.g., only an image)
            if not content:
                content = "No text content was found in the deleted message."

            # Create the simple embed
            embed = discord.Embed(
                description=content,
                color=0xFF0000,
                timestamp=deleted_at
            )
            embed.set_author(name=f"Sniped message from {author.name}", icon_url=author.display_avatar.url)
            embed.set_footer(text="Deleted at") # The timestamp is automatically formatted in the footer
            
            await ctx.send(embed=embed)
        else:
            # Send an error message if no message is stored for this channel
            embed = discord.Embed(
                description=f"{ERROR} | There are no deleted messages to snipe in this channel.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
