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
from discord .ext import commands 
import aiosqlite 
import asyncio 
import json 
import re 
import random 
import math 
from datetime import datetime ,timezone ,timedelta 
from typing import Optional ,Dict ,List ,Tuple 
try :
    from PIL import Image ,ImageDraw ,ImageFont ,ImageFilter ,ImageEnhance 
    PIL_AVAILABLE =True 
except ImportError :
    PIL_AVAILABLE =False 
import io 
import os 
import requests 
import logging 


logger =logging .getLogger ('discord')


def utc_to_local (dt :datetime )->datetime :
    return dt .replace (tzinfo =timezone .utc )

def format_number (num :int )->str :
    """Format numbers with commas for better readability"""
    return f"{num:,}"

def calculate_level_from_xp (xp :int )->int :
    """Calculate level from XP using standard formula"""
    if xp <0 :
        return 0 
    return int (math .sqrt (xp /100 ))

def calculate_xp_for_level (level :int )->int :
    """Calculate XP required for a specific level"""
    return level *level *100 

def get_level_progress (xp :int )->tuple :
    """Get current level, XP for current level, and XP for next level"""
    current_level =calculate_level_from_xp (xp )
    current_level_xp =calculate_xp_for_level (current_level )
    next_level_xp =calculate_xp_for_level (current_level +1 )
    progress =xp -current_level_xp 
    needed =next_level_xp -current_level_xp 
    return current_level ,progress ,needed 

def get_progress_bar (current :int ,total :int ,length :int =10 )->str :
    """Create a visual progress bar"""
    if total ==0 :
        return "▱"*length 
    filled =int ((current /total )*length )
    return "▰"*filled +"▱"*(length -filled )

def validate_hex_color (color :str )->bool :
    """Validate hex color format"""
    if not color .startswith ('#'):
        return False 
    return bool (re .match (r'^#(?:[0-9a-fA-F]{3}){1,2}$',color ))

def hex_to_int (hex_color :str )->int :
    """Convert hex color to integer"""
    try :
        if not hex_color .startswith ('#'):
            hex_color ='#'+hex_color 
        return int (hex_color .lstrip ('#'),16 )
    except (ValueError ,TypeError ):
        return 0xFF0000 

