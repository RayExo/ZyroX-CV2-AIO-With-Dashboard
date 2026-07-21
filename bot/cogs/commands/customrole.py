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
from utils.emoji import CROSS, TICK, ZWARNING
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import aiosqlite
import asyncio
from utils.Tools import *
from utils.cv2 import CV2, build_container
from typing import List, Tuple
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.config import *



DATABASE_PATH = 'db/customrole.db'
DATABASE_PATH2 = 'db/np.db'


class Customrole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cooldown = {}
        self.rate_limit = {}
        self.rate_limit_timeout = 5


        self.bot.loop.create_task(self.create_tables())


    async def reset_rate_limit(self, user_id):
        await asyncio.sleep(self.rate_limit_timeout)
        self.rate_limit.pop(user_id, None)
        



    async def add_role(self, *, role_id: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=role_id)
            await member.add_roles(role, reason=f"{BRAND_NAME} Customrole | Role Added")
        else:
            raise discord.Forbidden("Bot does not have permission to manage roles.")



    async def remove_role(self, *, role_id: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=role_id)
            await member.remove_roles(role, reason=f"{BRAND_NAME} Customrole | Role Removed")
        else:
            raise discord.Forbidden("Bot does not have permission to manage roles.")
            


    async def add_role2(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.add_roles(role, reason=f"{BRAND_NAME} Customrole | Role Added ")

    async def remove_role2(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.remove_roles(role, reason=f"{BRAND_NAME} Customrole| Role Removed")

    

    async def handle_role_command(self, context: Context, member: discord.Member, role_type: str):
        async with aiosqlite.connect('db/customrole.db') as db:
            async with db.execute(f"SELECT reqrole, {role_type} FROM roles WHERE guild_id = ?", (context.guild.id,)) as cursor:
                data = await cursor.fetchone()
                if data:
                    reqrole_id, role_id = data
                    reqrole = context.guild.get_role(reqrole_id)
                    role = context.guild.get_role(role_id)

                    if reqrole:
                        if context.author == context.guild.owner or reqrole in context.author.roles:
                            if role:
                                if role not in member.roles:
                                    await self.add_role2(role=role_id, member=member)
                                    await context.reply(view=CV2(f"{TICK} Success", f"**Given** <@&{role.id}> To {member.mention}"))
                                else:
                                    await self.remove_role2(role=role_id, member=member)
                                    await context.reply(view=CV2(f"{TICK} Success", f"**Removed** <@&{role.id}> From {member.mention}"))
                            else:
                                await context.reply(view=CV2(f"{CROSS} Error", f"{role_type.capitalize()} role is not set up in {context.guild.name}"))
                        else:
                            await context.reply(view=CV2(f"{ZWARNING} Access Denied", f"You need {reqrole.mention} to run this command."))
                    else:
                        await context.reply(view=CV2(f"{ZWARNING} Access Denied", f"Required role is not set up in {context.guild.name}"))
                else:
                    await context.reply(view=CV2(f"{CROSS} Error", f"Roles configuration is not set up in {context.guild.name}"))

    


    async def create_tables(self):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    guild_id INTEGER PRIMARY KEY,
                    staff INTEGER,
                    girl INTEGER,
                    vip INTEGER,
                    guest INTEGER,
                    frnd INTEGER,
                    reqrole INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_roles (
                    guild_id INTEGER,
                    name TEXT,
                    role_id INTEGER,
                    PRIMARY KEY (guild_id, name)
                )
            ''')
            await db.commit()

    
    @commands.hybrid_group(name="setup",
                           description="Setups custom roles for the server.",
                           help="Setups custom roles for the server.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set(self, context: Context):
        if context.subcommand_passed is None:
            await context.send_help(context.command)
            context.command.reset_cooldown(context)

    async def fetch_role_data(self, guild_id):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT staff, girl, vip, guest, frnd, reqrole FROM roles WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchone()




    async def update_role_data(self, guild_id, column, value):
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute(f"INSERT OR REPLACE INTO roles (guild_id, {column}) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET {column} = ?",
                                 (guild_id, value, value))
                await db.commit()
        except Exception as e:
            print(f"Error updating role data: {e}")
            

    async def fetch_custom_role_data(self, guild_id):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT name, role_id FROM custom_roles WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchall()


    @set.command(name="staff",
                 description="Setup staff role in guild",
                 help="Setup staff role in Guild")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def staff(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'staff', role.id)
            await context.reply(view=CV2(f"{TICK} Success", f"Added {role.mention} to `Staff` Role\n\n__**How to Use?**__\nUse `staff <user>` Command to **Add {role.mention}** role to User & use again to the same user to **Remove role**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

    @set.command(name="girl",
                 description="Setup girl role in the Guild",
                 help="Setup girl role in the Guild")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def girl(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'girl', role.id)
            await context.reply(view=CV2(f"{TICK} Success", f"Added {role.mention} to `Girl` Role\n\n__**How to Use?**__\nUse `girl <user>` Command to **Add {role.mention}** role to User & use again to the same user to **Remove role**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

    @set.command(name="vip",
                 description="Setups vip role in the Guild",
                 help="Setups vip role in the Guild")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def vip(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'vip', role.id)
            await context.reply(view=CV2(f"{TICK} Success", f"Added {role.mention} to `VIP` Role\n\n__**How to Use?**__\nUse `vip <user>` Command to **Add {role.mention}** role to User & use again to the same user to **Remove role**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

    @set.command(name="guest",
                 description="Setup guest role in the Guild",
                 help="Setup guest role in the Guild")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def guest(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'guest', role.id)
            await context.reply(view=CV2(f"{TICK} Success", f"Added {role.mention} to `Guest` Role\n\n__**How to Use?**__\nUse `guest <user>` Command to **Add {role.mention}** role to User & use again to the same user to **Remove role**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

    @set.command(name="friend",
                 description="Setup friend role in the Guild",
                 help="Setup friend role in the Guild")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def friend(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'frnd', role.id)
            await context.reply(view=CV2(f"{TICK} Success", f"Added {role.mention} to `Friend` Role\n\n__**How to Use?**__\nUse `friend <user>` Command to **Add {role.mention}** role to User & use again to the same user to **Remove role**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

    @set.command(name="reqrole",
                 description="Setup required role for custom role commands",
                 help="Setup required role for custom role commands")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be added")
    async def req_role(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'reqrole', role.id)
            await context.reply(view=CV2(f"{TICK} Success", f"Added {role.mention} for Required role to run custom role commands in {context.guild.name}"))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

    

    @set.command(name="config",
                 description="Shows the current custom role configuration in the Guild.",
                 help="Shows the current custom role configuration in the Guild.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def config(self, context: Context) -> None:
        role_data = await self.fetch_role_data(context.guild.id)
        if role_data:
            staff = context.guild.get_role(role_data[0]).mention if role_data[0] else "None"
            girl = context.guild.get_role(role_data[1]).mention if role_data[1] else "None"
            vip = context.guild.get_role(role_data[2]).mention if role_data[2] else "None"
            guest = context.guild.get_role(role_data[3]).mention if role_data[3] else "None"
            friend = context.guild.get_role(role_data[4]).mention if role_data[4] else "None"
            reqrole = context.guild.get_role(role_data[5]).mention if role_data[5] else "None"
            config_text = (
                f"**Staff Role:** {staff}\n"
                f"**Girl Role:** {girl}\n"
                f"**VIP Role:** {vip}\n"
                f"**Guest Role:** {guest}\n"
                f"**Friend Role:** {friend}\n"
                f"**Required Role:** {reqrole}\n\n"
                "Use Commands to assign role & use again to the same user to remove role."
            )
            await context.reply(view=CV2("Custom Role Configuration", config_text))
        else:
            await context.reply(view=CV2(f"{CROSS} Error", "No custom role configuration found in this Guild."))



            


    @set.command(name="create",
                 description="Creates a custom role command.",
                 help="Creates a custom role command")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(name="Command name", role="Role to be assigned")
    async def create(self, context: Context, name: str, role: discord.Role) -> None:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM custom_roles WHERE guild_id = ?", (context.guild.id,)) as cursor:
                count = await cursor.fetchone()
                if count[0] >= 56:
                    await context.reply(view=CV2(f"{ZWARNING} Limit Reached", "You have reached the maximum limit of 56 custom role commands for this guild."))
                    return

            async with db.execute("SELECT name FROM custom_roles WHERE guild_id = ?", (context.guild.id,)) as cursor:
                existing_role = await cursor.fetchall()
                if any(name == row[0] for row in existing_role):
                    await context.reply(view=CV2(f"{CROSS} Error", f"A custom role command with the name `{name}` already exists in this guild. Remove it before creating a new one."))
                    return

            await db.execute("INSERT INTO custom_roles (guild_id, name, role_id) VALUES (?, ?, ?)",
                             (context.guild.id, name, role.id))
            await db.commit()

        await context.reply(view=CV2(f"{TICK} Success", f"Custom role command `{name}` created to assign the role {role.mention}.\n\n__**How to Use?**__\nUse `{name} <user>` Command to Assign/Remove {role.mention} role to User.\n> This will work for the users having `Manage Roles` permissions."))
        

    @set.command(name="delete", aliases=["remove"],
                 description="Deletes a custom role command.",
                 help="Deletes a custom role command.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(name="Command name to be deleted")
    async def delete(self, context: Context, name: str) -> None:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT name FROM custom_roles WHERE guild_id = ? AND name = ?", (context.guild.id, name)) as cursor:
                existing_role = await cursor.fetchone()

        if not existing_role:
            await context.reply(view=CV2(f"{CROSS} Error", f"No custom role command with the name `{name}` was found in this guild."))
            return

        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("DELETE FROM custom_roles WHERE guild_id = ? AND name = ?", (context.guild.id, name))
            await db.commit()

        await context.reply(view=CV2(f"{TICK} Success", f"Custom role command `{name}` has been deleted."))
        

    @set.command(
        name="list",
        description="List all the custom roles setup for the server.",
        help="List all the custom roles setup for the server."
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def list(self, context: Context) -> None:
        custom_roles = await self.fetch_custom_role_data(context.guild.id)

        if not custom_roles:
            await context.reply(view=CV2(f"{CROSS} Error", "No custom roles have been created for this server."))
            return

        
        def chunk_list(data: List[Tuple[str, int]], chunk_size: int):
            """Yield successive chunks of `chunk_size` from `data`."""
            for i in range(0, len(data), chunk_size):
                yield data[i:i + chunk_size]

        
        chunks = list(chunk_list(custom_roles, 7))

        for i, chunk in enumerate(chunks):
            roles_text = ""
            for name, role_id in chunk:
                role = context.guild.get_role(role_id)
                if role:
                    roles_text += f"**{name}** → {role.mention}\n"
            footer = f"Page {i+1}/{len(chunks)} | These commands are usable by Members having Manage Role permissions."
            await context.reply(view=CV2("Custom Roles", roles_text, footer))


    @set.command(name="reset",
         description="Resets custom role configuration for the server.",
         help="Resets custom role configuration for the server.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def reset(self, context: Context) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            removed_roles = []
            role_data = await self.fetch_role_data(context.guild.id)
            if role_data:
                roles = ["staff", "girl", "vip", "guest", "frnd", "reqrole"]
                for i, role_name in enumerate(roles):
                    role_id = role_data[i]
                    if role_id:
                        role = context.guild.get_role(role_id)
                        if role:
                            removed_roles.append(f"**{role_name.capitalize()}:** {role.mention}")
                            await self.update_role_data(context.guild.id, role_name, None)
                            
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("DELETE FROM custom_roles WHERE guild_id = ?", (context.guild.id,))
                    await db.commit()
                    reset_desc = f"Deleted All Custom Role commands {TICK}\n\n**Removed Roles:**\n" + "\n".join(removed_roles) if removed_roles else "No roles were previously set."
                    await context.reply(view=CV2("Custom Role Configuration Reset", reset_desc))
            else:
                await context.reply(view=CV2("Info", "No configuration found for this server."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Access Denied", "Your role should be above my top role."))

        
            

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot or not message.content:
            return

        prefixes = await self.bot.get_prefix(message)

        
        if not prefixes:
            return

        
        if not any(message.content.startswith(prefix) for prefix in prefixes):
            return

        
        for prefix in prefixes:
            if message.content.startswith(prefix):
                command_name = message.content[len(prefix):].split()[0] 
                break
        else:
            return

        guild_id = message.guild.id

        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT role_id FROM custom_roles WHERE guild_id = ? AND name = ?", (guild_id, command_name)) as cursor:
                result = await cursor.fetchone()

        if result:
            role_id = result[0]
            role = message.guild.get_role(role_id)

            
            async with aiosqlite.connect(DATABASE_PATH) as db:
                async with db.execute("SELECT reqrole FROM roles WHERE guild_id = ?", (guild_id,)) as cursor:
                    reqrole_result = await cursor.fetchone()

            reqrole_id = reqrole_result[0] if reqrole_result else None
            reqrole = message.guild.get_role(reqrole_id) if reqrole_id else None

            
            if reqrole is None:
                await message.channel.send(f"{ZWARNING} The required role is not set up in this server. Please set it up using `setup reqrole`.")
                return

            
            if reqrole not in message.author.roles:
                await message.channel.send(view=CV2(f"{ZWARNING} Access Denied", f"You need the {reqrole.mention} role to use this command."))
                return

            
            member = message.mentions[0] if message.mentions else None
            if not member:
                await message.channel.send("Please mention a user to assign the role.")
                return

            
            now = asyncio.get_event_loop().time()
            if guild_id not in self.cooldown or now - self.cooldown[guild_id] >= 10:
                self.cooldown[guild_id] = now
            else:
                await message.channel.send("You're on a cooldown of 5 seconds. Please wait before sending another command.", delete_after=5)
                return

            try:
                if role in member.roles:
                    await self.remove_role(role_id=role_id, member=member)
                    await message.channel.send(view=CV2(f"{TICK} Success", f"**Removed** the role {role.mention} from {member.mention}."))
                else:
                    await self.add_role(role_id=role_id, member=member)
                    await message.channel.send(view=CV2(f"{TICK} Success", f"**Added** the role {role.mention} to {member.mention}."))
            except discord.Forbidden as e:
                await message.channel.send("I do not have permission to manage this role to the given user.")
                print(f"Error: {e}")
        else:
            return

    

    @commands.hybrid_command(name="staff",
         description="Gives the staff role to the user.",
         aliases=['official'],
         help="Gives the staff role to the user.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _staff(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'staff')

    @commands.hybrid_command(name="girl",
         description="Gives the girl role to the user.",
         aliases=['qt'],
         help="Gives the girl role to the user.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _girl(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'girl')

    @commands.hybrid_command(name="vip",
         description="Gives the VIP role to the user.",
         help="Gives the VIP role to the user.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _vip(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'vip')

    @commands.hybrid_command(name="guest",
         description="Gives the guest role to the user.",
         help="Gives the guest role to the user.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _guest(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'guest')

    @commands.hybrid_command(name="friend",
         description="Gives the friend role to the user.",
         aliases=['frnd'],
         help="Gives the friend role to the user.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _friend(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'frnd')


 