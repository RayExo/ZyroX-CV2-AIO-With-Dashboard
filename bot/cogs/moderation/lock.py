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
from utils.emoji import TICK
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.red()

    @commands.hybrid_command(
        name="lock",
        description="Locks a channel to prevent sending messages.",
        aliases=["lockchannel"]
    )
    # Using manage_channels is more appropriate for locking/unlocking
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock_command(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Locks the specified channel or the current one if none is provided."""
        
        # If no channel is specified, use the current channel
        channel = channel or ctx.channel
        
        # Check if the channel is already locked
        if not channel.permissions_for(ctx.guild.default_role).send_messages:
            embed = discord.Embed(
                description=f"**Channel: {channel.mention}\n{TICK} Status: Already Locked**",
                color=0xFF0000
            )
            #embed.set_author(name=f"{c", icon_url="")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            return

        # Lock the channel by updating permissions for the @everyone role
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        # Create the confirmation embed
        embed = discord.Embed(
            title="{BRAND_NAME} | Lockdown",
            description=f"{TICK} | Successfully Locked {channel.mention}",
            color=0xFF0000
        )
        #embed.set_author(name=f"Successfully Locked {channel.name}", icon_url="")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        #embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        # Send the final message
        await ctx.send(embed=embed)

# Standard setup function to load the cog
async def setup(bot):
    await bot.add_cog(Lock(bot))
