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
from discord .ext import commands 
from discord import app_commands 
import aiosqlite 
import random 
import string 
import io 
from PIL import Image ,ImageDraw ,ImageFont 
import asyncio 
import logging 
from datetime import datetime ,timezone ,timedelta 
from typing import Optional 
from utils .Tools import *


logger =logging .getLogger ('discord')

DATABASE_PATH ='db/verification.db'


DISCORD_COLORS ={
'primary':0xFF0000 ,
'success':0xFF0000 ,
'warning':0xFF0000 ,
'error':0xFF0000 ,
'secondary':0xFF0000 ,
'neutral':0xFF0000 
}


def utc_to_ist (dt :datetime )->datetime :
    ist_offset =timedelta (hours =5 ,minutes =30 )
    return dt .replace (tzinfo =timezone .utc ).astimezone (timezone (ist_offset ))


async def check_bot_permissions (guild :discord .Guild ,channel =None )->dict :
    """Check if bot has necessary permissions"""
    bot_member =guild .me 
    required_perms ={
    'guild':['manage_roles','manage_channels','send_messages','manage_messages'],
    'channel':['view_channel','send_messages','attach_files','embed_links','manage_messages']
    }

    missing_perms ={'guild':[],'channel':[]}


    for perm in required_perms ['guild']:
        if not getattr (bot_member .guild_permissions ,perm ):
            missing_perms ['guild'].append (perm .replace ('_',' ').title ())


    if channel and hasattr (channel ,'permissions_for'):
        channel_perms =channel .permissions_for (bot_member )
        for perm in required_perms ['channel']:
            if not getattr (channel_perms ,perm ):
                missing_perms ['channel'].append (perm .replace ('_',' ').title ())

    return missing_perms 


def validate_role_hierarchy (guild :discord .Guild ,role :discord .Role )->bool :
    """Check if bot can manage the specified role"""
    bot_top_role =guild .me .top_role 
    return bot_top_role .position >role .position 

async def create_verified_role (guild :discord .Guild )->discord .Role :
    """Create a verified role with proper permissions"""
    try :

        existing_role =discord .utils .get (guild .roles ,name ="Verified")
        if existing_role :
            return existing_role 


        verified_role =await guild .create_role (
        name ="Verified",
        color =discord .Color .from_rgb (35 ,165 ,90 ),
        reason ="Auto-created for verification system",
        permissions =discord .Permissions (
        read_messages =True ,
        send_messages =True ,
        read_message_history =True ,
        use_external_emojis =True ,
        add_reactions =True ,
        attach_files =True ,
        embed_links =True ,
        connect =True ,
        speak =True ,
        use_voice_activation =True 
        )
        )


        bot_roles =[role for role in guild .roles if role .managed and role .members and guild .me in role .members ]
        position =1 
        if bot_roles :
            position =min (role .position for role in bot_roles )-1 

        await verified_role .edit (position =max (1 ,position ))

        return verified_role 
    except Exception as e :
        logger .error (f"Error creating verified role: {e}")
        raise 

async def auto_fix_permissions (guild :discord .Guild ,verification_channel :discord .TextChannel ,verified_role :discord .Role ):
    """Automatically fix channel permissions for verification system"""
    try :
        everyone_role =guild .default_role 
        bot_member =guild .me 
        failed_channels =[]


        try :
            await verification_channel .set_permissions (
            everyone_role ,
            view_channel =True ,
            send_messages =False ,
            add_reactions =False ,
            reason ="Auto-fix: Verification channel permissions"
            )
            await verification_channel .set_permissions (
            verified_role ,
            view_channel =False ,
            reason ="Auto-fix: Hide verification from verified users"
            )
            await verification_channel .set_permissions (
            bot_member ,
            view_channel =True ,
            send_messages =True ,
            manage_messages =True ,
            embed_links =True ,
            attach_files =True ,
            reason ="Auto-fix: Bot verification permissions"
            )
        except discord .Forbidden :
            logger .warning (f"Cannot fix permissions for verification channel: {verification_channel.name}")


        for channel in guild .channels :
            if isinstance (channel ,(discord .TextChannel ,discord .VoiceChannel ,discord .CategoryChannel )):
                if channel .id !=verification_channel .id :
                    try :

                        current_overwrites =channel .overwrites 


                        everyone_perms =current_overwrites .get (everyone_role )
                        if not everyone_perms or everyone_perms .view_channel is not False :
                            await channel .set_permissions (
                            everyone_role ,
                            view_channel =False ,
                            reason ="Auto-fix: Verification system privacy"
                            )


                        verified_perms =current_overwrites .get (verified_role )
                        if not verified_perms or verified_perms .view_channel is not True :
                            await channel .set_permissions (
                            verified_role ,
                            view_channel =True ,
                            reason ="Auto-fix: Verified role access"
                            )
                    except discord .Forbidden :
                        failed_channels .append (channel .name )

        if failed_channels :
            logger .warning (f"Failed to auto-fix permissions for channels: {', '.join(failed_channels)}")

        return len (failed_channels )

    except Exception as e :
        logger .error (f"Error in auto-fix permissions: {e}")
        return -1 

