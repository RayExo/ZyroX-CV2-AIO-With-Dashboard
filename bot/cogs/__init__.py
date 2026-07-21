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

from __future__ import annotations
from core import zyrox
from colorama import Fore, Style, init


from .commands.help import Help
from .commands.general import General
from .commands.music import Music
from .commands.automod import Automod
from .commands.welcome import Welcomer
from .commands.fun import Fun
from .commands.Games import Games
from .commands.extra import Extra
from .commands.owner import Owner
from .commands.voice import Voice
from .commands.afk import afk
from .commands.ignore import Ignore
from .commands.Media import Media
from .commands.Invc import Invcrole
from .commands.giveaway import Giveaway
from .commands.Embed import Embed
from .commands.steal import Steal
from .commands.timer import Timer
from .commands.blacklist import Blacklist
from .commands.block import Block
from .commands.nightmode import Nightmode
from .commands.tracking import Tracking
from .commands.owner import Badges
#from .commands.map import Map
from .commands.autoresponder import AutoResponder
from .commands.customrole import Customrole
from .commands.autorole import AutoRole
from .commands.ticket import TicketCog
from .commands.logging import Logging
from .commands.translate import TranslateCog
from .commands.jail import Jail
from .commands.antinuke import Antinuke
from .commands.extraown import Extraowner
from .commands.anti_wl import Whitelist
from .commands.anti_unwl import Unwhitelist
from .commands.slots import Slots
from .commands.blackjack import Blackjack
from .commands.autoreact import AutoReaction
from .commands.stats import Stats
from .commands.emergency import Emergency
from .commands.notify import NotifCommands
from .commands.status import Status
from .commands.np import NoPrefix
from .commands.filters import FilterCog
from .commands.owner2 import Global
from .commands.qr import QR
from .commands.vanityroles import VanityRoles
from .commands.reactionroles import ReactionRoles 
from .commands.messages import Messages
from .commands.fastgreet import FastGreet
from .commands.counting import Counting
from .commands.j2c import JoinToCreate
from .commands.ai import AI 
from .commands.dms import StaffDMCog
from .commands.booster import Booster
from .commands.leveling import Leveling
from .commands.stickymessage import StickyMessage
from .commands.verification import Verification
from .commands.minecraft import Minecraft
from .commands.encryption import encryption
from .commands.calc import calculator
from .commands.joindm import joindm
from .commands.Birthday import Birthdays
from .commands.nitro import Nitro
from .commands.image import ImageCommands
from .commands.youtube import Youtube
#____________ Events _____________

#from .events.autoblacklist import AutoBlacklist
from .events.Errors import Errors
from .events.on_guild import Guild
from .events.autorole import Autorole2
from .events.auto import Autorole
from .events.greet2 import greet
from .events.mention import Mention
from .events.react import React
from .events.autoreact import AutoReactListener
#from .events.topgg import TopGG
from .events.ai import AIResponses 
from .events.stickymessage import StickyMessageListener

########-------HELP-------########
from .zyrox.antinuke import _antinuke
from .zyrox.extra import _extra
from .zyrox.general import _general
from .zyrox.automod import _automod 
from .zyrox.moderation import _moderation
#from .zyrox.inviteTracker import _inviteTracker
from .zyrox.music import _music
from .zyrox.fun import _fun
from .zyrox.games import _games
from .zyrox.ignore import _ignore
from .zyrox.server import _server
from .zyrox.voice import _voice 
from .zyrox.welcome import _welcome 
from .zyrox.giveaway import _giveaway
from .zyrox.ticket import _ticket
#from .axon.vanityroles import Vanityroles69999
from .zyrox.logging import _logging
from .zyrox.vanity import _vanity
from .zyrox.inviteTracker import inviteTracker 
from .zyrox.counting import _Counting
from .zyrox.j2c import _J2C
from .zyrox.ai import _ai
from .zyrox.booster import __boost 
from .zyrox.leveling import _leveling
from .zyrox.sticky import _sticky
from .zyrox.verify import _verify
from .zyrox.encryption import _encrypt
from .zyrox.mc import _mc
from .zyrox.joindm import _joindm
from .zyrox.birth import _birth

#########ANTINUKE#########

from .antinuke.anti_member_update import AntiMemberUpdate
from .antinuke.antiban import AntiBan
from .antinuke.antibotadd import AntiBotAdd
from .antinuke.antichcr import AntiChannelCreate
from .antinuke.antichdl import AntiChannelDelete
from .antinuke.antichup import AntiChannelUpdate
from .antinuke.antieveryone import AntiEveryone
from .antinuke.antiguild import AntiGuildUpdate
from .antinuke.antiIntegration import AntiIntegration
from .antinuke.antikick import AntiKick
from .antinuke.antiprune import AntiPrune
from .antinuke.antirlcr import AntiRoleCreate
from .antinuke.antirldl import AntiRoleDelete
from .antinuke.antirlup import AntiRoleUpdate
from .antinuke.antiwebhook import AntiWebhookUpdate
from .antinuke.antiwebhookcr import AntiWebhookCreate
from .antinuke.antiwebhookdl import AntiWebhookDelete

