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
from discord.ui import LayoutView, TextDisplay, Separator, Container, Button, ActionRow
from discord.ext import commands
from utils.cv2 import CV2, build_container
from utils.config import STAFF_IDS


class SuccessView(LayoutView):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

        self.add_item(
            build_container(
                TextDisplay("**Message Sent**"),
                Separator(visible=True),
                TextDisplay(
                    f"✅ Your message has been successfully sent to **{member.name}**"
                ),
            )
        )


class ErrorView(LayoutView):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

        self.add_item(
            build_container(
                TextDisplay("**Delivery Failed**"),
                Separator(visible=True),
                TextDisplay(
                    f"❌ Could not send the message. **{member.name}** may have their DMs disabled."
                ),
            )
        )


class GenericErrorView(LayoutView):
    def __init__(self, error):
        super().__init__(timeout=None)
        self.error = error

        self.add_item(
            build_container(
                TextDisplay("**Error Occurred**"),
                Separator(visible=True),
                TextDisplay(f"🤔 Something went wrong. Error: {error}"),
            )
        )


class PermissionErrorView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            build_container(
                TextDisplay("**Permission Denied**"),
                Separator(visible=True),
                TextDisplay("❌ You do not have permission to use this command."),
            )
        )


class StaffDMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dmstaff")
    async def dm_staff(self, ctx, member: discord.Member, *, message: str):
        if ctx.author.id not in STAFF_IDS:
            view = PermissionErrorView()
            await ctx.reply(view=view)
            return

        try:
            embed = discord.Embed(
                title="📢 A Message from the Staff Team",
                description=message,
                color=0xFF0000,
            )
            embed.set_footer(text=f"This message was sent by {ctx.author.name}.")

            await member.send(embed=embed)

            view = SuccessView(member)
            await ctx.reply(view=view)

        except discord.Forbidden:
            view = ErrorView(member)
            await ctx.reply(view=view)
        except Exception as e:
            view = GenericErrorView(str(e))
            await ctx.reply(view=view)
            print(f"Error in dmstaff command: {e}")


async def setup(bot):
    await bot.add_cog(StaffDMCog(bot))