class VerificationModal (discord .ui .Modal ,title ="Enter Verification Code"):
    def __init__ (self ,bot ,captcha_code :str ,guild_id :int ):
        super ().__init__ ()
        self .bot =bot 
        self .captcha_code =captcha_code 
        self .guild_id =guild_id 

    captcha_input =discord .ui .TextInput (
    label ="Verification Code",
    placeholder ="Enter the 6-character code from the image",
    required =True ,
    max_length =6 ,
    min_length =6 
    )

    async def on_submit (self ,interaction :discord .Interaction ):
        try :
            if self .captcha_input .value .strip ()!=self .captcha_code :
                embed =discord .Embed (
                title ="Incorrect Code",
                description ="The code you entered is incorrect. Please try again by clicking the verification button in the server.",
                color =DISCORD_COLORS ['error']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )
                return 

            guild =self .bot .get_guild (self .guild_id )
            if not guild :
                await interaction .response .send_message ("Server not found.",ephemeral =True )
                return 

            member =guild .get_member (interaction .user .id )
            if not member :
                await interaction .response .send_message ("You are not in the server.",ephemeral =True )
                return 


            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await interaction .response .send_message ("Verification system is not configured.",ephemeral =True )
                        return 

                    verified_role =guild .get_role (result [0 ])
                    if not verified_role :
                        await interaction .response .send_message ("Verified role not found.",ephemeral =True )
                        return 


                    if verified_role in member .roles :
                        embed =discord .Embed (
                        title ="Already Verified",
                        description ="You are already verified in this server!",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            await member .add_roles (verified_role ,reason ="CAPTCHA verification completed")


            await self .log_verification (guild .id ,member .id ,"captcha")

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Verification Successful",
            description =f"Welcome to **{guild.name}**!\n\n"
            f"You have been successfully verified and can now access all channels.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verified at {current_time.strftime('%I:%M %p IST')}")

            await interaction .response .send_message (embed =embed ,ephemeral =True )


            await self .send_verification_log (guild ,member ,"CAPTCHA",True )

        except discord .Forbidden :
            await interaction .response .send_message ("Bot lacks permission to assign roles.",ephemeral =True )
        except Exception as e :
            logger .error (f"Error in verification modal: {e}")
            pass 

    async def log_verification (self ,guild_id :int ,user_id :int ,method :str ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    current_time =utc_to_ist (discord .utils .utcnow ())
                    await cur .execute (
                    "INSERT INTO verification_logs (guild_id, user_id, verification_method, verified_at) VALUES (?, ?, ?, ?)",
                    (guild_id ,user_id ,method ,current_time .isoformat ())
                    )
                    await db .commit ()
        except Exception as e :
            logger .error (f"Error logging verification: {e}")

    async def send_verification_log (self ,guild :discord .Guild ,user :discord .Member ,method :str ,success :bool ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT log_channel_id FROM verification_config WHERE guild_id = ?",
                    (guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if result and result [0 ]:
                        log_channel =guild .get_channel (result [0 ])
                        if log_channel and log_channel .permissions_for (guild .me ).send_messages :
                            current_time =utc_to_ist (discord .utils .utcnow ())
                            embed =discord .Embed (
                            title ="User Verification Log",
                            color =DISCORD_COLORS ['success']if success else DISCORD_COLORS ['error'],
                            timestamp =current_time 
                            )
                            embed .add_field (
                            name ="User Information",
                            value =f"**User:** {user.mention}\n**ID:** {user.id}\n**Username:** {user.name}",
                            inline =False 
                            )
                            embed .add_field (
                            name ="Verification Details",
                            value =f"**Method:** {method}\n**Status:** {'Success' if success else 'Failed'}\n**Time:** {current_time.strftime('%I:%M %p IST')}",
                            inline =False 
                            )
                            embed .set_thumbnail (url =user .avatar .url if user .avatar else user .default_avatar .url )
                            await log_channel .send (embed =embed )
        except Exception as e :
            logger .error (f"Error sending verification log: {e}")

class VerificationView (discord .ui .View ):
    def __init__ (self ,bot ):
        super ().__init__ (timeout =None )
        self .bot =bot 

    @discord .ui .button (label ="Quick Verify",style =discord .ButtonStyle .green ,custom_id ="verify_button_quick")
    async def verify_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id, verification_method FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="System Unavailable",
                        description ="Verification system is not configured or disabled.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    verification_method =result [1 ]

                    if not verified_role :
                        embed =discord .Embed (
                        description ="Verified role not found. Please contact an administrator.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Already Verified",
                        description ="You are already verified! You can access all channels.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            if verification_method not in ["button","both"]:
                embed =discord .Embed (
                title ="CAPTCHA Required",
                description ="This server requires CAPTCHA verification. Please use the CAPTCHA button below.",
                color =DISCORD_COLORS ['warning']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )
                return 


            await interaction .user .add_roles (verified_role ,reason ="Quick button verification")


            modal =VerificationModal (self .bot ,"",interaction .guild .id )
            await modal .log_verification (interaction .guild .id ,interaction .user .id ,"button")
            await modal .send_verification_log (interaction .guild ,interaction .user ,"BUTTON",True )

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Welcome to the Server",
            description =f"**{interaction.user.mention}** has been verified!\n\n"
            f"Welcome to {interaction.guild.name}!\n"
            f"You now have access to all channels.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verified at {current_time.strftime('%I:%M %p IST')}")

            await interaction .response .send_message (embed =embed ,ephemeral =True )

        except discord .Forbidden :
            embed =discord .Embed (
            description ="Bot lacks permission to assign roles. Please contact an administrator.",
            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )
        except Exception as e :
            logger .error (f"Error in verify button: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

    @discord .ui .button (label ="CAPTCHA Verify",style =discord .ButtonStyle .primary ,custom_id ="verify_captcha_secure")
    async def verify_captcha (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="System Unavailable",
                        description ="Verification system is not configured or disabled.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    if not verified_role :
                        embed =discord .Embed (
                        description ="Verified role not found. Please contact an administrator.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Already Verified",
                        description ="You are already verified! You can access all channels.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            captcha_code =self .generate_captcha_code ()
            captcha_image =self .create_captcha_image (captcha_code )

            try :

                file =discord .File (captcha_image ,filename ="captcha.png")
                embed =discord .Embed (
                title ="CAPTCHA Verification",
                description =f"**Server:** {interaction.guild.name}\n\n"
                f"Please solve the CAPTCHA below to verify yourself.\n"
                f"Click the button below to enter your answer.\n\n"
                f"**Important:** The code is case-sensitive!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_image (url ="attachment://captcha.png")
                embed .set_footer (text ="This CAPTCHA will expire in 10 minutes")

                modal =VerificationModal (self .bot ,captcha_code ,interaction .guild .id )
                view =CaptchaModalView (modal )

                await interaction .user .send (embed =embed ,file =file ,view =view )


                embed =discord .Embed (
                title ="Check Your DMs",
                description ="I've sent you a CAPTCHA in your direct messages.\n\n"
                f"**Steps:**\n"
                f"1. Check your DMs from me\n"
                f"2. Solve the CAPTCHA image\n"
                f"3. Click the button to enter your answer\n\n"
                f"Make sure your DMs are open!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_footer (text ="CAPTCHA expires in 10 minutes")
                await interaction .response .send_message (embed =embed ,ephemeral =True )

            except discord .Forbidden :
                embed =discord .Embed (
                title ="DMs Disabled",
                description ="I couldn't send you a DM! Please enable DMs from server members and try again.\n\n"
                f"**How to enable DMs:**\n"
                f"1. Right-click on **{interaction.guild.name}**\n"
                f"2. Go to **Privacy Settings**\n"
                f"3. Enable **Direct Messages**\n"
                f"4. Try verification again",
                color =DISCORD_COLORS ['error']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error in verify captcha: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

    def generate_captcha_code (self )->str :
        """Generate a random 6-character alphanumeric code"""
        return ''.join (random .choices (string .ascii_letters +string .digits ,k =6 ))

    def create_captcha_image (self ,code :str )->io .BytesIO :
        """Create a CAPTCHA image with the given code"""

        width ,height =300 ,120 
        image =Image .new ('RGB',(width ,height ),color ='white')
        draw =ImageDraw .Draw (image )


        for y in range (height ):
            color_value =255 -int ((y /height )*50 )
            for x in range (width ):
                draw .point ((x ,y ),fill =(color_value ,color_value ,255 ))


        for _ in range (200 ):
            x =random .randint (0 ,width )
            y =random .randint (0 ,height )
            draw .point ((x ,y ),fill =(random .randint (150 ,200 ),random .randint (150 ,200 ),random .randint (150 ,200 )))


        for _ in range (8 ):
            x1 =random .randint (0 ,width )
            y1 =random .randint (0 ,height )
            x2 =random .randint (0 ,width )
            y2 =random .randint (0 ,height )
            draw .line ([(x1 ,y1 ),(x2 ,y2 )],fill =(random .randint (100 ,150 ),random .randint (100 ,150 ),random .randint (100 ,150 )),width =2 )


        try :
            font =ImageFont .truetype ("utils/arial.ttf",40 )
        except :
            try :
                font =ImageFont .load_default ()
            except :
                font =None 


        if font :
            bbox =draw .textbbox ((0 ,0 ),code ,font =font )
            text_width =bbox [2 ]-bbox [0 ]
            text_height =bbox [3 ]-bbox [1 ]
        else :
            text_width =len (code )*20 
            text_height =20 

        start_x =(width -text_width )//2 
        start_y =(height -text_height )//2 


        for i ,char in enumerate (code ):
            char_x =start_x +(i *text_width //len (code ))+random .randint (-8 ,8 )
            char_y =start_y +random .randint (-15 ,15 )


            color =(random .randint (0 ,100 ),random .randint (0 ,100 ),random .randint (0 ,100 ))

            if font :
                draw .text ((char_x ,char_y ),char ,fill =color ,font =font )
            else :
                draw .text ((char_x ,char_y ),char ,fill =color )


        draw .rectangle ([(0 ,0 ),(width -1 ,height -1 )],outline ='black',width =2 )


        img_buffer =io .BytesIO ()
        image .save (img_buffer ,format ='PNG',quality =95 )
        img_buffer .seek (0 )

        return img_buffer 



class CaptchaOnlyVerificationView (discord .ui .View ):
    def __init__ (self ,bot ):
        super ().__init__ (timeout =None )
        self .bot =bot 

    @discord .ui .button (label ="Verify with CAPTCHA",style =discord .ButtonStyle .primary ,custom_id ="verify_captcha_only")
    async def verify_captcha (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="System Unavailable",
                        description ="Verification system is not configured or disabled.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    if not verified_role :
                        embed =discord .Embed (
                        description ="Verified role not found. Please contact an administrator.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Already Verified",
                        description ="You are already verified! You can access all channels.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            captcha_code =self .generate_captcha_code ()
            captcha_image =self .create_captcha_image (captcha_code )

            try :

                file =discord .File (captcha_image ,filename ="captcha.png")
                embed =discord .Embed (
                title ="CAPTCHA Verification",
                description =f"**Server:** {interaction.guild.name}\n\n"
                f"Please solve the CAPTCHA below to verify yourself.\n"
                f"Click the button below to enter your answer.\n\n"
                f"**Important:** The code is case-sensitive!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_image (url ="attachment://captcha.png")
                embed .set_footer (text ="This CAPTCHA will expire in 10 minutes")

                modal =VerificationModal (self .bot ,captcha_code ,interaction .guild .id )
                view =CaptchaModalView (modal )

                await interaction .user .send (embed =embed ,file =file ,view =view )


                embed =discord .Embed (
                title ="Check Your DMs",
                description ="I've sent you a CAPTCHA in your direct messages.\n\n"
                f"**Steps:**\n"
                f"1. Check your DMs from me\n"
                f"2. Solve the CAPTCHA image\n"
                f"3. Click the button to enter your answer\n\n"
                f"Make sure your DMs are open!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_footer (text ="CAPTCHA expires in 10 minutes")
                await interaction .response .send_message (embed =embed ,ephemeral =True )

            except discord .Forbidden :
                embed =discord .Embed (
                title ="DMs Disabled",
                description ="I couldn't send you a DM! Please enable DMs from server members and try again.\n\n"
                f"**How to enable DMs:**\n"
                f"1. Right-click on **{interaction.guild.name}**\n"
                f"2. Go to **Privacy Settings**\n"
                f"3. Enable **Direct Messages**\n"
                f"4. Try verification again",
                color =DISCORD_COLORS ['error']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error in verify captcha: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

    def generate_captcha_code (self )->str :
        """Generate a random 6-character alphanumeric code"""
        return ''.join (random .choices (string .ascii_letters +string .digits ,k =6 ))

    def create_captcha_image (self ,code :str )->io .BytesIO :
        """Create a CAPTCHA image with the given code"""

        width ,height =300 ,120 
        image =Image .new ('RGB',(width ,height ),color ='white')
        draw =ImageDraw .Draw (image )


        for y in range (height ):
            color_value =255 -int ((y /height )*50 )
            for x in range (width ):
                draw .point ((x ,y ),fill =(color_value ,color_value ,255 ))


        for _ in range (200 ):
            x =random .randint (0 ,width )
            y =random .randint (0 ,height )
            draw .point ((x ,y ),fill =(random .randint (150 ,200 ),random .randint (150 ,200 ),random .randint (150 ,200 )))


        for _ in range (8 ):
            x1 =random .randint (0 ,width )
            y1 =random .randint (0 ,height )
            x2 =random .randint (0 ,width )
            y2 =random .randint (0 ,height )
            draw .line ([(x1 ,y1 ),(x2 ,y2 )],fill =(random .randint (100 ,150 ),random .randint (100 ,150 ),random .randint (100 ,150 )),width =2 )


        try :
            font =ImageFont .truetype ("utils/arial.ttf",40 )
        except :
            try :
                font =ImageFont .load_default ()
            except :
                font =None 


        if font :
            bbox =draw .textbbox ((0 ,0 ),code ,font =font )
            text_width =bbox [2 ]-bbox [0 ]
            text_height =bbox [3 ]-bbox [1 ]
        else :
            text_width =len (code )*20 
            text_height =20 

        start_x =(width -text_width )//2 
        start_y =(height -text_height )//2 


        for i ,char in enumerate (code ):
            char_x =start_x +(i *text_width //len (code ))+random .randint (-8 ,8 )
            char_y =start_y +random .randint (-15 ,15 )


            color =(random .randint (0 ,100 ),random .randint (0 ,100 ),random .randint (0 ,100 ))

            if font :
                draw .text ((char_x ,char_y ),char ,fill =color ,font =font )
            else :
                draw .text ((char_x ,char_y ),char ,fill =color )


        draw .rectangle ([(0 ,0 ),(width -1 ,height -1 )],outline ='black',width =2 )


        img_buffer =io .BytesIO ()
        image .save (img_buffer ,format ='PNG',quality =95 )
        img_buffer .seek (0 )

        return img_buffer 

class CaptchaModalView (discord .ui .View ):
    def __init__ (self ,modal :VerificationModal ):
        super ().__init__ (timeout =600 )
        self .modal =modal 

    @discord .ui .button (label ="Enter Code",style =discord .ButtonStyle .secondary ,custom_id ="enter_captcha_code")
    async def enter_captcha (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        await interaction .response .send_modal (self .modal )

class VerificationSetupView (discord .ui .View ):
    def __init__ (self ,bot ,ctx ):
        super ().__init__ (timeout =300 )
        self .bot =bot 
        self .ctx =ctx 
        self .verification_channel =None 
        self .log_channel =None 
        self .verification_method ="both"

    @discord .ui .select (
    cls =discord .ui .ChannelSelect ,
    channel_types =[discord .ChannelType .text ],
    placeholder ="Select verification channel..."
    )
    async def verification_channel_select (self ,interaction :discord .Interaction ,select :discord .ui .ChannelSelect ):
        await interaction .response .defer ()
        selected_channel =select .values [0 ]
        self .verification_channel =interaction .guild .get_channel (selected_channel .id )

    @discord .ui .select (
    cls =discord .ui .ChannelSelect ,
    channel_types =[discord .ChannelType .text ],
    placeholder ="Select log channel (optional)..."
    )
    async def log_channel_select (self ,interaction :discord .Interaction ,select :discord .ui .ChannelSelect ):
        await interaction .response .defer ()
        selected_channel =select .values [0 ]
        self .log_channel =interaction .guild .get_channel (selected_channel .id )

    @discord .ui .select (
    placeholder ="Select verification method...",
    options =[
    discord .SelectOption (
    label ="Quick Button Only",
    value ="button",
    description ="Users verify instantly by clicking a button"
    ),
    discord .SelectOption (
    label ="CAPTCHA Only",
    value ="captcha",
    description ="Users must solve a CAPTCHA (more secure)"
    ),
    discord .SelectOption (
    label ="Both Methods",
    value ="both",
    description ="Users can choose between button or CAPTCHA"
    )
    ]
    )
    async def method_select (self ,interaction :discord .Interaction ,select :discord .ui .Select ):
        await interaction .response .defer ()
        self .verification_method =select .values [0 ]

    @discord .ui .button (label ="Setup Verification System",style =discord .ButtonStyle .green )
    async def setup_verification (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        if not self .verification_channel :
            embed =discord .Embed (
            title ="Missing Configuration",
            description ="Please select a verification channel first!",
            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )
            return 

        try :
            await interaction .response .defer (ephemeral =True )


            verified_role =await create_verified_role (interaction .guild )


            failed_count =await auto_fix_permissions (interaction .guild ,self .verification_channel ,verified_role )


            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    """INSERT OR REPLACE INTO verification_config 
                           (guild_id, verification_channel_id, verified_role_id, log_channel_id, verification_method, enabled) 
                           VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                    interaction .guild .id ,
                    self .verification_channel .id ,
                    verified_role .id ,
                    self .log_channel .id if self .log_channel else None ,
                    self .verification_method ,
                    True 
                    )
                    )
                    await db .commit ()


            await self .send_verification_panel (verified_role )


            try :
                await asyncio .sleep (5 )
                if hasattr (interaction ,'message')and interaction .message :
                    await interaction .message .delete ()
            except discord .NotFound :
                pass 
            except discord .Forbidden :
                pass 
            except Exception as e :
                logger .error (f"Error deleting setup embed: {e}")

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Verification System Setup Complete",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .add_field (
            name ="Configuration Summary",
            value =f"**Verification Channel:** {self.verification_channel.mention}\n"
            f"**Verified Role:** {verified_role.mention}\n"
            f"**Log Channel:** {self.log_channel.mention if self.log_channel else 'None'}\n"
            f"**Method:** {self.verification_method.title()}",
            inline =False 
            )

            security_features ="All channels made private to unverified users\n" "Verification channel locked for unverified users\n" "Auto-message deletion in verification channel\n" "DM-based CAPTCHA system\n" "Comprehensive logging enabled"

            if failed_count >0 :
                security_features +=f"\n\nNote: {failed_count} channels couldn't be auto-fixed due to permissions"

            embed .add_field (
            name ="Security Features",
            value =security_features ,
            inline =False 
            )
            embed .add_field (
            name ="System Status",
            value =f"{TICK} **Verification system is now ENABLED and ready to use!**",
            inline =False 
            )
            embed .set_footer (text =f"Setup completed and enabled at {current_time.strftime('%I:%M %p IST')}")


            await interaction .followup .send (embed =embed ,ephemeral =True )


            try :
                await asyncio .sleep (3 )
                if hasattr (interaction ,'message')and interaction .message :
                    await interaction .message .delete ()
            except discord .NotFound :
                pass 
            except discord .Forbidden :
                pass 
            except Exception as e :
                logger .error (f"Error deleting setup embed: {e}")

            self .stop ()

        except Exception as e :
            logger .error (f"Error setting up verification: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await interaction .followup .send (embed =embed ,ephemeral =True )

    async def send_verification_panel (self ,verified_role :discord .Role ):
        """Send the verification panel to the verification channel"""
        try :
            channel =self .verification_channel 
            current_time =utc_to_ist (discord .utils .utcnow ())

            embed =discord .Embed (
            title ="Server Verification Required",
            description =f"**Welcome to {channel.guild.name}!**\n\n"
            f"To access all channels and features, you need to verify yourself first.\n\n"
            f"**Choose your verification method:**",
            color =DISCORD_COLORS ['primary'],
            timestamp =current_time 
            )

            if self .verification_method in ["button","both"]:
                embed .add_field (
                name ="Quick Verification",
                value ="Instant access with one click! Perfect for trusted users.",
                inline =True 
                )

            if self .verification_method in ["captcha","both"]:
                embed .add_field (
                name ="CAPTCHA Verification",
                value ="Secure verification via DM. Proves you're human!",
                inline =True 
                )

            embed .add_field (
            name ="What happens after verification?",
            value =f"• Access to all server channels\n"
            f"• Ability to chat and participate\n"
            f"• Access to all server features\n"
            f"• **{verified_role.name}** role assigned",
            inline =False 
            )

            embed .set_footer (text =f"Verification panel • {current_time.strftime('%I:%M %p IST')}")


            if self .verification_method =="button":
                view =ButtonOnlyVerificationView (self .bot )
            elif self .verification_method =="captcha":
                view =CaptchaOnlyVerificationView (self .bot )
            else :
                view =VerificationView (self .bot )

            await channel .send (embed =embed ,view =view )

        except Exception as e :
            logger .error (f"Error sending verification panel: {e}")

class ButtonOnlyVerificationView (discord .ui .View ):
    def __init__ (self ,bot ):
        super ().__init__ (timeout =None )
        self .bot =bot 

    @discord .ui .button (label ="Verify Now",style =discord .ButtonStyle .green ,custom_id ="verify_button_only")
    async def verify_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id, verification_method FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="System Unavailable",
                        description ="Verification system is not configured or disabled.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    verification_method =result [1 ]

                    if not verified_role :
                        embed =discord .Embed (
                        description ="Verified role not found. Please contact an administrator.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Already Verified",
                        description ="You are already verified! You can access all channels.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            await interaction .user .add_roles (verified_role ,reason ="Quick button verification")


            modal =VerificationModal (self .bot ,"",interaction .guild .id )
            await modal .log_verification (interaction .guild .id ,interaction .user .id ,"button")
            await modal .send_verification_log (interaction .guild ,interaction .user ,"BUTTON",True )

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Welcome to the Server",
            description =f"**{interaction.user.mention}** has been verified!\n\n"
            f"Welcome to {interaction.guild.name}!\n"
            f"You now have access to all channels.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verified at {current_time.strftime('%I:%M %p IST')}")

            await interaction .response .send_message (embed =embed ,ephemeral =True )

        except discord .Forbidden :
            embed =discord .Embed (
            description ="Bot lacks permission to assign roles. Please contact an administrator.",
            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )
        except Exception as e :
            logger .error (f"Error in verify button: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

class Verification (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .bot .loop .create_task (self .create_tables ())

        self .bot .add_view (VerificationView (self .bot ))
        self .bot .add_view (ButtonOnlyVerificationView (self .bot ))
        self .bot .add_view (CaptchaOnlyVerificationView (self .bot ))

    async def create_tables (self ):
        """Create database tables for verification system"""
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS verification_config (
                        guild_id INTEGER PRIMARY KEY,
                        verification_channel_id INTEGER NOT NULL,
                        verified_role_id INTEGER NOT NULL,
                        log_channel_id INTEGER,
                        verification_method TEXT DEFAULT 'both',
                        enabled BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS verification_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        verification_method TEXT NOT NULL,
                        verified_at TEXT NOT NULL,
                        FOREIGN KEY (guild_id) REFERENCES verification_config (guild_id)
                    )
                """)

                await db .commit ()
                pass 
        except Exception as e :
            logger .error (f"Error creating verification tables: {e}")

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        """Auto-delete messages in verification channel from non-bot users"""
        if message .author .bot :
            return 

        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verification_channel_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (message .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if result and result [0 ]==message .channel .id :

                        if not message .author .guild_permissions .manage_messages :
                            try :
                                await message .delete ()

                                embed =discord .Embed (
                                title ="Message Deleted",
                                description ="This channel is for verification only. Please use the buttons above to verify.",
                                color =DISCORD_COLORS ['warning']
                                )
                                try :
                                    await message .author .send (embed =embed )
                                except discord .Forbidden :
                                    pass 
                            except discord .Forbidden :
                                pass 
        except Exception as e :
            logger .error (f"Error in verification message handler: {e}")

    @commands .hybrid_group (name ="verification",invoke_without_command =True ,description ="Advanced verification system management.")
    @commands .has_permissions (administrator =True )
    async def verification (self ,ctx ):
        await ctx .send_help (ctx .command )

    @verification .command (name ="setup",description ="Set up the advanced verification system.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_setup (self ,ctx ):
        try :

            missing_perms =await check_bot_permissions (ctx .guild )

            if missing_perms ['guild']:
                embed =discord .Embed (
                title ="Missing Permissions",
                description =f"Bot is missing required server permissions: {', '.join(missing_perms['guild'])}\n\n"
                "Please grant these permissions and try again.",
                color =DISCORD_COLORS ['error']
                )
                await ctx .send (embed =embed )
                return 

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Advanced Verification System Setup",
            description ="**Welcome to the next-generation verification system!**\n\n"
            "• **Auto-creates verified role** with proper permissions\n"
            "• **DM-based CAPTCHA** system for enhanced security\n"
            "• **Smart channel management** - hides verification after verification\n"
            "• **Auto-permission fixing** for seamless setup\n"
            "• **Auto-message deletion** in verification channel\n"
            "• **Comprehensive logging** and analytics\n\n"
            "**Configure your system using the dropdowns below:**",
            color =DISCORD_COLORS ['primary'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Setup wizard started at {current_time.strftime('%I:%M %p IST')}")

            view =VerificationSetupView (self .bot ,ctx )
            await ctx .send (embed =embed ,view =view )

        except Exception as e :
            logger .error (f"Error in verification setup: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="status",description ="Check verification system status and analytics.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_status (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    """SELECT verification_channel_id, verified_role_id, log_channel_id, 
                                  verification_method, enabled FROM verification_config 
                           WHERE guild_id = ?""",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="Not Configured",
                        description ="Verification system is not set up. Use `/verification setup` to get started!",
                        color =DISCORD_COLORS ['error']
                        )
                        await ctx .send (embed =embed )
                        return 

                    verification_channel =ctx .guild .get_channel (result [0 ])
                    verified_role =ctx .guild .get_role (result [1 ])
                    log_channel =ctx .guild .get_channel (result [2 ])if result [2 ]else None 
                    verification_method =result [3 ]
                    enabled =result [4 ]


                    await cur .execute (
                    "SELECT COUNT(*) FROM verification_logs WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    total_verifications =(await cur .fetchone ())[0 ]

                    await cur .execute (
                    """SELECT verification_method, COUNT(*) FROM verification_logs 
                           WHERE guild_id = ? GROUP BY verification_method""",
                    (ctx .guild .id ,)
                    )
                    method_stats =await cur .fetchall ()


                    yesterday =utc_to_ist (discord .utils .utcnow ())-timedelta (days =1 )
                    await cur .execute (
                    "SELECT COUNT(*) FROM verification_logs WHERE guild_id = ? AND verified_at > ?",
                    (ctx .guild .id ,yesterday .isoformat ())
                    )
                    recent_verifications =(await cur .fetchone ())[0 ]


            issues =[]
            if not verification_channel :
                issues .append ("Verification channel not found")
            if not verified_role :
                issues .append ("Verified role not found")
            elif not validate_role_hierarchy (ctx .guild ,verified_role ):
                issues .append ("Bot cannot manage verified role (role hierarchy)")

            missing_perms =await check_bot_permissions (ctx .guild ,verification_channel )
            if missing_perms ['guild']:
                issues .append (f"Missing server permissions: {', '.join(missing_perms['guild'])}")
            if missing_perms ['channel']:
                issues .append (f"Missing channel permissions: {', '.join(missing_perms['channel'])}")

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Verification System Status",
            color =DISCORD_COLORS ['success']if enabled and not issues else DISCORD_COLORS ['warning']if enabled else DISCORD_COLORS ['error'],
            timestamp =current_time 
            )


            status_text ="Fully Operational"if enabled and not issues else "Operational with Issues"if enabled else "Disabled"

            embed .add_field (
            name ="System Status",
            value =f"**Status:** {status_text}\n"
            f"**Method:** {verification_method.title()}\n"
            f"**Enabled:** {'Yes' if enabled else 'No'}",
            inline =True 
            )

            embed .add_field (
            name ="Configuration",
            value =f"**Channel:** {verification_channel.mention if verification_channel else 'Not found'}\n"
            f"**Role:** {verified_role.mention if verified_role else 'Not found'}\n"
            f"**Log Channel:** {log_channel.mention if log_channel else 'None'}",
            inline =True 
            )

            embed .add_field (
            name ="Analytics",
            value =f"**Total Verifications:** {total_verifications}\n"
            f"**Last 24 Hours:** {recent_verifications}\n"
            f"**Verified Members:** {len([m for m in ctx.guild.members if verified_role in m.roles]) if verified_role else 0}",
            inline =True 
            )

            if method_stats :
                stats_text ="\n".join ([f"**{method.title()}:** {count}"for method ,count in method_stats ])
                embed .add_field (
                name ="Method Breakdown",
                value =stats_text ,
                inline =True 
                )

            if issues :
                embed .add_field (
                name ="Issues Detected",
                value ="\n".join ([f"• {issue}"for issue in issues ]),
                inline =False 
                )

            embed .set_footer (text =f"Status checked at {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error checking verification status: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="fix",description ="Auto-fix channel permissions for verification system.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_fix (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verification_channel_id, verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="Not Configured",
                        description ="Verification system is not set up or disabled.",
                        color =DISCORD_COLORS ['error']
                        )
                        await ctx .send (embed =embed )
                        return 

                    verification_channel =ctx .guild .get_channel (result [0 ])
                    verified_role =ctx .guild .get_role (result [1 ])

                    if not verification_channel or not verified_role :
                        embed =discord .Embed (
                        description ="Verification channel or role not found.",
                        color =DISCORD_COLORS ['error']
                        )
                        await ctx .send (embed =embed )
                        return 


            failed_count =await auto_fix_permissions (ctx .guild ,verification_channel ,verified_role )

            if failed_count ==-1 :
                embed =discord .Embed (
                color =DISCORD_COLORS ['error']
                )
            elif failed_count >0 :
                embed =discord .Embed (
                title ="Permissions Partially Fixed",
                description =f"Permissions have been auto-fixed for most channels.\n"
                f"{failed_count} channels couldn't be fixed due to permission restrictions.",
                color =DISCORD_COLORS ['warning']
                )
            else :
                embed =discord .Embed (
                title ="Permissions Fixed",
                description ="All channel permissions have been auto-fixed successfully!",
                color =DISCORD_COLORS ['success']
                )

            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error fixing verification permissions: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="disable",description ="Disable the verification system and reset all channel permissions.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_disable (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verification_channel_id, verified_role_id FROM verification_config WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await ctx .send ("Verification system is not set up.")
                        return 


                    await cur .execute (
                    "UPDATE verification_config SET enabled = 0 WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    await db .commit ()


            verification_channel =ctx .guild .get_channel (result [0 ])if result [0 ]else None 
            verified_role =ctx .guild .get_role (result [1 ])if result [1 ]else None 
            everyone_role =ctx .guild .default_role 
            count =0 
            failed_count =0 


            for channel in ctx .guild .channels :
                if isinstance (channel ,(discord .TextChannel ,discord .VoiceChannel ,discord .CategoryChannel )):
                    try :

                        overwrites =channel .overwrites .copy ()


                        if everyone_role in overwrites :
                            del overwrites [everyone_role ]
                        if verified_role and verified_role in overwrites :
                            del overwrites [verified_role ]


                        await channel .edit (overwrites =overwrites ,reason ="Verification system disabled - restoring public access")
                        count +=1 
                    except discord .Forbidden :
                        failed_count +=1 
                    except Exception as e :
                        logger .error (f"Error resetting permissions for channel {channel.name}: {e}")
                        failed_count +=1 

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Verification System Disabled",
            description =f"The verification system has been disabled and all channels have been reset to public access.\n\n"
            f"**Channels Reset:** {count}\n"
            f"**Failed to Reset:** {failed_count}"+(f" (due to permission restrictions)"if failed_count >0 else ""),
            color =DISCORD_COLORS ['success']if failed_count ==0 else DISCORD_COLORS ['warning'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Disabled and reset at {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error disabling verification: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="enable",description ="Enable the verification system.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_enable (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await ctx .send ("Verification system is not set up. Use `/verification setup` first.")
                        return 


                    verified_role =ctx .guild .get_role (result [0 ])
                    if not verified_role :
                        await ctx .send ("Verified role no longer exists. Please run setup again.")
                        return 

                    if not validate_role_hierarchy (ctx .guild ,verified_role ):
                        await ctx .send ("Bot cannot manage the verified role due to role hierarchy. Please fix role positions.")
                        return 


                    missing_perms =await check_bot_permissions (ctx .guild )
                    if missing_perms ['guild']:
                        await ctx .send (
                        f"Bot is missing required permissions: "
                        f"{', '.join(missing_perms['guild'])}. Please grant these permissions first."
                        )
                        return 

                    await cur .execute (
                    "UPDATE verification_config SET enabled = 1 WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    await db .commit ()

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Verification System Enabled",
            description ="The verification system has been enabled.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Enabled at {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error enabling verification: {e}")
            pass 

    @verification .command (name ="logs",description ="View recent verification logs.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_logs (self ,ctx ,limit :int =10 ):
        try :
            if limit >50 :
                limit =50 

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    """SELECT user_id, verification_method, verified_at 
                           FROM verification_logs WHERE guild_id = ? 
                           ORDER BY verified_at DESC LIMIT ?""",
                    (ctx .guild .id ,limit )
                    )
                    logs =await cur .fetchall ()

                    if not logs :
                        await ctx .send ("No verification logs found.")
                        return 

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title =f"Recent Verification Logs ({len(logs)})",
            color =DISCORD_COLORS ['primary'],
            timestamp =current_time 
            )

            log_text =""
            for user_id ,method ,verified_at in logs :
                user =ctx .guild .get_member (user_id )
                user_name =user .display_name if user else f"Unknown User ({user_id})"
                log_text +=f"**{user_name}** - {method.upper()} - {verified_at}\n"

            embed .description =log_text 
            embed .set_footer (text =f"Logs retrieved at {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error retrieving verification logs: {e}")
            pass 

    @verification .command (name ="reset",description ="Reset all channel permissions (remove verification restrictions).")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_reset (self ,ctx ):
        try :
            embed =discord .Embed (
            title ="Reset Channel Permissions",
            description ="This will remove all verification-related channel restrictions.\n\n"
            "**Warning:** This action cannot be undone and may take some time.\n"
            "All channels will become visible to @everyone again.",
            color =DISCORD_COLORS ['warning']
            )

            view =discord .ui .View (timeout =60 )

            async def confirm_reset (interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("This action is not for you!",ephemeral =True )
                    return 

                await interaction .response .defer ()


                everyone_role =ctx .guild .default_role 
                count =0 
                failed_count =0 

                for channel in ctx .guild .channels :
                    if isinstance (channel ,(discord .TextChannel ,discord .VoiceChannel ,discord .CategoryChannel )):
                        try :
                            await channel .set_permissions (
                            everyone_role ,
                            overwrite =None ,
                            reason ="Verification system reset"
                            )
                            count +=1 
                        except discord .Forbidden :
                            failed_count +=1 

                current_time =utc_to_ist (discord .utils .utcnow ())
                success_embed =discord .Embed (
                title ="Permissions Reset Complete",
                description =f"Successfully reset permissions for {count} channels.\n"
                f"{f'Failed to reset {failed_count} channels due to permission restrictions.' if failed_count > 0 else ''}\n\n"
                f"The verification system configuration has been preserved.\n"
                f"You can re-enable restrictions using `/verification setup`.",
                color =DISCORD_COLORS ['success'],
                timestamp =current_time 
                )
                success_embed .set_footer (text =f"Reset completed at {current_time.strftime('%I:%M %p IST')}")
                await interaction .edit_original_response (embed =success_embed ,view =None )

            async def cancel_reset (interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("This action is not for you!",ephemeral =True )
                    return 
                await interaction .response .edit_message (content ="Reset cancelled.",embed =None ,view =None )

            confirm_button =discord .ui .Button (label ="Confirm Reset",style =discord .ButtonStyle .red )
            cancel_button =discord .ui .Button (label ="Cancel",style =discord .ButtonStyle .grey )

            confirm_button .callback =confirm_reset 
            cancel_button .callback =cancel_reset 

            view .add_item (confirm_button )
            view .add_item (cancel_button )

            await ctx .send (embed =embed ,view =view )

        except Exception as e :
            logger .error (f"Error in verification reset: {e}")
            pass 

    @verification .command (name ="verify",description ="Manually verify a user (Admin only).")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_verify (self ,ctx ,user :discord .Member ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await ctx .send ("Verification system is not set up or disabled.")
                        return 

                    verified_role =ctx .guild .get_role (result [0 ])
                    if not verified_role :
                        await ctx .send ("Verified role not found.")
                        return 

                    if not validate_role_hierarchy (ctx .guild ,verified_role ):
                        await ctx .send ("Bot cannot manage the verified role due to role hierarchy.")
                        return 

                    if verified_role in user .roles :
                        await ctx .send (f"{user.mention} is already verified.")
                        return 


            if not ctx .guild .me .guild_permissions .manage_roles :
                await ctx .send ("Bot lacks 'Manage Roles' permission.")
                return 


            await user .add_roles (verified_role ,reason =f"Manual verification by {ctx.author}")


            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    current_time =utc_to_ist (discord .utils .utcnow ())
                    await cur .execute (
                    "INSERT INTO verification_logs (guild_id, user_id, verification_method, verified_at) VALUES (?, ?, ?, ?)",
                    (ctx .guild .id ,user .id ,"manual",current_time .isoformat ())
                    )
                    await db .commit ()

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="User Manually Verified",
            description =f"{user.mention} has been manually verified by {ctx.author.mention}.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verified at {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except discord .Forbidden :
            await ctx .send ("Bot lacks permission to assign roles.")
        except Exception as e :
            logger .error (f"Error manually verifying user: {e}")
            pass 

async def setup (bot):
    await bot.add_cog(Verification (bot))
    logger .info ("Advanced verification cog loaded successfully")