#Extra Optional Events 

#from .antinuke.antiemocr import AntiEmojiCreate
#from .antinuke.antiemodl import AntiEmojiDelete
#from .antinuke.antiemoup import AntiEmojiUpdate
#from .antinuke.antisticker import AntiSticker
#from .antinuke.antiunban import AntiUnban

############ AUTOMOD ############
from .automod.antispam import AntiSpam
from .automod.anticaps import AntiCaps
from .automod.antilink import AntiLink
from .automod.anti_invites import AntiInvite
from .automod.anti_mass_mention import AntiMassMention
from .automod.anti_emoji_spam import AntiEmojiSpam


from .moderation.ban import Ban
from .moderation.unban import Unban
from .moderation.timeout import Mute
from .moderation.unmute import Unmute
from .moderation.lock import Lock
from .moderation.unlock import Unlock
from .moderation.hide import Hide
from .moderation.unhide import Unhide
from .moderation.kick import Kick
from .moderation.warn import Warn
from .moderation.role import Role
from .moderation.message import Message
from .moderation.moderation import Moderation
from .moderation.topcheck import TopCheck
from .moderation.snipe import Snipe


from utils.config import BotName

async def setup(bot: zyrox):
  cogs_to_load = [
        Help, General, Moderation, Automod, Welcomer, Fun, Games, Extra,
        Voice, Owner, Customrole, afk, Embed, Media, Ignore, TicketCog, Logging,
        Invcrole, Steal, Timer,
        Blacklist, Block, Nightmode, Badges, Antinuke, Whitelist, 
        Unwhitelist, Extraowner, Blackjack, Slots, Guild, Errors, Autorole2, Autorole, greet, AutoResponder,
        Mention, AutoRole, React, AntiMemberUpdate, AntiBan, AntiBotAdd,
        AntiChannelCreate, AntiChannelDelete, AntiChannelUpdate, AntiEveryone, AntiGuildUpdate,
        AntiIntegration, AntiKick, AntiPrune, AntiRoleCreate, AntiRoleDelete,
        AntiRoleUpdate, AntiWebhookUpdate, AntiWebhookCreate, 
        AntiWebhookDelete, AntiSpam, AntiCaps, AntiLink, AntiInvite, AntiMassMention, Stats, Status, NoPrefix, FilterCog, AutoReaction, AutoReactListener, Ban, Unban, Mute, Unmute, Lock, Unlock, Hide, Unhide, Kick, Warn, Role, Message, Moderation, TopCheck, Snipe, Global, QR, VanityRoles, ReactionRoles, Messages, TranslateCog, FastGreet, Jail, inviteTracker,Counting,AI
    ]


  await bot.add_cog(Help(bot))
  await bot.add_cog(General(bot))
  await bot.add_cog(Music(bot))
  await bot.add_cog(Automod(bot))
  await bot.add_cog(Welcomer(bot))
  await bot.add_cog(Fun(bot))
  await bot.add_cog(Tracking(bot))
  await bot.add_cog(Games(bot))
  await bot.add_cog(Extra(bot))
  await bot.add_cog(Voice(bot))
  await bot.add_cog(Owner(bot))
  await bot.add_cog(Customrole(bot))
  await bot.add_cog(afk(bot))
  await bot.add_cog(Embed(bot))
  await bot.add_cog(Media(bot))
  await bot.add_cog(Ignore(bot))
  await bot.add_cog(Invcrole(bot))
  await bot.add_cog(Giveaway(bot))
  await bot.add_cog(Steal(bot))
  await bot.add_cog(Booster(bot))
  await bot.add_cog(Timer(bot))
  await bot.add_cog(Blacklist(bot))
  await bot.add_cog(Block(bot))
  await bot.add_cog(Nightmode(bot))
  await bot.add_cog(Badges(bot))
  await bot.add_cog(Antinuke(bot))
  await bot.add_cog(Whitelist(bot))
  await bot.add_cog(Unwhitelist(bot))
  await bot.add_cog(Extraowner(bot))
  await bot.add_cog(Slots(bot))
  await bot.add_cog(Blackjack(bot))
  await bot.add_cog(Stats(bot))
  await bot.add_cog(Emergency(bot))
  await bot.add_cog(Status(bot))
  await bot.add_cog(NoPrefix(bot))
  await bot.add_cog(FilterCog(bot))
  await bot.add_cog(Global(bot))
 # await bot.add_cog(Map(bot))
  await bot.add_cog(TicketCog(bot))
  await bot.add_cog(Logging(bot))
  await bot.add_cog(QR(bot))
  await bot.add_cog(VanityRoles(bot))
  await bot.add_cog(ReactionRoles(bot))
  await bot.add_cog(Messages(bot))
  await bot.add_cog(TranslateCog(bot))
  await bot.add_cog(FastGreet(bot))
  await bot.add_cog(Jail(bot))
  await bot.add_cog(JoinToCreate(bot))
  await bot.add_cog(AI(bot))
  await bot.add_cog(StaffDMCog(bot))
  await bot.add_cog(Leveling(bot))
  await bot.add_cog(StickyMessage(bot))
  await bot.add_cog(Verification(bot))
  await bot.add_cog(Minecraft(bot))
  await bot.add_cog(encryption(bot))
  await bot.add_cog(calculator(bot))
  await bot.add_cog(joindm(bot))
  await bot.add_cog(Birthdays(bot))
  await bot.add_cog(Nitro(bot))
  await bot.add_cog(ImageCommands(bot))
  await bot.add_cog(Youtube(bot))

  await bot.add_cog(_antinuke(bot))
  await bot.add_cog(_extra(bot))
  await bot.add_cog(_general(bot))
  await bot.add_cog(_automod(bot))  
  await bot.add_cog(_moderation(bot))
  await bot.add_cog(_music(bot))
  await bot.add_cog(_fun(bot))
  await bot.add_cog(_games(bot))
  await bot.add_cog(_ignore(bot))
  await bot.add_cog(_server(bot))
  await bot.add_cog(_voice(bot))   
  await bot.add_cog(_welcome(bot))
  await bot.add_cog(_giveaway(bot))
  await bot.add_cog(_ticket(bot))
  await bot.add_cog(_logging(bot))
  await bot.add_cog(_vanity(bot))
  await bot.add_cog(inviteTracker(bot))
  await bot.add_cog(Counting(bot))
  await bot.add_cog(_Counting(bot))
  await bot.add_cog(_J2C(bot))
  await bot.add_cog(_ai(bot))
  await bot.add_cog(__boost(bot))
  await bot.add_cog(_leveling(bot))
  await bot.add_cog(_sticky(bot))
  await bot.add_cog(_verify(bot))
  await bot.add_cog(_encrypt(bot))
  await bot.add_cog(_mc(bot))
  await bot.add_cog(_joindm(bot))
  await bot.add_cog(_birth(bot))


  
  #await bot.add_cog(AutoBlacklist(bot))
  await bot.add_cog(Guild(bot))
  await bot.add_cog(Errors(bot))
  await bot.add_cog(Autorole2(bot))
  await bot.add_cog(Autorole(bot))
  await bot.add_cog(greet(bot))
  await bot.add_cog(AutoResponder(bot))
  await bot.add_cog(Mention(bot))
  await bot.add_cog(AutoRole(bot))
  await bot.add_cog(React(bot))
  await bot.add_cog(AutoReaction(bot))
  await bot.add_cog(AutoReactListener(bot))
  await bot.add_cog(NotifCommands(bot))
  await bot.add_cog(StickyMessageListener(bot))
  await bot.add_cog(AIResponses(bot))


  await bot.add_cog(AntiMemberUpdate(bot))
  await bot.add_cog(AntiBan(bot))
  await bot.add_cog(AntiBotAdd(bot))
  await bot.add_cog(AntiChannelCreate(bot))
  await bot.add_cog(AntiChannelDelete(bot))
  await bot.add_cog(AntiChannelUpdate(bot))
  await bot.add_cog(AntiEveryone(bot))
  await bot.add_cog(AntiGuildUpdate(bot))
  await bot.add_cog(AntiIntegration(bot))
  await bot.add_cog(AntiKick(bot))
  await bot.add_cog(AntiPrune(bot))
  await bot.add_cog(AntiRoleCreate(bot))
  await bot.add_cog(AntiRoleDelete(bot))
  await bot.add_cog(AntiRoleUpdate(bot))
  await bot.add_cog(AntiWebhookUpdate(bot))
  await bot.add_cog(AntiWebhookCreate(bot))
  await bot.add_cog(AntiWebhookDelete(bot))


