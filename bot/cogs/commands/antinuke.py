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
from utils.emoji import CROSS, EMOTE, TICK, ZSAFE, ZSETTINGS
from discord.ext import commands
from discord.ui import LayoutView, TextDisplay, Separator, Container, Button, ActionRow
import aiosqlite
import asyncio
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import *




class Antinuke(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.loop.create_task(self.initialize_db())

  async def initialize_db(self):
    self.db = await aiosqlite.connect('db/anti.db')
    await self.db.execute('''
        CREATE TABLE IF NOT EXISTS antinuke (
            guild_id INTEGER PRIMARY KEY,
            status BOOLEAN
        )
    ''')
    await self.db.commit()

    
  async def enable_limit_settings(self, guild_id):
    default_limits = DEFAULT_LIMITS
    for action, limit in default_limits.items():
      await self.db.execute('INSERT OR REPLACE INTO limit_settings (guild_id, action_type, action_limit, time_window) VALUES (?, ?, ?, ?)', (guild_id, action, limit, TIME_WINDOW))
      await self.db.commit()

  async def disable_limit_settings(self, guild_id):
    await self.db.execute('DELETE FROM limit_settings WHERE guild_id = ?', (guild_id,))
    await self.db.commit()


  @commands.hybrid_command(name='antinuke', aliases=['antiwizz', 'anti'], help="Enables/Disables Anti-Nuke Module in the server")
  
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 4, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def antinuke(self, ctx, option: str = None):
    guild_id = ctx.guild.id
    pre=ctx.prefix

    async with self.db.execute('SELECT status FROM antinuke WHERE guild_id = ?', (guild_id,)) as cursor:
      row = await cursor.fetchone()

    async with self.db.execute(
            "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
            (ctx.guild.id, ctx.author.id)
        ) as cursor:
            check = await cursor.fetchone()

    is_owner = ctx.author.id == ctx.guild.owner_id
    if not is_owner and not check:
      view = CV2(f"{CROSS} Access Denied", "Only Server Owner or Extra Owner can Run this Command!")
      return await ctx.send(view=view)

    is_activated = row[0] if row else False

    if option is None:
      view = CV2(
        f"{ZSAFE} {BRAND_NAME} Security",
        "**Antinuke Defense Mode** — Protect your server from harmful admin actions with smart automated security protocols.",
        "**Core Functionalities**\n"
        "• Auto-ban malicious admin activities instantly.\n"
        "• Whitelist protection for trusted users.\n"
        "• Live monitoring of admin actions.\n"
        "• Rapid threat detection & neutralization.",
        "**Configuration Panel**\n"
        f"{TICK} Enable Protection: `antinuke enable`\n"
        f"{CROSS} Disable Protection: `antinuke disable`"
      )
      await ctx.send(view=view)

    elif option.lower() == 'enable':
      if is_activated:
        view = CV2(
          f"Security Settings For {ctx.guild.name}",
          f"Your server __**already has Antinuke enabled.**__\n\nCurrent Status: {TICK} Enabled\nTo Disable use `antinuke disable`"
        )
        await ctx.send(view=view)
      else:
        
        setup_view = CV2(f"Antinuke Setup {EMOTE}", f"{TICK} | Initializing Quick Setup!")
        setup_message = await ctx.send(view=setup_view)

        
        if not ctx.guild.me.guild_permissions.administrator:
          view = CV2(f"Antinuke Setup {EMOTE}",
            f"{TICK} | Initializing Quick Setup!\n"
            f"{CROSS} | **Ops! It seems I Don't Have Administrator Perm To enable antinuke**.")
          await setup_message.edit(view=view)
          return

        await asyncio.sleep(1)
        view = CV2(f"Antinuke Setup {EMOTE}",
          f"{TICK} | Initializing Quick Setup!\n"
          f"{TICK} Checking {BRAND_NAME}'s role position for optimal configuration...")
        await setup_message.edit(view=view)

        await asyncio.sleep(1)
        view = CV2(f"Antinuke Setup {EMOTE}",
          f"{TICK} | Initializing Quick Setup!\n"
          f"{TICK} Checking {BRAND_NAME}'s role position for optimal configuration...\n"
          f"{TICK} | Crafting and configuring the {BRAND_NAME} Supreme role...")
        await setup_message.edit(view=view)
        
        try:
          role = await ctx.guild.create_role(
            name=f"{BRAND_NAME} Supreme™",
            color=0xFF0000,
            permissions=discord.Permissions(administrator=True),
            hoist=False,
            mentionable=False,
            reason="Antinuke setup Role Creation"
          )
          await ctx.guild.me.add_roles(role)
        except discord.Forbidden:
          view = CV2("Antinuke Setup", f"{CROSS} | **Uh oh! I don't Have perms to enable antinuke**.")
          await setup_message.edit(view=view)
          return
        except discord.HTTPException as e:
          view = CV2("Antinuke Setup", f"{CROSS} | **Uh: HTTPException: {e}\nCheck Guild Audit Logs**.")
          await setup_message.edit(view=view)
          return

        await asyncio.sleep(1)
        view = CV2(f"Antinuke Setup {EMOTE}",
          f"{TICK} | Initializing Quick Setup!\n"
          f"{TICK} Checking {BRAND_NAME}'s role position...\n"
          f"{TICK} | Crafting the {BRAND_NAME} Supreme role...\n"
          f"{TICK} | Ensuring precise placement of the {BRAND_NAME} Supreme™ role...")
        await setup_message.edit(view=view)

        try:
          await ctx.guild.edit_role_positions(positions={role: 1})
        except discord.Forbidden:
          view = CV2("Antinuke Setup", f"{CROSS} | Ops! I don't have sufficient perms to move role.")
          await setup_message.edit(view=view)
          return
        except discord.HTTPException as e:
          view = CV2("Antinuke Setup", f"{CROSS} | Setup failed: HTTPException: {e}.")
          await setup_message.edit(view=view)
          return

        await asyncio.sleep(1)
        await asyncio.sleep(1)

        await self.db.execute('INSERT OR REPLACE INTO antinuke (guild_id, status) VALUES (?, ?)', (guild_id, True))
        await self.db.commit()

        await asyncio.sleep(1)
        await setup_message.delete()

        modules = (
          f"{TICK} **Anti Ban**\n"
          f"{TICK} **Anti Kick**\n"
          f"{TICK} **Anti Bot**\n"
          f"{TICK} **Anti Channel Create**\n"
          f"{TICK} **Anti Channel Delete**\n"
          f"{TICK} **Anti Channel Update**\n"
          f"{TICK} **Anti Everyone/Here**\n"
          f"{TICK} **Anti Role Create**\n"
          f"{TICK} **Anti Role Delete**\n"
          f"{TICK} **Anti Role Update**\n"
          f"{TICK} **Anti Member Update**\n"
          f"{TICK} **Anti Guild Update**\n"
          f"{TICK} **Anti Integration**\n"
          f"{TICK} **Anti Webhook Create**\n"
          f"{TICK} **Anti Webhook Delete**\n"
          f"{TICK} **Anti Webhook Update**\n"
          f"{TICK} **Anti Prune**\n"
          f"{TICK} **Auto Recovery**"
        )

        punishment_btn = Button(label="Show Punishment Type", style=discord.ButtonStyle.secondary)
        punishment_btn.callback = self._show_punishment

        result_view = LayoutView(timeout=None)
        result_view.add_item(
          build_container(
            TextDisplay(f"**{ZSETTINGS} Security Settings For {ctx.guild.name}**"),
            Separator(visible=True),
            TextDisplay("Tip: For optimal functionality, please ensure that my role has **Administration** permissions and is positioned at the **Top** of the roles list."),
            Separator(visible=True),
            TextDisplay(f"**Modules Enabled**\n{modules}"),
            Separator(visible=True),
            TextDisplay(f"Successfully Enabled Antinuke | Powered by {BRAND_NAME} Development™"),
            ActionRow(punishment_btn)
          )
        )

        await ctx.send(view=result_view)

    elif option.lower() == 'disable':
      if not is_activated:
        view = CV2(
          f"Security Settings For {ctx.guild.name}",
          f"Uhh, looks like your server hasn't enabled Antinuke.\n\nCurrent Status: {CROSS} Disabled\n\nTo Enable use `antinuke enable`"
        )
      else:
        await self.db.execute('DELETE FROM antinuke WHERE guild_id = ?', (guild_id,))
        await self.db.commit()
        view = CV2(
          f"Security Settings For {ctx.guild.name}",
          f"Successfully disabled Antinuke for this server.\n\nCurrent Status: {CROSS} Disabled\n\nTo Enable use `antinuke enable`"
        )
      await ctx.send(view=view)
    else:
      view = CV2(f"{CROSS} Error", "Invalid option. Please use `enable` or `disable`.")
      await ctx.send(view=view)

  async def _show_punishment(self, interaction: discord.Interaction):
    view = CV2(
      "Punishment Types for Unwhitelisted Admins/Mods",
      "**Anti Ban:** Ban\n"
      "**Anti Kick:** Ban\n"
      "**Anti Bot:** Ban the bot Inviter\n"
      "**Anti Channel Create/Delete/Update:** Ban\n"
      "**Anti Everyone/Here:** Remove the message & 1 hour timeout\n"
      "**Anti Role Create/Delete/Update:** Ban\n"
      "**Anti Member Update:** Ban\n"
      "**Anti Guild Update:** Ban\n"
      "**Anti Integration:** Ban\n"
      "**Anti Webhook Create/Delete/Update:** Ban\n"
      "**Anti Prune:** Ban\n"
      "**Auto Recovery:** Automatically recover damaged channels, roles, and settings",
      "Note: In the case of member updates, action will be taken only if the role contains dangerous permissions such as Ban Members, Administrator, Manage Guild, Manage Channels, Manage Roles, Manage Webhooks, or Mention Everyone"
    )
    await interaction.response.send_message(view=view, ephemeral=True)