class PlaceholdersView (discord .ui .View ):
    def __init__ (self ):
        super ().__init__ (timeout =60 )

    @discord .ui .button (label ="Show Placeholders",style =discord .ButtonStyle .secondary ,emoji ="📝")
    async def show_placeholders (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        embed =discord .Embed (
        title ="📝 Available Placeholders",
        description ="**You can use these placeholders in your level up message:**\n\n"
        "`{user}` - Mentions the user (@username)\n"
        "`{username}` - User's display name\n"
        "`{level}` - The new level reached\n"
        "`{server}` - Server name\n\n"
        "**Example:**\n"
        "`Congratulations {user}! You've reached level {level} in {server}!`",
        color =0xFF0000 ,
        timestamp =datetime .now (timezone .utc )
        )
        await interaction .response .send_message (embed =embed ,ephemeral =True )

class LevelConfigModal (discord .ui .Modal ,title ="Leveling System Configuration"):
    def __init__ (self ,cog ,current_settings ):
        super ().__init__ ()

        self .cog =cog 


        self .xp_per_message =discord .ui .TextInput (
        label ="XP per Message",
        placeholder ="Amount of XP per message (default: 20)",
        default =str (current_settings .get ('xp_per_message',20 )),
        required =True ,
        max_length =3 
        )

        self .level_up_message =discord .ui .TextInput (
        label ="Level Up Message",
        placeholder ="Use {user}, {level}, {username}, {server} as placeholders",
        default =current_settings .get ('level_message','Congratulations {user}! You have reached level {level}!'),
        required =True ,
        style =discord .TextStyle .paragraph ,
        max_length =2000 
        )


        current_color =current_settings .get ('embed_color','#000000')
        if isinstance (current_color ,int ):
            current_color =f"#{current_color:06x}"
        elif not isinstance (current_color ,str ):
            current_color ='#000000'


        if not current_color .startswith ('#'):
            current_color ='#000000'

        self .embed_color =discord .ui .TextInput (
        label ="Embed Color (Hex)",
        placeholder ="#FF0000",
        default =current_color ,
        required =True ,
        max_length =7 
        )

        self .level_up_image =discord .ui .TextInput (
        label ="Level Up Image URL (Optional)",
        placeholder ="Direct image URL for level up embeds",
        default =current_settings .get ('level_image',''),
        required =False ,
        max_length =500 
        )

        self .thumbnail_enabled =discord .ui .TextInput (
        label ="Show User Avatar Thumbnail (true/false)",
        placeholder ="true or false",
        default =str (current_settings .get ('thumbnail_enabled',True )).lower (),
        required =True ,
        max_length =5 
        )

        self .add_item (self .xp_per_message )
        self .add_item (self .level_up_message )
        self .add_item (self .embed_color )
        self .add_item (self .level_up_image )
        self .add_item (self .thumbnail_enabled )

    async def on_submit (self ,interaction :discord .Interaction ):
        try :
            if not interaction or not hasattr (interaction ,'response'):
                logger .error ("Invalid interaction object in LevelConfigModal")
                return 

            await interaction .response .defer (ephemeral =True )


            try :
                xp_value =int (self .xp_per_message .value )
                if xp_value <1 or xp_value >999 :
                    raise ValueError ("XP per message must be between 1 and 999")
            except ValueError as ve :
                logger .error (f"XP validation error: {ve}")
                await interaction .followup .send (f"{CROSS} Invalid XP per message value! Must be between 1 and 999.",ephemeral =True )
                return 


            color_value =self .embed_color .value .strip ()
            if not color_value .startswith ('#'):
                color_value ='#'+color_value 

            if not validate_hex_color (color_value ):
                await interaction .followup .send (f"{CROSS} Invalid hex color format! Use format like #FF0000",ephemeral =True )
                return 

            thumbnail_bool =self .thumbnail_enabled .value .lower ()in ['true','yes','1','on']


            try :
                embed_color_int =hex_to_int (color_value )
            except Exception as e :
                logger .error (f"Color conversion error: {e}")
                embed_color_int =0 


            image_value =self .level_up_image .value .strip ()if self .level_up_image .value and self .level_up_image .value .strip ()else None 


            try :
                async with aiosqlite .connect ("db/leveling.db")as db :

                    async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(interaction .guild .id ,))as cursor :
                        exists =await cursor .fetchone ()

                    if exists :

                        await db .execute ("""
                            UPDATE leveling_settings 
                            SET enabled = ?, xp_per_message = ?, level_message = ?, embed_color = ?, 
                                level_image = ?, thumbnail_enabled = ?
                            WHERE guild_id = ?
                        """,(
                        1 ,
                        xp_value ,
                        self .level_up_message .value ,
                        embed_color_int ,
                        image_value ,
                        1 if thumbnail_bool else 0 ,
                        interaction .guild .id 
                        ))
                        logger .info (f"Updated settings for guild {interaction.guild.id}")
                    else :

                        await db .execute ("""
                            INSERT INTO leveling_settings 
                            (guild_id, enabled, xp_per_message, level_message, embed_color, level_image, thumbnail_enabled,
                             min_xp, max_xp, cooldown_seconds, dm_level_up, channel_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,(
                        interaction .guild .id ,
                        1 ,
                        xp_value ,
                        self .level_up_message .value ,
                        embed_color_int ,
                        image_value ,
                        1 if thumbnail_bool else 0 ,
                        15 ,
                        25 ,
                        60 ,
                        0 ,
                        None 
                        ))
                        logger .info (f"Created new settings for guild {interaction.guild.id}")

                    await db .commit ()
                    logger .info (f"Settings saved successfully for guild {interaction.guild.id}")

            except Exception as e :
                return 


            embed =discord .Embed (
            title =f"{TICK} Leveling Configuration Updated",
            description =f"**XP per Message:** {xp_value}\n"
            f"**Level Up Message:** {self.level_up_message.value[:50]}{'...' if len(self.level_up_message.value) > 50 else ''}\n"
            f"**Embed Color:** {color_value}\n"
            f"**Level Up Image:** {'Set' if image_value else 'None'}\n"
            f"**Thumbnail Enabled:** {thumbnail_bool}",
            color =0xFF0000 ,
            timestamp =datetime .now (timezone .utc )
            )


            view =PlaceholdersView ()
            await interaction .followup .send (embed =embed ,view =view ,ephemeral =True )

        except Exception as e :
            logger .error (f"Critical error in LevelConfigModal: {e}")
            await interaction .followup .send (
            f"{CROSS} An unexpected error occurred: {str(e)}",
            ephemeral =True 
            )

class Leveling (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .message_cooldowns ={}
        self .last_level_cache ={}
        self .db_path ="db/leveling.db"

    @commands.group (name ="level",invoke_without_command =True ,description ="Leveling system")
    async def level (self ,ctx ):
        """Main leveling command"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    async def cog_load (self ):
        """Initialize database tables"""
        try :
            await self .init_database ()

        except Exception as e :
            logger .error (f"Error loading Leveling cog: {e}")

    async def init_database (self ):
        """Initialize all required database tables"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :

                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS user_xp (
                        guild_id INTEGER,
                        user_id INTEGER,
                        xp INTEGER DEFAULT 0,
                        messages INTEGER DEFAULT 0,
                        last_message_time TEXT,
                        PRIMARY KEY (guild_id, user_id)
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS leveling_settings (
                        guild_id INTEGER PRIMARY KEY,
                        enabled INTEGER DEFAULT 0,
                        channel_id INTEGER,
                        level_message TEXT DEFAULT 'Congratulations {user}! You have reached level {level}!',
                        embed_color INTEGER DEFAULT 0,
                        level_image TEXT,
                        thumbnail_enabled INTEGER DEFAULT 1,
                        xp_per_message INTEGER DEFAULT 20,
                        min_xp INTEGER DEFAULT 15,
                        max_xp INTEGER DEFAULT 25,
                        cooldown_seconds INTEGER DEFAULT 60,
                        dm_level_up INTEGER DEFAULT 0
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS level_rewards (
                        guild_id INTEGER,
                        level INTEGER,
                        role_id INTEGER,
                        remove_previous INTEGER DEFAULT 0,
                        PRIMARY KEY (guild_id, level)
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS xp_multipliers (
                        guild_id INTEGER,
                        target_id INTEGER,
                        target_type TEXT,
                        multiplier REAL,
                        PRIMARY KEY (guild_id, target_id, target_type)
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS leveling_blacklist (
                        guild_id INTEGER,
                        target_id INTEGER,
                        target_type TEXT,
                        PRIMARY KEY (guild_id, target_id, target_type)
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS users (
                        guild_id INTEGER,
                        user_id INTEGER,
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        PRIMARY KEY (guild_id, user_id)
                    )
                """)

                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS level_roles (
                        guild_id INTEGER,
                        level INTEGER,
                        role_id INTEGER,
                        PRIMARY KEY (guild_id, level)
                    )
                """)


                async with db .cursor ()as cursor :

                    await cursor .execute ("PRAGMA table_info(leveling_blacklist)")
                    columns =[col [1 ]for col in await cursor .fetchall ()]
                    if "target_type"not in columns :
                        await cursor .execute ("ALTER TABLE leveling_blacklist ADD COLUMN target_type TEXT")
                        logger .info ("Added target_type column to leveling_blacklist table")

                await db .commit ()
        except Exception as e :
            logger .error (f"Database initialization error: {e}")

    async def get_guild_settings (self ,guild_id :int )->dict :
        """Get guild leveling settings"""
        max_retries =5 
        for attempt in range (max_retries ):
            try :
                async with aiosqlite .connect ("db/leveling.db")as db :
                    async with db .execute ("SELECT * FROM leveling_settings WHERE guild_id = ?",(guild_id ,))as cursor :
                        row =await cursor .fetchone ()

                    if not row :

                        async with aiosqlite .connect ("db/leveling.db")as db :
                            await db .execute ("INSERT INTO leveling_settings (guild_id, enabled) VALUES (?, 0)",(guild_id ,))
                            await db .commit ()
                        return {
                        'enabled':False ,'channel_id':None ,
                        'level_message':'Congratulations {user}! You have reached level {level}!',
                        'embed_color':'#000000','level_image':None ,'thumbnail_enabled':True ,
                        'xp_per_message':20 ,'min_xp':15 ,'max_xp':25 ,'cooldown_seconds':60 ,
                        'dm_level_up':False 
                        }


                    embed_color =row [4 ]if len (row )>4 and row [4 ]is not None else 0 
                    if isinstance (embed_color ,int ):
                        color_hex =f"#{embed_color:06x}"
                    else :
                        color_hex ='#FF0000'


                    return {
                    'enabled':bool (row [1 ])if len (row )>1 else False ,
                    'channel_id':row [2 ]if len (row )>2 else None ,
                    'level_message':row [3 ]if len (row )>3 else 'Congratulations {user}! You have reached level {level}!',
                    'embed_color':color_hex ,
                    'level_image':row [5 ]if len (row )>5 else None ,
                    'thumbnail_enabled':bool (row [6 ])if len (row )>6 else True ,
                    'xp_per_message':row [7 ]if len (row )>7 else 20 ,
                    'min_xp':row [8 ]if len (row )>8 else 15 ,
                    'max_xp':row [9 ]if len (row )>9 else 25 ,
                    'cooldown_seconds':row [10 ]if len (row )>10 else 60 ,
                    'dm_level_up':bool (row [11 ])if len (row )>11 else False 
                    }

            except aiosqlite .OperationalError as e :
                if attempt <max_retries -1 :
                    logger .warning (f"Database locked, retrying... (attempt {attempt + 1})")
                    await asyncio .sleep (0.1 *(attempt +1 ))
                    continue 
                else :
                    logger .error (f"Database error after {max_retries} attempts: {e}")
                    break 
            except Exception as e :
                logger .error (f"Error getting guild settings: {e}")
                break 


        return {
        'enabled':False ,'channel_id':None ,
        'level_message':'Congratulations {user}! You have reached level {level}!',
        'embed_color':'#000000','level_image':None ,'thumbnail_enabled':True ,
        'xp_per_message':20 ,'min_xp':15 ,'max_xp':25 ,'cooldown_seconds':60 ,
        'dm_level_up':False 
        }

    async def is_blacklisted (self ,guild_id :int ,user_id :int ,channel_id :int )->bool :
        """Check if user or channel is blacklisted"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :

                async with db .cursor ()as cursor :
                    await cursor .execute ("PRAGMA table_info(leveling_blacklist)")
                    columns =[col [1 ]for col in await cursor .fetchall ()]

                    if "target_type"not in columns :

                        logger .warning ("target_type column missing from leveling_blacklist table")
                        return False 


                async with db .execute (
                "SELECT 1 FROM leveling_blacklist WHERE guild_id = ? AND target_id = ? AND target_type = 'channel'",
                (guild_id ,channel_id )
                )as cursor :
                    if await cursor .fetchone ():
                        return True 


                guild =self .bot .get_guild (guild_id )
                if guild :
                    member =guild .get_member (user_id )
                    if member :
                        async with db .execute (
                        "SELECT target_id FROM leveling_blacklist WHERE guild_id = ? AND target_type = 'role'",
                        (guild_id ,)
                        )as cursor :
                            blacklisted_roles =[row [0 ]for row in await cursor .fetchall ()]
                            if any (role .id in blacklisted_roles for role in member .roles ):
                                return True 
                return False 
        except Exception as e :
            logger .error (f"Error checking blacklist: {e}")
            return False 

    async def get_xp_multiplier (self ,guild_id :int ,user_id :int ,channel_id :int )->float :
        """Get XP multiplier for user"""
        try :
            guild =self .bot .get_guild (guild_id )
            if not guild :
                return 1.0 

            member =guild .get_member (user_id )
            if not member :
                return 1.0 

            total_multiplier =1.0 
            async with aiosqlite .connect ("db/leveling.db")as db :

                async with db .execute (
                "SELECT target_id, multiplier FROM xp_multipliers WHERE guild_id = ? AND target_type = 'role'",
                (guild_id ,)
                )as cursor :
                    role_multipliers =await cursor .fetchall ()

                for role_id ,multiplier in role_multipliers :
                    if any (role .id ==role_id for role in member .roles ):
                        total_multiplier *=multiplier 


                async with db .execute (
                "SELECT multiplier FROM xp_multipliers WHERE guild_id = ? AND target_id = ? AND target_type = 'channel'",
                (guild_id ,channel_id )
                )as cursor :
                    channel_mult =await cursor .fetchone ()
                    if channel_mult :
                        total_multiplier *=channel_mult [0 ]

            return total_multiplier 
        except Exception as e :
            logger .error (f"Error getting XP multiplier: {e}")
            return 1.0 

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        """Handle message XP tracking with independent message tracking system"""
        if message .author .bot or not message .guild :
            return 

        guild_id =message .guild .id 
        user_id =message .author .id 
        channel_id =message .channel .id 


        cooldown_key =f"{guild_id}_{user_id}"
        now =datetime .now ()

        if cooldown_key in self .message_cooldowns :
            if now <self .message_cooldowns [cooldown_key ]:
                return 

        try :
            settings =await self .get_guild_settings (guild_id )
            if not settings .get ('enabled',False ):
                return 

            if await self .is_blacklisted (guild_id ,user_id ,channel_id ):
                return 


            cooldown_seconds =settings .get ('cooldown_seconds',60 )
            self .message_cooldowns [cooldown_key ]=now +timedelta (seconds =cooldown_seconds )


            base_xp =settings .get ('xp_per_message',20 )
            if base_xp is None :
                base_xp =20 

            final_xp =base_xp 


            multiplier =await self .get_xp_multiplier (guild_id ,user_id ,channel_id )
            if multiplier is None :
                multiplier =1.0 

            final_xp =int (final_xp *multiplier )


            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT xp, messages FROM user_xp WHERE guild_id = ? AND user_id = ?",
                (guild_id ,user_id )
                )as cursor :
                    row =await cursor .fetchone ()

                if row and len (row )>=2 :
                    current_xp =row [0 ]if row [0 ]is not None else 0 
                    current_messages =row [1 ]if row [1 ]is not None else 0 
                    old_level =calculate_level_from_xp (current_xp )
                    new_xp =current_xp +final_xp 
                    new_level =calculate_level_from_xp (new_xp )
                    new_messages =current_messages +1 

                    await db .execute ("""
                        UPDATE user_xp 
                        SET xp = ?, messages = ?, last_message_time = ?
                        WHERE guild_id = ? AND user_id = ?
                    """,(new_xp ,new_messages ,now .isoformat (),guild_id ,user_id ))
                else :
                    old_level =0 
                    new_level =calculate_level_from_xp (final_xp )
                    new_messages =1 

                    await db .execute ("""
                        INSERT INTO user_xp (guild_id, user_id, xp, messages, last_message_time)
                        VALUES (?, ?, ?, ?, ?)
                    """,(guild_id ,user_id ,final_xp ,new_messages ,now .isoformat ()))


                current_new_xp =new_xp if 'new_xp'in locals ()else final_xp 
                current_new_level =new_level if 'new_level'in locals ()else calculate_level_from_xp (final_xp )
                await db .execute ("""
                    INSERT OR REPLACE INTO users (guild_id, user_id, xp, level)
                    VALUES (?, ?, ?, ?)
                """,(guild_id ,user_id ,current_new_xp ,current_new_level ))

                await db .commit ()


            if new_level >old_level :
                await self .handle_level_up (message ,new_level ,settings )

        except Exception as e :
            logger .error (f"Error handling message XP: {e}")

    async def handle_level_up (self ,message ,new_level ,settings ):
        """Handle level up notification and rewards"""
        try :

            channel_id =settings .get ('channel_id')
            channel =None 

            if channel_id :
                channel =self .bot .get_channel (channel_id )

                if channel and not channel .permissions_for (message .guild .me ).send_messages :
                    logger .warning (f"No permission to send messages in configured level channel {channel_id}")
                    channel =None 


            if not channel :
                if not channel_id :

                    channel =message .channel 
                else :

                    logger .error (f"Configured level channel {channel_id} not found or not accessible")
                    return 


            level_message =settings .get ('level_message','Congratulations {user}! You have reached level {level}!')
            level_message =level_message .replace ('{user}',message .author .mention )
            level_message =level_message .replace ('{level}',str (new_level ))
            level_message =level_message .replace ('{username}',message .author .display_name )
            level_message =level_message .replace ('{server}',message .guild .name )


            embed_color =settings .get ('embed_color','#FF0000')
            if isinstance (embed_color ,str ):
                embed_color =hex_to_int (embed_color )

            embed =discord .Embed (
            title ="🎉 Level Up!",
            description =level_message ,
            color =0xFF0000 ,
            timestamp =datetime .now (timezone .utc )
            )

            if settings .get ('thumbnail_enabled',True ):
                embed .set_thumbnail (url =message .author .display_avatar .url )

            if settings .get ('level_image'):
                embed .set_image (url =settings ['level_image'])

            embed .set_footer (text =f"Level {new_level} • {message.guild.name}")

            try :
                await channel .send (embed =embed )
                logger .info (f"Level up message sent for {message.author} (Level {new_level}) in channel {channel.id}")
            except discord .Forbidden :
                logger .error (f"No permission to send level up message in channel {channel.id}")
            except discord .NotFound :
                logger .error (f"Level up channel {channel.id} not found")
            except Exception as e :
                logger .error (f"Error sending level up message: {e}")


            await self .give_level_rewards (message .guild ,message .author ,new_level )


            await self .apply_level_roles (message .guild ,message .author ,new_level )

        except Exception as e :
            logger .error (f"Error handling level up: {e}")

    async def give_level_rewards (self ,guild ,member ,level ):
        """Give role rewards for reaching a level"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT role_id, remove_previous FROM level_rewards WHERE guild_id = ? AND level <= ? ORDER BY level DESC",
                (guild .id ,level )
                )as cursor :
                    rewards =await cursor .fetchall ()

            for role_id ,remove_previous in rewards :
                role =guild .get_role (role_id )
                if role and role not in member .roles :
                    await member .add_roles (role ,reason =f"Level {level} reward")

                    if remove_previous :

                        async with aiosqlite .connect ("db/leveling.db")as db :
                            async with db .execute (
                            "SELECT role_id FROM level_rewards WHERE guild_id = ? AND level < ?",
                            (guild .id ,level )
                            )as cursor :
                                prev_rewards =await cursor .fetchall ()

                        for prev_role_id ,in prev_rewards :
                            prev_role =guild .get_role (prev_role_id )
                            if prev_role and prev_role in member .roles :
                                await member .remove_roles (prev_role ,reason =f"Upgraded to level {level}")

        except Exception as e :
            logger .error (f"Error giving level rewards: {e}")

    async def apply_level_roles (self ,guild ,member ,level ):
        """Apply level roles for reaching a level"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT role_id FROM level_roles WHERE guild_id = ? AND level <= ? ORDER BY level DESC",
                (guild .id ,level )
                )as cursor :
                    level_roles =await cursor .fetchall ()

            for role_id ,in level_roles :
                role =guild .get_role (role_id )
                if role and role not in member .roles :
                    try :
                        await member .add_roles (role ,reason =f"Reached level {level}")
                    except discord .Forbidden :
                        logger .warning (f"No permission to add role {role.name} to {member}")
                    except Exception as e :
                        logger .error (f"Error adding level role {role_id}: {e}")

        except Exception as e :
            logger .error (f"Error applying level roles: {e}")

    async def get_user_data (self ,guild_id :int ,user_id :int )->tuple :
        """Get user XP and level data"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT xp, messages FROM user_xp WHERE guild_id = ? AND user_id = ?",
                (guild_id ,user_id )
                )as cursor :
                    row =await cursor .fetchone ()
                    if row :
                        xp ,messages =row 
                        level =calculate_level_from_xp (xp if xp is not None else 0 )
                        return xp if xp is not None else 0 ,level ,messages if messages is not None else 0 
                    return 0 ,0 ,0 
        except Exception as e :
            logger .error (f"Error getting user data: {e}")
            return 0 ,0 ,0 

    async def get_user_rank (self ,guild_id :int ,user_id :int )->int :
        """Get user's rank in the guild"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT COUNT(*) + 1 FROM user_xp WHERE guild_id = ? AND xp > (SELECT COALESCE(xp, 0) FROM user_xp WHERE guild_id = ? AND user_id = ?)",
                (guild_id ,guild_id ,user_id )
                )as cursor :
                    rank =(await cursor .fetchone ())[0 ]
                    return rank 
        except Exception as e :
            logger .error (f"Error getting user rank: {e}")
            return 1 

    def create_simple_rank_card (self ,member ,xp ,level ,rank ,messages ):
        """Create a simple text-based rank card when PIL fails"""
        try :
            current_level ,progress ,needed =get_level_progress (xp )
            progress_bar =get_progress_bar (progress ,needed ,20 )

            rank_text =f"""
┌─────────────────────────────────────────┐
│ 🎮 RANK CARD - {member.display_name[:20]}
├─────────────────────────────────────────┤
│ 📊 Rank: #{rank:,}
│ ⭐ Level: {level:,}
│ 💬 Messages: {messages:,}
│ 🎯 XP: {xp:,}
├─────────────────────────────────────────┤
│ Progress to Level {level + 1}:
│ {progress_bar}
│ {progress:,} / {needed:,} XP
└─────────────────────────────────────────┘
            """
            return rank_text .strip ()
        except Exception as e :
            logger .error (f"Error creating simple rank card: {e}")
            return f"**{member.display_name}** - Level {level} - Rank #{rank}"

    async def create_rank_card (self ,member ,guild_id ):
        """Create rank card with random design selection - fallback to text if PIL fails"""
        try :
            xp ,level ,messages =await self .get_user_data (guild_id ,member .id )
            rank =await self .get_user_rank (guild_id ,member .id )


            if PIL_AVAILABLE :
                try :

                    design_number =random .randint (1 ,7 )
                    return await self .create_rank_card_design (member ,xp ,level ,rank ,messages ,design_number )

                except Exception as e :
                    logger .error (f"PIL error, falling back to text: {e}")

                    return self .create_simple_rank_card (member ,xp ,level ,rank ,messages )
            else :

                logger .warning ("PIL not available, using text-based rank card")
                return self .create_simple_rank_card (member ,xp ,level ,rank ,messages )

        except Exception as e :
            logger .error (f"Error creating rank card: {e}")
            return None 

    async def create_rank_card_design (self ,member ,xp ,level ,rank ,messages ,design_number ):
        """Create specific rank card design based on design number"""
        current_level ,progress ,needed =get_level_progress (xp )
        width ,height =900 ,300 


        try :
            font_large =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",28 )
            font_medium =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20 )
            font_small =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16 )
        except (OSError ,IOError ):
            font_large =ImageFont .load_default ()
            font_medium =ImageFont .load_default ()
            font_small =ImageFont .load_default ()

        if design_number ==1 :
            return await self .create_classic_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )
        elif design_number ==2 :
            return await self .create_neon_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )
        elif design_number ==3 :
            return await self .create_space_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )
        elif design_number ==4 :
            return await self .create_minimal_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )
        elif design_number ==5 :
            return await self .create_gaming_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )
        elif design_number ==6 :
            return await self .create_elegant_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )
        else :
            return await self .create_cyberpunk_design (member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )

    async def create_classic_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Original design with diagonal gradient"""
        img =Image .new ('RGB',(width ,height ),(32 ,34 ,37 ))
        draw =ImageDraw .Draw (img )


        color_schemes =[
        [(45 ,52 ,54 ),(99 ,110 ,114 )],
        [(74 ,144 ,226 ),(80 ,227 ,194 )],
        [(245 ,166 ,35 ),(242 ,112 ,156 )],
        [(165 ,94 ,234 ),(74 ,144 ,226 )],
        [(255 ,118 ,117 ),(255 ,204 ,128 )],
        [(18 ,194 ,233 ),(196 ,113 ,237 )],
        ]

        scheme =color_schemes [level %len (color_schemes )]


        for x in range (width ):
            for y in range (height ):
                factor_x =x /width 
                factor_y =y /height 
                factor =(factor_x +factor_y )/2 

                r =int (scheme [0 ][0 ]+(scheme [1 ][0 ]-scheme [0 ][0 ])*factor )
                g =int (scheme [0 ][1 ]+(scheme [1 ][1 ]-scheme [0 ][1 ])*factor )
                b =int (scheme [0 ][2 ]+(scheme [1 ][2 ]-scheme [0 ][2 ])*factor )
                draw .point ((x ,y ),fill =(r ,g ,b ))


        draw .rounded_rectangle ((15 ,15 ,width -15 ,height -15 ),radius =20 ,fill =(0 ,0 ,0 ,100 ))
        draw .rounded_rectangle ((15 ,15 ,width -15 ,height -15 ),radius =20 ,outline =(255 ,255 ,255 ,50 ),width =2 )


        await self .add_avatar_and_content_classic (draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )


        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def create_neon_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Neon cyberpunk style design"""
        img =Image .new ('RGB',(width ,height ),(10 ,10 ,25 ))
        draw =ImageDraw .Draw (img )


        grid_color =(0 ,255 ,255 ,30 )
        for x in range (0 ,width ,50 ):
            draw .line ([(x ,0 ),(x ,height )],fill =grid_color ,width =1 )
        for y in range (0 ,height ,50 ):
            draw .line ([(0 ,y ),(width ,y )],fill =grid_color ,width =1 )


        for i in range (5 ):
            draw .rounded_rectangle ((15 -i ,15 -i ,width -15 +i ,height -15 +i ),radius =20 +i ,outline =(0 ,255 ,255 ,50 -i *10 ),width =1 )


        draw .rounded_rectangle ((20 ,20 ,width -20 ,height -20 ),radius =15 ,fill =(5 ,5 ,20 ))


        await self .add_avatar_and_content_neon (draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )

        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def create_space_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Space theme with stars and nebula"""
        img =Image .new ('RGB',(width ,height ),(5 ,5 ,20 ))
        draw =ImageDraw .Draw (img )


        for i in range (100 ):
            x =random .randint (0 ,width )
            y =random .randint (0 ,height )
            size =random .randint (1 ,3 )
            brightness =random .randint (150 ,255 )
            draw .ellipse ((x ,y ,x +size ,y +size ),fill =(brightness ,brightness ,brightness ))


        for x in range (0 ,width ,20 ):
            for y in range (0 ,height ,20 ):
                if random .random ()<0.3 :
                    color_r =random .randint (50 ,150 )
                    color_g =random .randint (0 ,100 )
                    color_b =random .randint (100 ,200 )
                    draw .ellipse ((x ,y ,x +30 ,y +30 ),fill =(color_r ,color_g ,color_b ,30 ))


        draw .rounded_rectangle ((20 ,20 ,width -20 ,height -20 ),radius =15 ,fill =(0 ,0 ,0 ,150 ))

        await self .add_avatar_and_content_space (draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )

        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def create_minimal_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Clean minimal design"""
        img =Image .new ('RGB',(width ,height ),(248 ,249 ,250 ))
        draw =ImageDraw .Draw (img )


        draw .rounded_rectangle ((10 ,10 ,width -10 ,height -10 ),radius =15 ,outline =(220 ,220 ,220 ),width =2 ,fill =(255 ,255 ,255 ))


        draw .rounded_rectangle ((12 ,12 ,width -8 ,height -8 ),radius =15 ,outline =(240 ,240 ,240 ),width =1 )

        await self .add_avatar_and_content_minimal (draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )

        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def create_gaming_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Gaming RGB style design"""
        img =Image .new ('RGB',(width ,height ),(20 ,20 ,20 ))
        draw =ImageDraw .Draw (img )


        colors =[(255 ,0 ,0 ),(255 ,127 ,0 ),(255 ,255 ,0 ),(0 ,255 ,0 ),(0 ,0 ,255 ),(139 ,0 ,255 )]
        for i ,color in enumerate (colors ):
            offset =i *2 
            draw .rounded_rectangle ((10 +offset ,10 +offset ,width -10 -offset ,height -10 -offset ),
            radius =20 -offset ,outline =color ,width =2 )


        draw .rounded_rectangle ((25 ,25 ,width -25 ,height -25 ),radius =10 ,fill =(15 ,15 ,15 ))

        await self .add_avatar_and_content_gaming (draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small )

        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def create_elegant_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Elegant gold and black design"""
        img =Image .new ('RGB',(width ,height ),(25 ,25 ,25 ))
        draw =ImageDraw .Draw (img )


        for i in range (10 ):
            alpha =255 -(i *25 )
            color =(255 ,215 ,0 ,alpha )
            draw .rounded_rectangle ((5 +i ,5 +i ,width -5 -i ,height -5 -i ),radius =20 +i ,outline =color ,width =1 )


        draw .rounded_rectangle ((20 ,20 ,width -20 ,height -20 ),radius =15 ,fill =(35 ,35 ,35 ))

        await self .add_avatar_and_content_elegant (draw ,member ,xp ,progress ,needed ,messages ,level ,rank ,width ,height ,font_large ,font_medium ,font_small )

        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def create_cyberpunk_design (self ,member ,xp ,level ,rank ,messages ,current_level ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Cyberpunk style design"""
        img =Image .new ('RGB',(width ,height ),(15 ,15 ,15 ))
        draw =ImageDraw .Draw (img )


        line_color =(75 ,0 ,130 )
        for i in range (20 ):
            y =int (height /20 *i )
            draw .line ((0 ,y ,width ,y ),fill =line_color ,width =1 )


        panel_color =(25 ,25 ,25 )
        draw .rounded_rectangle ((20 ,20 ,width -20 ,height -20 ),radius =15 ,fill =panel_color )


        await self .add_avatar_and_content_cyberpunk (draw ,member ,xp ,progress ,needed ,messages ,level ,rank ,width ,height ,font_large ,font_medium ,font_small )

        img_bytes =io .BytesIO ()
        img .save (img_bytes ,format ='PNG')
        img_bytes .seek (0 )
        img .close ()
        return img_bytes 

    async def add_avatar_and_content_classic (self ,draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for classic design"""

        avatar_size =120 
        avatar_x ,avatar_y =30 ,90 

        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                draw .ellipse ((avatar_x -3 ,avatar_y -3 ,avatar_x +avatar_size +3 ,avatar_y +avatar_size +3 ),fill =(255 ,255 ,255 ))

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .ellipse ((avatar_x -3 ,avatar_y -3 ,avatar_x +avatar_size +3 ,avatar_y +avatar_size +3 ),fill =(255 ,255 ,255 ))
            draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(64 ,68 ,75 ))
            draw .text ((avatar_x +avatar_size //2 -20 ,avatar_y +avatar_size //2 -20 ),"👤",font =font_large ,fill =(255 ,255 ,255 ))


        info_x =180 
        username =member .display_name [:18 ]

        draw .text ((info_x +2 ,42 ),username ,font =font_large ,fill =(0 ,0 ,0 ))
        draw .text ((info_x ,40 ),username ,font =font_large ,fill =(255 ,255 ,255 ))

        draw .text ((info_x +2 ,82 ),f"🏆 Level {level}",font =font_medium ,fill =(0 ,0 ,0 ))
        draw .text ((info_x ,80 ),f"🏆 Level {level}",font =font_medium ,fill =(255 ,215 ,0 ))

        draw .text ((info_x +2 ,112 ),f"📊 Rank #{rank}",font =font_medium ,fill =(0 ,0 ,0 ))
        draw .text ((info_x ,110 ),f"📊 Rank #{rank}",font =font_medium ,fill =(135 ,206 ,250 ))


        bar_x ,bar_y =info_x ,150 
        bar_width ,bar_height =500 ,25 

        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =12 ,fill =(32 ,34 ,37 ))
        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =12 ,outline =(128 ,128 ,128 ),width =1 )

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :
                for i in range (progress_width ):
                    factor =i /progress_width if progress_width >0 else 0 
                    r =int (100 +(255 -100 )*factor )
                    g =int (150 +(105 -150 )*factor )
                    b =int (255 -50 *factor )
                    draw .line ([(bar_x +i ,bar_y +2 ),(bar_x +i ,bar_y +bar_height -2 )],fill =(r ,g ,b ))

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x +1 ,bar_y +6 ),xp_text ,font =font_small ,fill =(0 ,0 ,0 ))
        draw .text ((text_x ,bar_y +5 ),xp_text ,font =font_small ,fill =(255 ,255 ,255 ))


        stats_x =720 
        draw .text ((stats_x +1 ,81 ),f"💬 Messages",font =font_small ,fill =(0 ,0 ,0 ))
        draw .text ((stats_x ,80 ),f"💬 Messages",font =font_small ,fill =(255 ,255 ,255 ))
        draw .text ((stats_x +1 ,101 ),f"{messages:,}",font =font_medium ,fill =(0 ,0 ,0 ))
        draw .text ((stats_x ,100 ),f"{messages:,}",font =font_medium ,fill =(0 ,255 ,127 ))

        draw .text ((stats_x +1 ,131 ),f"⭐ Total XP",font =font_small ,fill =(0 ,0 ,0 ))
        draw .text ((stats_x ,130 ),f"⭐ Total XP",font =font_small ,fill =(255 ,255 ,255 ))
        draw .text ((stats_x +1 ,151 ),f"{xp:,}",font =font_medium ,fill =(0 ,0 ,0 ))
        draw .text ((stats_x ,150 ),f"{xp:,}",font =font_medium ,fill =(255 ,165 ,0 ))

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x +1 ,181 ),f"📈 Progress",font =font_small ,fill =(0 ,0 ,0 ))
        draw .text ((stats_x ,180 ),f"📈 Progress",font =font_small ,fill =(255 ,255 ,255 ))
        draw .text ((stats_x +1 ,201 ),f"{percentage:.1f}%",font =font_medium ,fill =(0 ,0 ,0 ))
        draw .text ((stats_x ,200 ),f"{percentage:.1f}%",font =font_medium ,fill =(255 ,105 ,180 ))

        if level >=10 :
            sparkle_positions =[(50 ,50 ),(850 ,50 ),(50 ,250 ),(850 ,250 )]
            for pos in sparkle_positions :
                draw .text (pos ,"✨",font =font_small ,fill =(255 ,255 ,255 ))

    async def add_avatar_and_content_neon (self ,draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for neon design"""
        avatar_size =100 
        avatar_x ,avatar_y =40 ,100 


        for i in range (3 ):
            draw .ellipse ((avatar_x -5 -i ,avatar_y -5 -i ,avatar_x +avatar_size +5 +i ,avatar_y +avatar_size +5 +i ),outline =(0 ,255 ,255 ),width =1 )

        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(0 ,50 ,50 ))
            draw .text ((avatar_x +avatar_size //2 -15 ,avatar_y +avatar_size //2 -15 ),"👤",font =font_medium ,fill =(0 ,255 ,255 ))


        info_x =170 
        username =member .display_name [:15 ]


        for offset in [(2 ,2 ),(1 ,1 ),(0 ,0 )]:
            color =(0 ,255 ,255 )if offset ==(0 ,0 )else (0 ,100 ,100 )
            draw .text ((info_x +offset [0 ],50 +offset [1 ]),username ,font =font_large ,fill =color )
            draw .text ((info_x +offset [0 ],85 +offset [1 ]),f"⚡ Level {level}",font =font_medium ,fill =color )
            draw .text ((info_x +offset [0 ],115 +offset [1 ]),f"🎯 Rank #{rank}",font =font_medium ,fill =color )


        bar_x ,bar_y =info_x ,160 
        bar_width ,bar_height =480 ,20 

        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =10 ,fill =(0 ,20 ,20 ))
        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =10 ,outline =(0 ,255 ,255 ),width =2 )

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :
                draw .rounded_rectangle ((bar_x +2 ,bar_y +2 ,bar_x +progress_width -2 ,bar_y +bar_height -2 ),radius =8 ,fill =(0 ,255 ,255 ))

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x ,bar_y +2 ),xp_text ,font =font_small ,fill =(255 ,255 ,255 ))


        stats_x =700 
        stats_y =80 
        draw .text ((stats_x ,stats_y ),f"💬 {messages:,}",font =font_small ,fill =(0 ,255 ,255 ))
        draw .text ((stats_x ,stats_y +25 ),f"⭐ {xp:,} XP",font =font_small ,fill =(0 ,255 ,255 ))

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x ,stats_y +50 ),f"📈 {percentage:.1f}%",font =font_small ,fill =(0 ,255 ,255 ))

    async def add_avatar_and_content_space (self ,draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for space design"""
        avatar_size =110 
        avatar_x ,avatar_y =35 ,95 


        for i in range (5 ):
            alpha =100 -(i *20 )
            draw .ellipse ((avatar_x -5 -i ,avatar_y -5 -i ,avatar_x +avatar_size +5 +i ,avatar_y +avatar_size +5 +i ),
            outline =(100 ,150 ,255 ,alpha ),width =1 )

        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(20 ,30 ,60 ))
            draw .text ((avatar_x +avatar_size //2 -15 ,avatar_y +avatar_size //2 -15 ),"🚀",font =font_medium ,fill =(255 ,255 ,255 ))


        info_x =175 
        username =member .display_name [:16 ]

        draw .text ((info_x ,45 ),username ,font =font_large ,fill =(255 ,255 ,255 ))
        draw .text ((info_x ,80 ),f"🌟 Level {level}",font =font_medium ,fill =(255 ,215 ,0 ))
        draw .text ((info_x ,110 ),f"🛸 Rank #{rank}",font =font_medium ,fill =(100 ,200 ,255 ))


        bar_x ,bar_y =info_x ,155 
        bar_width ,bar_height =490 ,22 

        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =11 ,fill =(10 ,10 ,30 ))
        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =11 ,outline =(100 ,150 ,255 ),width =1 )

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :

                for i in range (progress_width ):
                    factor =i /progress_width if progress_width >0 else 0 
                    r =int (50 +(200 *factor ))
                    g =int (100 +(150 *factor ))
                    b =255 
                    draw .line ([(bar_x +i ,bar_y +2 ),(bar_x +i ,bar_y +bar_height -2 )],fill =(r ,g ,b ))

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x ,bar_y +3 ),xp_text ,font =font_small ,fill =(255 ,255 ,255 ))


        stats_x =720 
        draw .text ((stats_x ,85 ),f"📡 Messages",font =font_small ,fill =(200 ,200 ,255 ))
        draw .text ((stats_x ,105 ),f"{messages:,}",font =font_medium ,fill =(255 ,255 ,255 ))
        draw .text ((stats_x ,135 ),f"⭐ Total XP",font =font_small ,fill =(200 ,200 ,255 ))
        draw .text ((stats_x ,155 ),f"{xp:,}",font =font_medium ,fill =(255 ,215 ,0 ))

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x ,185 ),f"🌌 {percentage:.1f}%",font =font_small ,fill =(100 ,200 ,255 ))

    async def add_avatar_and_content_minimal (self ,draw ,member ,level ,rank ,messages ,xp ,progress ,needed ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for minimal design"""
        avatar_size =100 
        avatar_x ,avatar_y =40 ,100 


        draw .ellipse ((avatar_x -2 ,avatar_y -2 ,avatar_x +avatar_size +2 ,avatar_y +avatar_size +2 ),outline =(200 ,200 ,200 ),width =2 )

        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(240 ,240 ,240 ))
            draw .text ((avatar_x +avatar_size //2 -15 ,avatar_y +avatar_size //2 -15 ),"👤",font =font_medium ,fill =(100 ,100 ,100 ))


        info_x =170 
        username =member .display_name [:18 ]

        draw .text ((info_x ,50 ),username ,font =font_large ,fill =(50 ,50 ,50 ))
        draw .text ((info_x ,85 ),f"Level {level}",font =font_medium ,fill =(100 ,100 ,100 ))
        draw .text ((info_x ,115 ),f"Rank #{rank}",font =font_medium ,fill =(150 ,150 ,150 ))


        bar_x ,bar_y =info_x ,160 
        bar_width ,bar_height =480 ,18 

        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =9 ,fill =(240 ,240 ,240 ))
        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =9 ,outline =(200 ,200 ,200 ),width =1 )

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :
                draw .rounded_rectangle ((bar_x +2 ,bar_y +2 ,bar_x +progress_width -2 ,bar_y +bar_height -2 ),radius =7 ,fill =(220 ,220 ,220 ))

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x ,bar_y +2 ),xp_text ,font =font_small ,fill =(100 ,100 ,100 ))


        stats_x =700 
        draw .text ((stats_x ,85 ),f"Messages: {messages:,}",font =font_small ,fill =(120 ,120 ,120 ))
        draw .text ((stats_x ,115 ),f"Total XP: {xp:,}",font =font_small ,fill =(120 ,120 ,120 ))

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x ,145 ),f"Progress: {percentage:.1f}%",font =font_small ,fill =(120 ,120 ,120 ))

    async def add_avatar_and_content_gaming (self ,draw ,member ,xp ,progress ,needed ,messages ,level ,rank ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for gaming design"""
        avatar_size =110 
        avatar_x ,avatar_y =35 ,95 


        colors =[(255 ,0 ,0 ),(0 ,255 ,0 ),(0 ,0 ,255 )]
        for i ,color in enumerate (colors ):
            offset =i *2 
            draw .ellipse ((avatar_x -5 -offset ,avatar_y -5 -offset ,avatar_x +avatar_size +5 +offset ,avatar_y +avatar_size +5 +offset ),outline =color ,width =1 )

        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(30 ,30 ,30 ))
            draw .text ((avatar_x +avatar_size //2 -15 ,avatar_y +avatar_size //2 -15 ),"🎮",font =font_medium ,fill =(200 ,200 ,200 ))


        info_x =175 
        username =member .display_name [:16 ]

        draw .text ((info_x ,45 ),username ,font =font_large ,fill =(200 ,200 ,200 ))
        draw .text ((info_x ,80 ),f"Level {level}",font =font_medium ,fill =(150 ,150 ,150 ))
        draw .text ((info_x ,110 ),f"Rank #{rank}",font =font_medium ,fill =(100 ,100 ,100 ))


        bar_x ,bar_y =info_x ,155 
        bar_width ,bar_height =490 ,22 

        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =11 ,fill =(30 ,30 ,30 ))
        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =11 ,outline =(80 ,80 ,80 ),width =1 )

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :

                for i in range (progress_width ):
                    factor =i /progress_width if progress_width >0 else 0 
                    r =int (50 +(150 *factor ))
                    g =int (100 +(100 *factor ))
                    b =200 
                    draw .line ([(bar_x +i ,bar_y +2 ),(bar_x +i ,bar_y +bar_height -2 )],fill =(r ,g ,b ))

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x ,bar_y +3 ),xp_text ,font =font_small ,fill =(200 ,200 ,200 ))


        stats_x =720 
        draw .text ((stats_x ,85 ),f"Messages: {messages:,}",font =font_small ,fill =(150 ,150 ,150 ))
        draw .text ((stats_x ,115 ),f"Total XP: {xp:,}",font =font_small ,fill =(150 ,150 ,150 ))

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x ,145 ),f"Progress: {percentage:.1f}%",font =font_small ,fill =(150 ,150 ,150 ))

    async def add_avatar_and_content_elegant (self ,draw ,member ,xp ,progress ,needed ,messages ,level ,rank ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for elegant design"""
        avatar_size =110 
        avatar_x ,avatar_y =35 ,95 


        for i in range (3 ):
            alpha =150 -(i *50 )
            draw .ellipse ((avatar_x -4 -i ,avatar_y -4 -i ,avatar_x +avatar_size +4 +i ,avatar_y +avatar_size +4 +i ),outline =(255 ,215 ,0 ,alpha ),width =1 )

        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(45 ,45 ,45 ))
            draw .text ((avatar_x +avatar_size //2 -15 ,avatar_y +avatar_size //2 -15 ),"👑",font =font_medium ,fill =(255 ,215 ,0 ))


        info_x =175 
        username =member .display_name [:16 ]

        draw .text ((info_x ,45 ),username ,font =font_large ,fill =(230 ,230 ,230 ))
        draw .text ((info_x ,80 ),f"Level {level}",font =font_medium ,fill =(200 ,170 ,0 ))
        draw .text ((info_x ,110 ),f"Rank #{rank}",font =font_medium ,fill =(180 ,180 ,180 ))


        bar_x ,bar_y =info_x ,155 
        bar_width ,bar_height =490 ,22 

        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =11 ,fill =(40 ,40 ,40 ))
        draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),radius =11 ,outline =(100 ,80 ,0 ),width =1 )

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :

                for i in range (progress_width ):
                    factor =i /progress_width if progress_width >0 else 0 
                    r =255 
                    g =int (150 +(65 *factor ))
                    b =0 
                    draw .line ([(bar_x +i ,bar_y +2 ),(bar_x +i ,bar_y +bar_height -2 )],fill =(r ,g ,b ))

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x ,bar_y +3 ),xp_text ,font =font_small ,fill =(220 ,220 ,220 ))


        stats_x =720 
        draw .text ((stats_x ,85 ),f"Messages: {messages:,}",font =font_small ,fill =(180 ,180 ,180 ))
        draw .text ((stats_x ,115 ),f"Total XP: {xp:,}",font =font_small ,fill =(255 ,215 ,0 ))

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x ,145 ),f"Progress: {percentage:.1f}%",font =font_small ,fill =(200 ,200 ,200 ))

    async def add_avatar_and_content_cyberpunk (self ,draw ,member ,xp ,progress ,needed ,messages ,level ,rank ,width ,height ,font_large ,font_medium ,font_small ):
        """Add avatar and content for cyberpunk design"""
        avatar_size =100 
        avatar_x ,avatar_y =40 ,100 


        try :
            avatar_url =str (member .display_avatar .with_size (256 ).url )
            response =requests .get (avatar_url ,timeout =10 )
            if response .status_code ==200 :
                avatar_img =Image .open (io .BytesIO (response .content ))
                avatar_img =avatar_img .resize ((avatar_size ,avatar_size ))

                mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                mask_draw =ImageDraw .Draw (mask )
                mask_draw .rectangle ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

                avatar_img .putalpha (mask )
                img =draw ._image 
                img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
            else :
                raise Exception ("Failed to download avatar")
        except Exception as e :
            draw .rectangle ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),fill =(45 ,45 ,45 ))
            draw .text ((avatar_x +avatar_size //2 -15 ,avatar_y +avatar_size //2 -15 ),"👤",font =font_medium ,fill =(148 ,0 ,211 ))


        text_color =(148 ,0 ,211 )
        info_x =170 
        username =member .display_name [:15 ]

        draw .text ((info_x ,50 ),username ,font =font_large ,fill =text_color )
        draw .text ((info_x ,85 ),f"Level {level}",font =font_medium ,fill =text_color )
        draw .text ((info_x ,115 ),f"Rank #{rank}",font =font_medium ,fill =text_color )


        bar_x ,bar_y =info_x ,160 
        bar_width ,bar_height =480 ,20 

        draw .rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),fill =(30 ,30 ,30 ))

        if needed >0 :
            progress_width =int ((progress /needed )*bar_width )
            if progress_width >0 :
                draw .rectangle ((bar_x ,bar_y ,bar_x +progress_width ,bar_y +bar_height ),fill =text_color )

        xp_text =f"{progress:,} / {needed:,} XP"
        text_bbox =draw .textbbox ((0 ,0 ),xp_text ,font =font_small )
        text_width =text_bbox [2 ]-text_bbox [0 ]
        text_x =bar_x +(bar_width -text_width )//2 
        draw .text ((text_x ,bar_y +2 ),xp_text ,font =font_small ,fill =(220 ,220 ,220 ))


        stats_x =700 
        draw .text ((stats_x ,85 ),f"Messages: {messages:,}",font =font_small ,fill =text_color )
        draw .text ((stats_x ,115 ),f"Total XP: {xp:,}",font =font_small ,fill =text_color )

        percentage =(progress /needed *100 )if needed >0 else 100 
        draw .text ((stats_x ,145 ),f"Progress: {percentage:.1f}%",font =font_small ,fill =text_color )

    @level .command (name ="rank",description ="View your current rank and level")
    async def rank (self ,ctx ,member :Optional [discord .Member ]=None ):
        """Display rank card"""
        member =member or ctx .author 
        guild_id =ctx .guild .id 

        try :
            rank_card =await self .create_rank_card (member ,guild_id )

            if rank_card :
                if isinstance (rank_card ,str ):

                    await ctx .send (rank_card )
                else :

                    file =discord .File (fp =rank_card ,filename ="rank_card.png")
                    await ctx .send (file =file )
                try :
                    rank_card .close ()
                except :
                    pass 
            else :
                pass 
        except Exception as e :
            logger .error (f"Error in rank command: {e}")
            pass 

    @level .command (name ="settings",description ="Configure leveling settings",aliases =['config'])
    @commands .has_permissions (administrator =True )
    async def settings (self ,ctx ):
        """Leveling settings configuration"""
        try :
            current_settings =await self .get_guild_settings (ctx .guild .id )


            if hasattr (ctx ,'interaction')and ctx .interaction :
                modal =LevelConfigModal (self ,current_settings )
                await ctx .interaction .response .send_modal (modal )
            else :

                await self .interactive_setup (ctx ,current_settings )

        except Exception as e :
            logger .error (f"Error in settings command: {e}")
            pass 

    async def interactive_setup (self ,ctx ,current_settings ):
        """Interactive setup for prefix commands"""
        try :
            embed =discord .Embed (
            title ="🔧 Interactive Leveling Setup",
            description ="Let's configure your leveling system! I'll ask you a few questions.\n"
            "Type `cancel` at any time to stop, or `skip` to keep current value.\n\n"
            "**Current Settings:**",
            color =0xFF0000 ,
            timestamp =datetime .now (timezone .utc )
            )

            embed .add_field (
            name ="Current Configuration",
            value =f"🔧 Status: {'{TICK} Enabled' if current_settings.get('enabled', False) else '{CROSS} Disabled'}\n"
            f"💎 XP per Message: {current_settings.get('xp_per_message', 20)}\n"
            f"🎨 Embed Color: {current_settings.get('embed_color', '#000000')}\n"
            f"🖼️ Thumbnail: {'{TICK} Yes' if current_settings.get('thumbnail_enabled', True) else '{CROSS} No'}\n"
            f"📢 Level Channel: {'Set' if current_settings.get('channel_id') else 'Not set'}",
            inline =False 
            )

            setup_msg =await ctx .send (embed =embed )

            def check (m ):
                return m .author ==ctx .author and m .channel ==ctx .channel 


            await ctx .send ("💎 **How much XP should users get per message?** (1-999)\n"
            f"Current: `{current_settings.get('xp_per_message', 20)}`")

            try :
                xp_msg =await self .bot .wait_for ('message',check =check ,timeout =60 )
                if xp_msg .content .lower ()=='cancel':
                    await ctx .send (f"{CROSS} Setup cancelled.")
                    return 

                if xp_msg .content .lower ()=='skip':
                    xp_per_message =current_settings .get ('xp_per_message',20 )
                else :
                    xp_per_message =int (xp_msg .content )
                    if xp_per_message <1 or xp_per_message >999 :
                        await ctx .send (f"{CROSS} XP must be between 1 and 999. Using current value.")
                        xp_per_message =current_settings .get ('xp_per_message',20 )
            except (ValueError ,asyncio .TimeoutError ):
                await ctx .send ("⏰ Timeout or invalid input. Using current value.")
                xp_per_message =current_settings .get ('xp_per_message',20 )


            current_msg =current_settings .get ('level_message','Congratulations {user}! You have reached level {level}!')
            await ctx .send ("💬 **What should the level-up message say?**\n"
            f"Available placeholders: `{'{user}'}`, `{'{username}'}`, `{'{level}'}`, `{'{server}'}`\n"
            f"Current: `{current_msg[:100]}{'...' if len(current_msg) > 100 else ''}`")

            try :
                msg_response =await self .bot .wait_for ('message',check =check ,timeout =120 )
                if msg_response .content .lower ()=='cancel':
                    await ctx .send (f"{CROSS} Setup cancelled.")
                    return 

                if msg_response .content .lower ()=='skip':
                    level_message =current_msg 
                else :
                    level_message =msg_response .content 
                    if len (level_message )>2000 :
                        await ctx .send (f"{CROSS} Message too long (max 2000 chars). Using current value.")
                        level_message =current_msg 
            except asyncio .TimeoutError :
                await ctx .send ("⏰ Timeout. Using current value.")
                level_message =current_msg 


            current_color =current_settings .get ('embed_color','#000000')
            await ctx .send ("🎨 **What color should the level-up embeds be?** (hex format like #FF0000)\n"
            f"Current: `{current_color}`")

            try :
                color_msg =await self .bot .wait_for ('message',check =check ,timeout =60 )
                if color_msg .content .lower ()=='cancel':
                    await ctx .send (f"{CROSS} Setup cancelled.")
                    return 

                if color_msg .content .lower ()=='skip':
                    embed_color =current_color 
                else :
                    color_input =color_msg .content .strip ()
                    if not color_input .startswith ('#'):
                        color_input ='#'+color_input 

                    if validate_hex_color (color_input ):
                        embed_color =color_input 
                    else :
                        await ctx .send (f"{CROSS} Invalid hex color. Using current value.")
                        embed_color =current_color 
            except asyncio .TimeoutError :
                await ctx .send ("⏰ Timeout. Using current value.")
                embed_color =current_color 


            current_image =current_settings .get ('level_image','')
            await ctx .send ("🖼️ **Level-up image URL** (optional, direct image link)\n"
            f"Current: `{'Set' if current_image else 'None'}`")

            try :
                image_msg =await self .bot .wait_for ('message',check =check ,timeout =60 )
                if image_msg .content .lower ()=='cancel':
                    await ctx .send (f"{CROSS} Setup cancelled.")
                    return 

                if image_msg .content .lower ()=='skip':
                    level_image =current_image 
                else :
                    level_image =image_msg .content .strip ()if image_msg .content .strip ()!='none'else None 
                    if level_image and len (level_image )>500 :
                        await ctx .send (f"{CROSS} URL too long. Using current value.")
                        level_image =current_image 
            except asyncio .TimeoutError :
                await ctx .send ("⏰ Timeout. Using current value.")
                level_image =current_image 


            current_thumb =current_settings .get ('thumbnail_enabled',True )
            await ctx .send ("🖼️ **Show user avatar thumbnail in level-up messages?** (yes/no)\n"
            f"Current: `{'Yes' if current_thumb else 'No'}`")

            try :
                thumb_msg =await self .bot .wait_for ('message',check =check ,timeout =60 )
                if thumb_msg .content .lower ()=='cancel':
                    await ctx .send (f"{CROSS} Setup cancelled.")
                    return 

                if thumb_msg .content .lower ()=='skip':
                    thumbnail_enabled =current_thumb 
                else :
                    thumbnail_enabled =thumb_msg .content .lower ()in ['yes','y','true','1','on','enable']
            except asyncio .TimeoutError :
                await ctx .send ("⏰ Timeout. Using current value.")
                thumbnail_enabled =current_thumb 


            embed_color_int =hex_to_int (embed_color )
            level_image_final =level_image if level_image and level_image .strip ()else None 

            async with aiosqlite .connect ("db/leveling.db")as db :

                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    exists =await cursor .fetchone ()

                if exists :

                    await db .execute ("""
                        UPDATE leveling_settings 
                        SET enabled = 1, xp_per_message = ?, level_message = ?, embed_color = ?, 
                            level_image = ?, thumbnail_enabled = ?
                        WHERE guild_id = ?
                    """,(
                    xp_per_message ,
                    level_message ,
                    embed_color_int ,
                    level_image_final ,
                    1 if thumbnail_enabled else 0 ,
                    ctx .guild .id 
                    ))
                else :

                    await db .execute ("""
                        INSERT INTO leveling_settings 
                        (guild_id, enabled, xp_per_message, level_message, embed_color, level_image, thumbnail_enabled,
                         min_xp, max_xp, cooldown_seconds, dm_level_up, channel_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,(
                    ctx .guild .id ,
                    1 ,
                    xp_per_message ,
                    level_message ,
                    embed_color_int ,
                    level_image_final ,
                    1 if thumbnail_enabled else 0 ,
                    15 ,
                    25 ,
                    60 ,
                    0 ,
                    None 
                    ))

                await db .commit ()


            final_embed =discord .Embed (
            title =f"{TICK} Leveling System Configured!",
            description ="Your leveling system has been successfully set up with these settings:",
            color =embed_color_int ,
            timestamp =datetime .now (timezone .utc )
            )

            final_embed .add_field (
            name ="📊 Configuration Summary",
            value =f"🔧 **Status:** Enabled\n"
            f"💎 **XP per Message:** {xp_per_message}\n"
            f"💬 **Level-up Message:** {level_message[:50]}{'...' if len(level_message) > 50 else ''}\n"
            f"🎨 **Embed Color:** {embed_color}\n"
            f"🖼️ **Level-up Image:** {'Set' if level_image_final else 'None'}\n"
            f"🖼️ **Show Thumbnail:** {'Yes' if thumbnail_enabled else 'No'}",
            inline =False 
            )

            final_embed .add_field (
            name ="🚀 Next Steps",
            value ="• Use `!level channel #channel` to set announcement channel\n"
            "• Use `!level rewards add <level> @role` to add level rewards\n"
            "• Use `!level leaderboard` to view the server leaderboard\n"
            "• Users will now gain XP from messages!",
            inline =False 
            )

            view =PlaceholdersView ()
            await ctx .send (embed =final_embed ,view =view )

        except Exception as e :
            logger .error (f"Error in interactive setup: {e}")
            pass 

    @level .command (name ="setxp",description ="Set XP amount per message")
    @commands .has_permissions (administrator =True )
    async def setxp (self ,ctx ,amount :int ):
        """Set XP per message amount"""
        try :
            if amount <1 or amount >999 :
                await ctx .send (f"{CROSS} XP per message must be between 1 and 999!")
                return 

            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    exists =await cursor .fetchone ()

                if exists :
                    await db .execute ("UPDATE leveling_settings SET xp_per_message = ? WHERE guild_id = ?",(amount ,ctx .guild .id ))
                else :
                    await db .execute ("INSERT INTO leveling_settings (guild_id, xp_per_message) VALUES (?, ?)",(ctx .guild .id ,amount ))

                await db .commit ()

            embed =discord .Embed (
            title =f"{TICK} XP Amount Updated",
            description =f"XP per message has been set to **{amount} XP**",
            color =0x00FF00 ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error setting XP amount: {e}")
            pass 

    @level .command (name ="setmessage",description ="Set level-up message")
    @commands .has_permissions (administrator =True )
    async def setmessage (self ,ctx ,*,message :str ):
        """Set level-up message"""
        try :
            if len (message )>2000 :
                await ctx .send (f"{CROSS} Level-up message must be less than 2000 characters!")
                return 

            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    exists =await cursor .fetchone ()

                if exists :
                    await db .execute ("UPDATE leveling_settings SET level_message = ? WHERE guild_id = ?",(message ,ctx .guild .id ))
                else :
                    await db .execute ("INSERT INTO leveling_settings (guild_id, level_message) VALUES (?, ?)",(ctx .guild .id ,message ))

                await db .commit ()

            embed =discord .Embed (
            title =f"{TICK} Level-Up Message Updated",
            description =f"Level-up message has been set to:\n```{message}```",
            color =0x00FF00 ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error setting level message: {e}")
            pass 

    @level .command (name ="setcolor",description ="Set embed color")
    @commands .has_permissions (administrator =True )
    async def setcolor (self ,ctx ,color :str ):
        """Set embed color"""
        try :

            if not color .startswith ('#'):
                color ='#'+color 

            if not validate_hex_color (color ):
                await ctx .send (f"{CROSS} Invalid hex color format! Use format like #FF0000")
                return 

            color_int =hex_to_int (color )

            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    exists =await cursor .fetchone ()

                if exists :
                    await db .execute ("UPDATE leveling_settings SET embed_color = ? WHERE guild_id = ?",(color_int ,ctx .guild .id ))
                else :
                    await db .execute ("INSERT INTO leveling_settings (guild_id, embed_color) VALUES (?, ?)",(ctx .guild .id ,color_int ))

                await db .commit ()

            embed =discord .Embed (
            title =f"{TICK} Embed Color Updated",
            description =f"Embed color has been set to **{color}**",
            color =color_int ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error setting embed color: {e}")
            pass 

    @level .command (name ="thumbnail",description ="Toggle user thumbnail in level-up messages")
    @commands .has_permissions (administrator =True )
    async def thumbnail (self ,ctx ,setting :str ):
        """Toggle thumbnail setting"""
        try :
            setting =setting .lower ()
            if setting not in ['on','off','true','false','yes','no','enable','disable']:
                await ctx .send (f"{CROSS} Use: `on/off`, `true/false`, `yes/no`, or `enable/disable`")
                return 

            enabled =setting in ['on','true','yes','enable']

            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    exists =await cursor .fetchone ()

                if exists :
                    await db .execute ("UPDATE leveling_settings SET thumbnail_enabled = ? WHERE guild_id = ?",(1 if enabled else 0 ,ctx .guild .id ))
                else :
                    await db .execute ("INSERT INTO leveling_settings (guild_id, thumbnail_enabled) VALUES (?, ?)",(ctx .guild .id ,1 if enabled else 0 ))

                await db .commit ()

            embed =discord .Embed (
            title =f"{TICK} Thumbnail Setting Updated",
            description =f"User thumbnails in level-up messages: **{'Enabled' if enabled else 'Disabled'}**",
            color =0x00FF00 ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error setting thumbnail: {e}")
            pass 

    @level .command (name ="cooldown",description ="Set message cooldown in seconds")
    @commands .has_permissions (administrator =True )
    async def cooldown (self ,ctx ,seconds :int ):
        """Set message cooldown"""
        try :
            if seconds <0 or seconds >3600 :
                await ctx .send (f"{CROSS} Cooldown must be between 0 and 3600 seconds (1 hour)!")
                return 

            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    exists =await cursor .fetchone ()

                if exists :
                    await db .execute ("UPDATE leveling_settings SET cooldown_seconds = ? WHERE guild_id = ?",(seconds ,ctx .guild .id ))
                else :
                    await db .execute ("INSERT INTO leveling_settings (guild_id, cooldown_seconds) VALUES (?, ?)",(ctx .guild .id ,seconds ))

                await db .commit ()

            embed =discord .Embed (
            title =f"{TICK} Cooldown Updated",
            description =f"Message cooldown has been set to **{seconds} seconds**",
            color =0x00FF00 ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error setting cooldown: {e}")
            pass 

    @level .group (name ="rewards",invoke_without_command =True ,description ="Manage level rewards")
    async def rewards (self ,ctx ):
        """Level rewards management"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    @rewards .command (name ="add",description ="Add a level reward")
    @commands .has_permissions (administrator =True )
    async def rewards_add (self ,ctx ,level :int ,role :discord .Role ,remove_previous :bool =False ):
        """Add level reward"""
        try :
            if level <=0 :
                await ctx .send ("Level must be greater than 0.")
                return 

            async with aiosqlite .connect ("db/leveling.db")as db :
                await db .execute (
                "INSERT OR REPLACE INTO level_rewards (guild_id, level, role_id, remove_previous) VALUES (?, ?, ?, ?)",
                (ctx .guild .id ,level ,role .id ,int (remove_previous ))
                )
                await db .commit ()

            await ctx .send (f"Added reward {role.mention} for level {level} (Remove Previous: {remove_previous})")
        except Exception as e :
            logger .error (f"Error in rewards add command: {e}")
            pass 

    @rewards .command (name ="remove",description ="Remove a level reward")
    @commands .has_permissions (administrator =True )
    async def rewards_remove (self ,ctx ,level :int ):
        """Remove level reward"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                await db .execute (
                "DELETE FROM level_rewards WHERE guild_id = ? AND level = ?",
                (ctx .guild .id ,level )
                )
                await db .commit ()

            await ctx .send (f"Removed reward for level {level}")
        except Exception as e :
            logger .error (f"Error in rewards remove command: {e}")
            pass 

    @rewards .command (name ="list",description ="List all level rewards")
    @commands .has_permissions (administrator =True )
    async def rewards_list (self ,ctx ):
        """List level rewards"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT level, role_id, remove_previous FROM level_rewards WHERE guild_id = ? ORDER BY level",
                (ctx .guild .id ,)
                )as cursor :
                    rewards =await cursor .fetchall ()

            if not rewards :
                await ctx .send ("No level rewards configured.")
                return 

            embed =discord .Embed (title ="Level Rewards",color =0xFF0000 ,timestamp =datetime .now (timezone .utc ))
            for level ,role_id ,remove_previous in rewards :
                role =ctx .guild .get_role (role_id )
                role_name =role .mention if role else "Role not found"
                embed .add_field (name =f"Level {level}",value =f"Role: {role_name} (Remove Previous: {remove_previous})",inline =False )

            await ctx .send (embed =embed )
        except Exception as e :
            logger .error (f"Error in rewards list command: {e}")
            pass 

    @level .group (name ="multiplier",invoke_without_command =True ,description ="Manage XP multipliers")
    async def multiplier (self ,ctx ):
        """XP multiplier management"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    @multiplier .command (name ="add",description ="Add an XP multiplier")
    @commands .has_permissions (administrator =True )
    async def multiplier_add (self ,ctx ,target_type :str ,target :str ,multiplier :float ):
        """Add XP multiplier"""
        try :
            if target_type not in ["role","channel"]:
                await ctx .send ("Invalid target type. Must be 'role' or 'channel'.")
                return 

            if multiplier <=0 :
                await ctx .send ("Multiplier must be greater than 0.")
                return 

            if target_type =="role":
                try :
                    role_id =int (target )
                    target_id =ctx .guild .get_role (role_id ).id 
                except :
                    await ctx .send ("Invalid role ID.")
                    return 
            else :
                try :
                    channel_id =int (target )
                    target_id =ctx .guild .get_channel (channel_id ).id 
                except :
                    await ctx .send ("Invalid channel ID.")
                    return 

            async with aiosqlite .connect ("db/leveling.db")as db :
                await db .execute (
                "INSERT OR REPLACE INTO xp_multipliers (guild_id, target_id, target_type, multiplier) VALUES (?, ?, ?, ?)",
                (ctx .guild .id ,target_id ,target_type ,multiplier )
                )
                await db .commit ()

            await ctx .send (f"Added {multiplier}x multiplier for {target_type} {target}")
        except Exception as e :
            logger .error (f"Error in multiplier add command: {e}")
            pass 

    @multiplier .command (name ="remove",description ="Remove an XP multiplier")
    @commands .has_permissions (administrator =True )
    async def multiplier_remove (self ,ctx ,target_type :str ,target :str ):
        """Remove XP multiplier"""
        try :
            if target_type not in ["role","channel"]:
                await ctx .send ("Invalid target type. Must be 'role' or 'channel'.")
                return 

            if target_type =="role":
                try :
                    role_id =int (target )
                    target_id =ctx .guild .get_role (role_id ).id 
                except :
                    await ctx .send ("Invalid role ID.")
                    return 
            else :
                try :
                    channel_id =int (target )
                    target_id =ctx .guild .get_channel (channel_id ).id 
                except :
                    await ctx .send ("Invalid channel ID.")
                    return 

            async with aiosqlite .connect ("db/leveling.db")as db :
                await db .execute (
                "DELETE FROM xp_multipliers WHERE guild_id = ? AND target_id = ? AND target_type = ?",
                (ctx .guild .id ,target_id ,target_type )
                )
                await db .commit ()

            await ctx .send (f"Removed multiplier for {target_type} {target}")
        except Exception as e :
            logger .error (f"Error in multiplier remove command: {e}")
            pass 

    @multiplier .command (name ="list",description ="List all XP multipliers")
    @commands .has_permissions (administrator =True )
    async def multiplier_list (self ,ctx ):
        """List XP multipliers"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT target_id, target_type, multiplier FROM xp_multipliers WHERE guild_id = ?",
                (ctx .guild .id ,)
                )as cursor :
                    multipliers =await cursor .fetchall ()

            if not multipliers :
                await ctx .send ("No XP multipliers configured.")
                return 

            embed =discord .Embed (title ="XP Multipliers",color =0xFF0000 ,timestamp =datetime .now (timezone .utc ))
            for target_id ,target_type ,multiplier in multipliers :
                if target_type =="role":
                    role =ctx .guild .get_role (target_id )
                    target_name =role .mention if role else "Role not found"
                else :
                    channel =ctx .guild .get_channel (target_id )
                    target_name =channel .mention if channel else "Channel not found"
                embed .add_field (name =f"{target_type.capitalize()}: {target_name}",value =f"Multiplier: {multiplier}x",inline =False )

            await ctx .send (embed =embed )
        except Exception as e :
            logger .error (f"Error in multiplier list command: {e}")
            pass 

    @level .group (name ="blacklist",invoke_without_command =True ,description ="Manage leveling blacklists")
    async def blacklist (self ,ctx ):
        """Leveling blacklist management"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    @blacklist .command (name ="add",description ="Add to the leveling blacklist")
    @commands .has_permissions (administrator =True )
    async def blacklist_add (self ,ctx ,target_type :str ,target :str ):
        """Add to leveling blacklist"""
        try :
            if target_type not in ["role","channel"]:
                await ctx .send ("Invalid target type. Must be 'role' or 'channel'.")
                return 

            if target_type =="role":
                try :
                    role_id =int (target )
                    target_id =ctx .guild .get_role (role_id ).id 
                except :
                    await ctx .send ("Invalid role ID.")
                    return 
            else :
                try :
                    channel_id =int (target )
                    target_id =ctx .guild .get_channel (channel_id ).id 
                except :
                    await ctx .send ("Invalid channel ID.")
                    return 

            async with aiosqlite .connect ("db/leveling.db")as db :
                await db .execute (
                "INSERT OR REPLACE INTO leveling_blacklist (guild_id, target_id, target_type) VALUES (?, ?, ?)",
                (ctx .guild .id ,target_id ,target_type )
                )
                await db .commit ()

            await ctx .send (f"Added {target_type} {target} to the leveling blacklist.")
        except Exception as e :
            logger .error (f"Error in blacklist add command: {e}")
            pass 

    @blacklist .command (name ="remove",description ="Remove from the leveling blacklist")
    @commands .has_permissions (administrator =True )
    async def blacklist_remove (self ,ctx ,target_type :str ,target :str ):
        """Remove from leveling blacklist"""
        try :
            if target_type not in ["role","channel"]:
                await ctx .send ("Invalid target type. Must be 'role' or 'channel'.")
                return 

            if target_type =="role":
                try :
                    role_id =int (target )
                    target_id =ctx .guild .get_role (role_id ).id 
                except :
                    await ctx .send ("Invalid role ID.")
                    return 
            else :
                try :
                    channel_id =int (target )
                    target_id =ctx .guild .get_channel (channel_id ).id 
                except :
                    await ctx .send ("Invalid channel ID.")
                    return 

            async with aiosqlite .connect ("db/leveling.db")as db :
                await db .execute (
                "DELETE FROM leveling_blacklist WHERE guild_id = ? AND target_id = ? AND target_type = ?",
                (ctx .guild .id ,target_id ,target_type )
                )
                await db .commit ()

            await ctx .send (f"Removed {target_type} {target} from the leveling blacklist.")
        except Exception as e :
            logger .error (f"Error in blacklist remove command: {e}")
            pass 

    @blacklist .command (name ="list",description ="List the leveling blacklist")
    @commands .has_permissions (administrator =True )
    async def blacklist_list (self ,ctx ):
        """List leveling blacklist"""
        try :
            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT target_id, target_type FROM leveling_blacklist WHERE guild_id = ?",
                (ctx .guild .id ,)
                )as cursor :
                    blacklisted =await cursor .fetchall ()

            if not blacklisted :
                await ctx .send ("The leveling blacklist is empty.")
                return 

            embed =discord .Embed (title ="Leveling Blacklist",color =0xFF0000 ,timestamp =datetime .now (timezone .utc ))
            for target_id ,target_type in blacklisted :
                if target_type =="role":
                    role =ctx .guild .get_role (target_id )
                    target_name =role .mention if role else "Role not found"
                else :
                    channel =ctx .guild .get_channel (target_id )
                    target_name =channel .mention if channel else "Channel not found"
                embed .add_field (name =f"{target_type.capitalize()}: {target_name}",value ="",inline =False )

            await ctx .send (embed =embed )
        except Exception as e :
            logger .error (f"Error in blacklist list command: {e}")
            pass 

    async def apply_level_roles (self ,guild ,member ,level ):
        """Apply level-based roles to a member."""
        try :
            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT role_id FROM level_roles WHERE guild_id = ? AND level = ?",(guild .id ,level ))as cursor :
                    result =await cursor .fetchone ()
                    if result :
                        role_id =result [0 ]
                        role =guild .get_role (role_id )
                        if role :
                            try :
                                await member .add_roles (role ,reason ="Reached level {}".format (level ))
                                logger .info (f"Applied level role {role.name} to {member.name} in {guild.name}")
                            except discord .Forbidden :
                                logger .error (f"Missing permissions to add role {role.name} to {member.name} in {guild.name}")
                            except discord .HTTPException as e :
                                logger .error (f"Failed to add role {role.name} to {member.name} in {guild.name}: {e}")
                        else :
                            logger .warning (f"Role with ID {role_id} not found in {guild.name}")
        except Exception as e :
            logger .error (f"Error applying level roles: {e}")

    @commands .hybrid_command (name ="setlevelrole",description ="Set a role for a specific level (admin only)")
    @commands .has_permissions (administrator =True )
    async def set_level_role (self ,ctx ,level :int ,role :discord .Role ):
        """Set a level role."""
        try :
            if level <=0 :
                await ctx .send ("Level must be greater than 0.")
                return 

            async with aiosqlite .connect (self .db_path )as db :
                await db .execute ("INSERT OR REPLACE INTO level_roles (guild_id, level, role_id) VALUES (?, ?, ?)",(ctx .guild .id ,level ,role .id ))
                await db .commit ()

            await ctx .send (f"Set role {role.mention} for level {level}.")
        except Exception as e :
            logger .error (f"Error setting level role: {e}")
            pass 

    @commands .hybrid_command (name ="removelevelrole",description ="Remove a level role (admin only)")
    @commands .has_permissions (administrator =True )
    async def remove_level_role (self ,ctx ,level :int ):
        """Remove a level role."""
        try :
            async with aiosqlite .connect (self .db_path )as db :
                await db .execute ("DELETE FROM level_roles WHERE guild_id = ? AND level = ?",(ctx .guild .id ,level ))
                await db .commit ()

            await ctx .send (f"Removed role for level {level}.")
        except Exception as e :
            logger .error (f"Error removing level role: {e}")
            pass 

    @commands .hybrid_command (name ="listlevelroles",description ="List all level roles (admin only)")
    @commands .has_permissions (administrator =True )
    async def list_level_roles (self ,ctx ):
        """List all level roles."""
        try :
            async with aiosqlite .connect (self .db_path )as db :
                async with db .execute ("SELECT level, role_id FROM level_roles WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    roles =await cursor .fetchall ()

            if not roles :
                await ctx .send ("No level roles set for this server.")
                return 

            embed =discord .Embed (title ="Level Roles",color =0xFF0000 ,timestamp =datetime .now (timezone .utc ))
            for level ,role_id in roles :
                role =ctx .guild .get_role (role_id )
                role_name =role .mention if role else "Role not found"
                embed .add_field (name =f"Level {level}",value =f"Role: {role_name}",inline =False )

            await ctx .send (embed =embed )
        except Exception as e :
            logger .error (f"Error listing level roles: {e}")
            pass 

    @commands .hybrid_command (name ="resetxp",description ="Reset a user's XP (admin only)")
    @commands .has_permissions (administrator =True )
    async def reset_xp (self ,ctx ,member :discord .Member ):
        """Reset a user's XP and level to default values."""
        try :
            async with aiosqlite .connect (self .db_path )as db :
                await db .execute ("UPDATE users SET xp = 0, level = 1 WHERE guild_id = ? AND user_id = ?",(ctx .guild .id ,member .id ))
                await db .commit ()

            await ctx .send (f"Successfully reset XP for {member.mention}.")
        except Exception as e :
            logger .error (f"Error resetting XP: {e}")
            pass 

    @commands .hybrid_command (name ="setxp",description ="Set a user's XP (admin only)")
    @commands .has_permissions (administrator =True )
    async def set_xp (self ,ctx ,member :discord .Member ,xp :int ):
        """Set a user's XP to a specific value."""
        try :
            level =calculate_level_from_xp (xp )
            async with aiosqlite .connect (self .db_path )as db :
                await db .execute ("UPDATE users SET xp = ?, level = ? WHERE guild_id = ? AND user_id = ?",(xp ,level ,ctx .guild .id ,member .id ))
                await db .commit ()

            await ctx .send (f"Successfully set XP for {member.mention} to {xp:,}.")
        except Exception as e :
            logger .error (f"Error setting XP: {e}")
            pass 

    @commands .hybrid_command (name ="setlevel",description ="Set a user's level (admin only)")
    @commands .has_permissions (administrator =True )
    async def set_level (self ,ctx ,member :discord .Member ,level :int ):
        """Set a user's level to a specific value."""
        try :
            xp =calculate_xp_for_level (level )
            async with aiosqlite .connect (self .db_path )as db :
                await db .execute ("UPDATE users SET xp = ?, level = ? WHERE guild_id = ? AND user_id = ?",(xp ,level ,ctx .guild .id ,member .id ))
                await db .commit ()

            await ctx .send (f"Successfully set level for {member.mention} to {level:,}.")
        except Exception as e :
            logger .error (f"Error setting level: {e}")
            pass 

    @level .command (name ="leaderboard",description ="View the server level leaderboard")
    @commands .cooldown (1 ,10 ,commands .BucketType .guild )
    async def level_leaderboard (self ,ctx ):
        """Display server level leaderboard"""
        try :
            if isinstance (ctx ,discord .Interaction ):
                await ctx .response .defer ()

            async with aiosqlite .connect ("db/leveling.db")as db :

                cursor =await db .execute ('''
                    SELECT user_id, xp, messages FROM user_xp 
                    WHERE guild_id = ? 
                    ORDER BY xp DESC 
                    LIMIT 10
                ''',(ctx .guild .id ,))

                top_users =await cursor .fetchall ()

            if not top_users :
                embed =discord .Embed (
                title ="📊 Server Level Leaderboard",
                description ="No users found in the leaderboard yet!",
                color =0xFF0000 
                )
                if isinstance (ctx ,discord .Interaction ):
                    await ctx .followup .send (embed =embed )
                else :
                    await ctx .send (embed =embed )
                return 


            leaderboard_image =await self .create_leaderboard_image (ctx .guild ,top_users )

            if leaderboard_image :
                if isinstance (leaderboard_image ,str ):

                    if isinstance (ctx ,discord .Interaction ):
                        await ctx .followup .send (leaderboard_image )
                    else :
                        await ctx .send (leaderboard_image )
                else :

                    file =discord .File (fp =leaderboard_image ,filename ="level_leaderboard.png")
                    if isinstance (ctx ,discord .Interaction ):
                        await ctx .followup .send (file =file )
                    else :
                        await ctx .send (file =file )
                    try :
                        leaderboard_image .close ()
                    except :
                        pass 
            else :
                if isinstance (ctx ,discord .Interaction ):
                    await ctx .followup .send ("Failed to generate leaderboard.")
                else :
                    pass 

        except Exception as e :
            logger .error (f"Error in level leaderboard command: {e}")
            error_msg =f"An error occurred: {e}"
            if isinstance (ctx ,discord .Interaction ):
                await ctx .followup .send (error_msg )
            else :
                await ctx .send (error_msg )

    async def create_leaderboard_image (self ,guild ,top_users ):
        """Create enhanced visual leaderboard image with custom background support and modern design"""
        try :
            if not PIL_AVAILABLE :
                return self .create_text_leaderboard (guild ,top_users )


            width ,height =1920 ,1080 


            background_loaded =False 
            background_extensions =['.jpg','.jpeg','.png','.gif','.webp']

            for ext in background_extensions :
                try :
                    bg_path =f"/home/container/assets/leaderboardlevel{ext}"
                    if os .path .exists (bg_path ):
                        temp_bg =Image .open (bg_path )
                        bg_width ,bg_height =temp_bg .size 


                        ratio =bg_width /bg_height 

                        if 1.7 <=ratio <=1.8 :
                            width ,height =1920 ,1080 
                        elif 1.3 <=ratio <=1.35 :
                            width ,height =1600 ,1200 
                        elif 0.95 <=ratio <=1.05 :
                            width ,height =1200 ,1200 
                        elif 0.7 <=ratio <=0.85 :
                            width ,height =1200 ,1600 
                        else :

                            if bg_width >2000 or bg_height >1500 :
                                scale =min (2000 /bg_width ,1500 /bg_height )
                                width =int (bg_width *scale )
                                height =int (bg_height *scale )
                            else :
                                width ,height =bg_width ,bg_height 

                        temp_bg .close ()
                        break 
                except Exception as e :
                    logger .error (f"Failed to analyze background {bg_path}: {e}")
                    continue 


            for ext in background_extensions :
                try :
                    bg_path =f"/home/container/assets/leaderboardlevel{ext}"
                    if os .path .exists (bg_path ):
                        background_img =Image .open (bg_path )

                        if hasattr (background_img ,'is_animated')and background_img .is_animated :
                            background_img =background_img .convert ('RGBA')

                        background_img =background_img .resize ((width ,height ),Image .Resampling .LANCZOS )
                        img =background_img .convert ('RGB')
                        background_loaded =True 
                        logger .info (f"Loaded custom background: {bg_path} - Resized to {width}x{height}")
                        break 
                except Exception as e :
                    logger .error (f"Failed to load background {bg_path}: {e}")
                    continue 


            if not background_loaded :
                img =Image .new ('RGB',(width ,height ),(15 ,15 ,25 ))
                draw_temp =ImageDraw .Draw (img )

                for y in range (height ):
                    factor =y /height 
                    r =int (15 +(45 -15 )*factor +10 *math .sin (factor *math .pi *2 ))
                    g =int (15 +(55 -15 )*factor +15 *math .sin (factor *math .pi *3 ))
                    b =int (25 +(85 -25 )*factor +20 *math .sin (factor *math .pi *4 ))
                    draw_temp .line ([(0 ,y ),(width ,y )],fill =(min (255 ,max (0 ,r )),min (255 ,max (0 ,g )),min (255 ,max (0 ,b ))))

            draw =ImageDraw .Draw (img )


            try :
                title_font =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",54 )
                name_font =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",32 )
                stats_font =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22 )
                rank_font =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",40 )
                small_font =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19 )
            except (OSError ,IOError ):
                title_font =ImageFont .load_default ()
                name_font =ImageFont .load_default ()
                stats_font =ImageFont .load_default ()
                rank_font =ImageFont .load_default ()
                small_font =ImageFont .load_default ()


            title =f"🏆 {guild.name} Level Leaderboard"
            title_bbox =draw .textbbox ((0 ,0 ),title ,font =title_font )
            title_width =title_bbox [2 ]-title_bbox [0 ]
            title_x =(width -title_width )//2 


            title_bg_margin =50 
            title_y =25 
            title_height =90 


            draw .rounded_rectangle (
            (title_x -title_bg_margin ,title_y ,title_x +title_width +title_bg_margin ,title_y +title_height ),
            radius =25 ,fill =(0 ,0 ,0 ,160 )
            )
            draw .rounded_rectangle (
            (title_x -title_bg_margin ,title_y ,title_x +title_width +title_bg_margin ,title_y +title_height ),
            radius =25 ,outline =(255 ,215 ,0 ,200 ),width =3 
            )


            for offset in [(5 ,5 ),(4 ,4 ),(3 ,3 ),(2 ,2 ),(1 ,1 )]:
                alpha =100 -(offset [0 ]*15 )
                draw .text ((title_x +offset [0 ],title_y +20 +offset [1 ]),title ,font =title_font ,fill =(0 ,0 ,0 ,alpha ))
            draw .text ((title_x ,title_y +20 ),title ,font =title_font ,fill =(255 ,215 ,0 ))


            start_y =180 
            entry_height =120 
            margin_left =100 
            margin_right =100 

            for i ,(user_id ,xp ,messages )in enumerate (top_users ):
                user =guild .get_member (user_id )
                if not user :
                    continue 

                y =start_y +(i *entry_height )
                level =calculate_level_from_xp (xp )


                if i ==0 :
                    rank_color =(255 ,215 ,0 )
                    bg_color =(40 ,35 ,15 )
                    border_color =(255 ,215 ,0 )
                    accent_color =(255 ,235 ,100 )
                elif i ==1 :
                    rank_color =(192 ,192 ,192 )
                    bg_color =(35 ,35 ,40 )
                    border_color =(192 ,192 ,192 )
                    accent_color =(220 ,220 ,220 )
                elif i ==2 :
                    rank_color =(205 ,127 ,50 )
                    bg_color =(40 ,30 ,20 )
                    border_color =(205 ,127 ,50 )
                    accent_color =(230 ,150 ,80 )
                else :
                    rank_color =(120 ,180 ,255 )
                    bg_color =(25 ,30 ,40 )
                    border_color =(80 ,120 ,160 )
                    accent_color =(150 ,200 ,255 )


                entry_bg_y =y -15 
                entry_bg_height =entry_height -10 


                draw .rounded_rectangle (
                (margin_left ,entry_bg_y ,width -margin_right ,entry_bg_y +entry_bg_height ),
                radius =20 ,fill =(0 ,0 ,0 ,180 )
                )


                for border_layer in range (4 ):
                    border_alpha =180 -(border_layer *30 )
                    draw .rounded_rectangle (
                    (margin_left -border_layer ,entry_bg_y -border_layer ,
                    width -margin_right +border_layer ,entry_bg_y +entry_bg_height +border_layer ),
                    radius =20 +border_layer ,outline =(*border_color ,border_alpha ),width =2 
                    )


                rank_x =margin_left +40 
                rank_text =f"#{i + 1}"


                rank_circle_size =55 
                rank_circle_y =y +20 
                draw .ellipse (
                (rank_x -5 ,rank_circle_y ,rank_x +rank_circle_size ,rank_circle_y +rank_circle_size ),
                fill =(*rank_color ,60 )
                )
                draw .ellipse (
                (rank_x -5 ,rank_circle_y ,rank_x +rank_circle_size ,rank_circle_y +rank_circle_size ),
                outline =rank_color ,width =3 
                )


                rank_bbox =draw .textbbox ((0 ,0 ),rank_text ,font =rank_font )
                rank_text_width =rank_bbox [2 ]-rank_bbox [0 ]
                rank_text_height =rank_bbox [3 ]-rank_bbox [1 ]
                rank_text_x =rank_x +(rank_circle_size -rank_text_width )//2 -5 
                rank_text_y =rank_circle_y +(rank_circle_size -rank_text_height )//2 


                draw .text ((rank_text_x +3 ,rank_text_y +3 ),rank_text ,font =rank_font ,fill =(0 ,0 ,0 ,200 ))
                draw .text ((rank_text_x ,rank_text_y ),rank_text ,font =rank_font ,fill =rank_color )


                avatar_x =margin_left +140 
                avatar_y =y +20 
                avatar_size =70 


                for border_layer in range (3 ):
                    border_size =avatar_size +(border_layer *6 )
                    border_x =avatar_x -(border_layer *3 )
                    border_y =avatar_y -(border_layer *3 )
                    alpha =200 -(border_layer *40 )

                    draw .ellipse (
                    (border_x ,border_y ,border_x +border_size ,border_y +border_size ),
                    outline =(*rank_color ,alpha ),width =3 
                    )


                try :
                    avatar_url =str (user .display_avatar .with_size (512 ).url )
                    response =requests .get (avatar_url ,timeout =10 )
                    if response .status_code ==200 :
                        avatar_img =Image .open (io .BytesIO (response .content ))
                        avatar_img =avatar_img .resize ((avatar_size ,avatar_size ),Image .Resampling .LANCZOS )


                        mask =Image .new ('L',(avatar_size ,avatar_size ),0 )
                        mask_draw =ImageDraw .Draw (mask )
                        mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )


                        avatar_img .putalpha (mask )
                        img .paste (avatar_img ,(avatar_x ,avatar_y ),avatar_img )
                    else :
                        raise Exception ("Failed to download avatar")
                except Exception as e :

                    draw .ellipse ((avatar_x ,avatar_y ,avatar_x +avatar_size ,avatar_y +avatar_size ),
                    fill =(40 ,40 ,50 ))


                    emoji ="👤"
                    emoji_bbox =draw .textbbox ((0 ,0 ),emoji ,font =name_font )
                    emoji_width =emoji_bbox [2 ]-emoji_bbox [0 ]
                    emoji_height =emoji_bbox [3 ]-emoji_bbox [1 ]
                    emoji_x =avatar_x +(avatar_size -emoji_width )//2 
                    emoji_y =avatar_y +(avatar_size -emoji_height )//2 
                    draw .text ((emoji_x ,emoji_y ),emoji ,font =name_font ,fill =accent_color )


                info_x =margin_left +240 
                username =user .display_name [:18 ]


                username_y =y +15 
                for shadow in [(4 ,4 ),(3 ,3 ),(2 ,2 ),(1 ,1 )]:
                    draw .text ((info_x +shadow [0 ],username_y +shadow [1 ]),username ,font =name_font ,fill =(0 ,0 ,0 ,150 ))
                draw .text ((info_x ,username_y ),username ,font =name_font ,fill =(255 ,255 ,255 ))


                level_text =f"Level {level:,}"
                level_badge_x =info_x 
                level_badge_y =y +55 
                level_bbox =draw .textbbox ((0 ,0 ),level_text ,font =stats_font )
                level_width =level_bbox [2 ]-level_bbox [0 ]


                draw .rounded_rectangle (
                (level_badge_x -8 ,level_badge_y -5 ,level_badge_x +level_width +16 ,level_badge_y +25 ),
                radius =12 ,fill =(*rank_color ,70 )
                )
                draw .rounded_rectangle (
                (level_badge_x -8 ,level_badge_y -5 ,level_badge_x +level_width +16 ,level_badge_y +25 ),
                radius =12 ,outline =rank_color ,width =2 
                )
                draw .text ((level_badge_x ,level_badge_y ),level_text ,font =stats_font ,fill =(255 ,255 ,255 ))


                info_spacing =30 
                xp_text =f"💎 {format_number(xp)} XP"
                msg_text =f"💬 {format_number(messages or 0)} msgs"

                xp_x =info_x +level_width +info_spacing 
                msg_x =xp_x +140 


                stats_bg_y =level_badge_y -2 
                stats_bg_height =24 
                draw .rounded_rectangle (
                (xp_x -5 ,stats_bg_y ,msg_x +150 ,stats_bg_y +stats_bg_height ),
                radius =8 ,fill =(0 ,0 ,0 ,100 )
                )

                draw .text ((xp_x ,level_badge_y ),xp_text ,font =stats_font ,fill =(200 ,220 ,255 ))
                draw .text ((msg_x ,level_badge_y ),msg_text ,font =stats_font ,fill =(255 ,200 ,150 ))


                bar_x =width -margin_right -380 
                bar_y =y +25 
                bar_width =320 
                bar_height =28 


                draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),
                radius =14 ,fill =(20 ,20 ,30 ,200 ))
                draw .rounded_rectangle ((bar_x ,bar_y ,bar_x +bar_width ,bar_y +bar_height ),
                radius =14 ,outline =(80 ,80 ,100 ),width =2 )


                current_level ,progress ,needed =get_level_progress (xp )
                if needed >0 :
                    progress_width =int ((progress /needed )*(bar_width -6 ))
                    if progress_width >0 :

                        for px in range (progress_width ):
                            factor =px /progress_width if progress_width >0 else 0 


                            base_color =rank_color 
                            brightness =0.4 +0.6 *factor 

                            fill_r =min (255 ,int (base_color [0 ]*brightness ))
                            fill_g =min (255 ,int (base_color [1 ]*brightness ))
                            fill_b =min (255 ,int (base_color [2 ]*brightness ))

                            draw .line ([(bar_x +3 +px ,bar_y +3 ),(bar_x +3 +px ,bar_y +bar_height -3 )],
                            fill =(fill_r ,fill_g ,fill_b ))


                        draw .rounded_rectangle (
                        (bar_x +2 ,bar_y +2 ,bar_x +3 +progress_width ,bar_y +bar_height -2 ),
                        radius =12 ,outline =rank_color ,width =2 
                        )


                percentage =(progress /needed *100 )if needed >0 else 100 
                progress_text =f"{percentage:.1f}% to Level {level + 1}"
                progress_bbox =draw .textbbox ((0 ,0 ),progress_text ,font =small_font )
                progress_text_width =progress_bbox [2 ]-progress_bbox [0 ]
                progress_text_x =bar_x +(bar_width -progress_text_width )//2 


                text_bg_y =bar_y +bar_height +8 
                draw .rounded_rectangle (
                (progress_text_x -12 ,text_bg_y -2 ,progress_text_x +progress_text_width +12 ,text_bg_y +18 ),
                radius =8 ,fill =(0 ,0 ,0 ,180 )
                )
                draw .text ((progress_text_x ,text_bg_y ),progress_text ,font =small_font ,fill =(255 ,255 ,255 ))


                xp_progress_text =f"{format_number(progress)} / {format_number(needed)} XP"
                xp_text_bbox =draw .textbbox ((0 ,0 ),xp_progress_text ,font =small_font )
                xp_text_width =xp_text_bbox [2 ]-xp_text_bbox [0 ]
                xp_text_x =bar_x +(bar_width -xp_text_width )//2 

                draw .text ((xp_text_x ,bar_y +6 ),xp_progress_text ,font =small_font ,fill =(200 ,200 ,200 ))


            footer_y =height -80 
            footer_bg_height =50 


            draw .rounded_rectangle (
            (60 ,footer_y ,width -60 ,footer_y +footer_bg_height ),
            radius =15 ,fill =(0 ,0 ,0 ,150 )
            )
            draw .rounded_rectangle (
            (60 ,footer_y ,width -60 ,footer_y +footer_bg_height ),
            radius =15 ,outline =(100 ,100 ,120 ),width =2 
            )

            footer_text =f"✨ Generated at {datetime.now(timezone.utc).strftime('%H:%M UTC')} • {len(top_users)} Active Members • {guild.name}"
            footer_bbox =draw .textbbox ((0 ,0 ),footer_text ,font =small_font )
            footer_width =footer_bbox [2 ]-footer_bbox [0 ]
            footer_x =(width -footer_width )//2 


            draw .text ((footer_x +2 ,footer_y +17 ),footer_text ,font =small_font ,fill =(0 ,0 ,0 ,200 ))
            draw .text ((footer_x ,footer_y +15 ),footer_text ,font =small_font ,fill =(220 ,220 ,240 ))


            img_bytes =io .BytesIO ()
            img .save (img_bytes ,format ='PNG')
            img_bytes .seek (0 )
            img .close ()
            return img_bytes 

        except Exception as e :
            logger .error (f"Error creating leaderboard image: {e}")
            return self .create_text_leaderboard (guild ,top_users )

    def create_text_leaderboard (self ,guild ,top_users ):
        """Create text-based leaderboard when image creation fails"""
        try :
            leaderboard_text =f"🏆 **{guild.name} Level Leaderboard** 🏆\n\n"

            for i ,(user_id ,xp ,messages )in enumerate (top_users ):
                user =guild .get_member (user_id )
                if not user :
                    continue 

                level =calculate_level_from_xp (xp )

                if i ==0 :
                    emoji ="🥇"
                elif i ==1 :
                    emoji ="🥈"
                elif i ==2 :
                    emoji ="🥉"
                else :
                    emoji =f"#{i + 1}"

                leaderboard_text +=f"{emoji} **{user.display_name}**\n"
                leaderboard_text +=f"    Level {level:,} • {format_number(xp)} XP • {format_number(messages or 0)} messages\n\n"

            return leaderboard_text 

        except Exception as e :
            logger .error (f"Error creating text leaderboard: {e}")
            return "Failed to generate leaderboard."

    @level .command (name ="placeholders",description ="Show available placeholders for level-up messages")
    async def placeholders (self ,ctx ):
        """Show placeholders for level-up messages"""
        embed =discord .Embed (
        title ="📝 Available Placeholders",
        description =(
        "**You can use these placeholders in your level-up message:**\n\n"
        "`{user}` - Mentions the user (@username)\n"
        "`{username}` - User's display name\n"
        "`{level}` - The new level reached\n"
        "`{server}` - Server name\n\n"
        "**Example:**\n"
        "`Congratulations {user}! You've reached level {level} in {server}!`"
        ),
        color =0x00BFFF ,
        timestamp =datetime .now (timezone .utc )
        )
        await ctx .send (embed =embed )

    @level .command (name ="enable",description ="Enable the leveling system")
    @commands .has_permissions (administrator =True )
    async def enable (self ,ctx ):
        try :
            async with aiosqlite .connect (self .db_path )as db :

                async with db .execute ("SELECT enabled FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    result =await cursor .fetchone ()

                if result :
                    if result [0 ]==1 :
                        await ctx .send (f"{ZWARNING} Leveling system is already enabled!")
                        return 

                    await db .execute ("UPDATE leveling_settings SET enabled = 1 WHERE guild_id = ?",(ctx .guild .id ,))
                else :

                    await db .execute ("INSERT INTO leveling_settings (guild_id, enabled) VALUES (?, 1)",(ctx .guild .id ,))

                await db .commit ()

            embed =discord .Embed (
            title =f"{TICK} Leveling System Enabled",
            description ="The leveling system has been successfully enabled for this server!\n\n"
            "**Next Steps:**\n"
            "• Use `/level settings` to configure XP rates and messages\n"
            "• Use `/level channel` to set level-up announcement channel\n"
            "• Use `/level rewards add` to set up level rewards",
            color =0x00FF00 ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error enabling leveling system: {e}")
            pass 

    @level .command (name ="disable",description ="Disable the leveling system")
    @commands .has_permissions (administrator =True )
    async def disable (self ,ctx ):
        try :
            async with aiosqlite .connect (self .db_path )as db :

                async with db .execute ("SELECT enabled FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    result =await cursor .fetchone ()

                if not result :
                    await ctx .send (f"{ZWARNING} Leveling system is not configured for this server!")
                    return 

                if result [0 ]==0 :
                    await ctx .send (f"{ZWARNING} Leveling system is already disabled!")
                    return 

                await db .execute ("UPDATE leveling_settings SET enabled = 0 WHERE guild_id = ?",(ctx .guild .id ,))
                await db .commit ()

            embed =discord .Embed (
            title =f"{CROSS} Leveling System Disabled",
            description ="The leveling system has been disabled for this server.\n\n"
            "**What this means:**\n"
            "• Users will no longer gain XP from messages\n"
            "• Level-up notifications will stop\n"
            "• Existing user data is preserved\n"
            "• Use `/level enable` to re-enable anytime",
            color =0xFF0000 ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error disabling leveling system: {e}")
            pass 

    @level .command (name ="stats",description ="View detailed level statistics")
    async def stats (self ,ctx ,member :Optional [discord .Member ]=None ):
        """Display detailed user level statistics with rank card"""
        member =member or ctx .author 
        guild_id =ctx .guild .id 

        try :

            xp ,level ,messages =await self .get_user_data (guild_id ,member .id )
            rank =await self .get_user_rank (guild_id ,member .id )


            current_level ,progress ,needed =get_level_progress (xp )
            next_level =level +1 
            percentage =(progress /needed *100 )if needed >0 else 100 


            async with aiosqlite .connect ("db/leveling.db")as db :
                async with db .execute (
                "SELECT COUNT(*) FROM user_xp WHERE guild_id = ? AND xp > 0",
                (guild_id ,)
                )as cursor :
                    total_members =(await cursor .fetchone ())[0 ]


            avg_xp_per_message =(xp /messages )if messages >0 else 0 
            xp_to_next_level =needed -progress 


            embed =discord .Embed (
            title =f"📊 Level Statistics for {member.display_name}",
            color =0xFF0000 ,
            timestamp =datetime .now (timezone .utc )
            )


            embed .add_field (
            name ="🎯 Basic Stats",
            value =f"**Level:** {level:,}\n"
            f"**Total XP:** {format_number(xp)}\n"
            f"**Server Rank:** #{rank:,} / {total_members:,}\n"
            f"**Messages Sent:** {format_number(messages)}",
            inline =True 
            )


            embed .add_field (
            name ="📈 Progress to Level {next_level}",
            value =f"**Current Progress:** {format_number(progress)} / {format_number(needed)} XP\n"
            f"**Percentage:** {percentage:.1f}%\n"
            f"**XP Needed:** {format_number(xp_to_next_level)}\n"
            f"**Progress Bar:** {get_progress_bar(progress, needed, 15)}",
            inline =True 
            )


            embed .add_field (
            name ="📊 Additional Stats",
            value =f"**Avg XP/Message:** {avg_xp_per_message:.1f}\n"
            f"**XP for Level {level}:** {format_number(calculate_xp_for_level(level))}\n"
            f"**XP for Level {next_level}:** {format_number(calculate_xp_for_level(next_level))}\n"
            f"**Total Levels Gained:** {level - 1:,}",
            inline =True 
            )


            percentile =((total_members -rank +1 )/total_members *100 )if total_members >0 else 0 


            if rank ==1 :
                tier ="🏆 Champion"
                tier_color =0xFFD700 
            elif rank <=3 :
                tier ="🥇 Elite"
                tier_color =0xC0C0C0 
            elif rank <=10 :
                tier ="⭐ Expert"
                tier_color =0xCD7F32 
            elif percentile >=90 :
                tier ="💎 Advanced"
                tier_color =0x00FFFF 
            elif percentile >=70 :
                tier ="🔥 Experienced"
                tier_color =0xFF4500 
            elif percentile >=50 :
                tier ="⚡ Intermediate"
                tier_color =0xFFFF00 
            elif percentile >=25 :
                tier ="🌟 Beginner"
                tier_color =0x90EE90 
            else :
                tier ="🌱 Newcomer"
                tier_color =0x98FB98 

            embed .add_field (
            name ="🏅 Rank Information",
            value =f"**Tier:** {tier}\n"
            f"**Percentile:** Top {100-percentile:.1f}%\n"
            f"**Users Below:** {total_members - rank:,}\n"
            f"**Users Above:** {rank - 1:,}",
            inline =False 
            )


            embed .color =tier_color 


            embed .set_thumbnail (url =member .display_avatar .url )


            embed .set_footer (
            text =f"Requested by {ctx.author.display_name} • {ctx.guild.name}",
            icon_url =ctx .author .display_avatar .url 
            )


            rank_card =await self .create_rank_card (member ,guild_id )

            if rank_card and not isinstance (rank_card ,str ):

                file =discord .File (fp =rank_card ,filename ="rank_card.png")
                embed .set_image (url ="attachment://rank_card.png")
                await ctx .send (embed =embed ,file =file )
                try :
                    rank_card .close ()
                except :
                    pass 
            else :

                await ctx .send (embed =embed )
                if isinstance (rank_card ,str ):

                    await ctx .send (f"```{rank_card}```")

        except Exception as e :
            logger .error (f"Error in level stats command: {e}")
            pass 

    @level .command (name ="channel",description ="Set the level-up announcement channel")
    @commands .has_permissions (administrator =True )
    async def channel (self ,ctx ,channel :discord .TextChannel ):
        try :
            async with aiosqlite .connect (self .db_path )as db :

                async with db .execute ("SELECT guild_id FROM leveling_settings WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    result =await cursor .fetchone ()

                if result :
                    await db .execute ("UPDATE leveling_settings SET channel_id = ? WHERE guild_id = ?",(channel .id ,ctx .guild .id ))
                else :
                    await db .execute ("INSERT INTO leveling_settings (guild_id, channel_id) VALUES (?, ?)",(ctx .guild .id ,channel .id ))

                await db .commit ()

            embed =discord .Embed (
            title ="📢 Level-Up Channel Set",
            description =f"Level-up messages will now be sent in {channel.mention}\n\n"
            "**Note:** Make sure the bot has permission to send messages in this channel!",
            color =0x00BFFF ,
            timestamp =datetime .now (timezone .utc )
            )
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error setting level channel: {e}")
            pass 