#Extra Optional Events 

  #await bot.add_cog(AntiEmojiCreate(bot))
  #await bot.add_cog(AntiEmojiDelete(bot))
  #await bot.add_cog(AntiEmojiUpdate(bot))
  #await bot.add_cog(AntiSticker(bot))
  #await bot.add_cog(AntiUnban(bot))


  await bot.add_cog(AntiSpam(bot))
  await bot.add_cog(AntiCaps(bot))
  await bot.add_cog(AntiInvite(bot))
  await bot.add_cog(AntiLink(bot))
  await bot.add_cog(AntiMassMention(bot))
  await bot.add_cog(AntiEmojiSpam(bot))







  await bot.add_cog(Ban(bot))
  await bot.add_cog(Unban(bot))
  await bot.add_cog(Mute(bot))
  await bot.add_cog(Unmute(bot))
  await bot.add_cog(Lock(bot))
  await bot.add_cog(Unlock(bot))
  await bot.add_cog(Hide(bot))
  await bot.add_cog(Unhide(bot))
  await bot.add_cog(Kick(bot))
  await bot.add_cog(Warn(bot))
  await bot.add_cog(Role(bot))
  await bot.add_cog(Message(bot))
  await bot.add_cog(Moderation(bot))
  await bot.add_cog(TopCheck(bot))
  await bot.add_cog(Snipe(bot))
  


  for cog in cogs_to_load:
    print(Fore.RED + Style.BRIGHT + f"Loaded cog: {cog.__name__}")
  print(Fore.RED + Style.BRIGHT + f"All {BotName} Cogs loaded successfully.")
