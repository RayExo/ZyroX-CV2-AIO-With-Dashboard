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
from utils.emoji import LEVEL_UP
from discord .ext import commands 


class _leveling (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 

    """Leveling commands"""

    def help_custom (self ):
		      emoji =LEVEL_UP
		      label ="Leveling Commands"
		      description ="Shows you the commands of leveling"
		      return emoji ,label ,description 

    @commands .group ()
    async def __Leveling__ (self ,ctx :commands .Context ):
        """`level status`, `level channel`, `level message`, `level desc`, `level color`, `level thumbnail`, `level image`, `level clearimage`, `level xprange`, `level multiplier`, `level addreward`, `level removereward`, `level rewards`, `level setxp`, `level preview`, `level xpboost`, `level xpboost add`, `level xpboost remove`, `level xpboost list`, `level blacklist`, `level blacklist channel`, `level blacklist role`, `level unblacklist`, `level unblacklist channel`, `level unblacklist role`, `level stats`, `level leaderboard`, `level reset`, `level reset user`, `level reset all`, `level placeholders`, `level rank`"""