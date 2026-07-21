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
from utils.emoji import THUNDER
from discord .ext import commands 

class _verify(commands .Cog ):
    def __init__ (self ,bot ):
        self.bot=bot 

    """Verification commands help"""

    def help_custom (self ):
        emoji =THUNDER
        label ="Verification Commands"
        description ="Show you the commands of Verification"
        return emoji ,label ,description 

    @commands .group ()
    async def __Verification__ (self ,ctx :commands .Context ):
        """`verification setup`, `verification status`, `verification enable`, `verification disable`, `verification logs`, `verification reset`, `verification verify`, `verification fix`"""
        pass 

async def setup (bot ):
    await bot.add_cog(_verify(bot))
