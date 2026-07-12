import discord
from utils.emoji import ZCOUNTING

from discord.ext import commands

class _Counting(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    """Counting"""

    def help_custom(self):

              emoji = ZCOUNTING

              label = "Counting"

              description = "Show you Commands of Counting"

              return emoji, label, description

    @commands.group()

    async def __Counting__(self, ctx: commands.Context):

        """`>counting`, `>counting enable/disable`, `>counting channel #channel`, `>counting stats`, `>counting config continue/reset`"""