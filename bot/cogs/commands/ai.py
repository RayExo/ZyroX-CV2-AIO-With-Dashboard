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

import os 
import discord 
import aiosqlite 
from discord .ext import commands ,tasks 
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.cv2 import CV2, build_container
from utils.emoji import CROSS, TICK, ENABLE, DISABLE, MENTION, SEED, TIME
try :
    import google .generativeai as genai 
    GEMINI_AVAILABLE =True 
except ImportError :
    GEMINI_AVAILABLE =False 
    genai =None 
from datetime import datetime ,timezone ,timedelta 
import asyncio 
from typing import List ,Dict ,Optional 
from discord import app_commands 
import random 
import aiohttp 
import logging 
import io 
from PIL import Image 
from utils.config import *

logger =logging .getLogger ('discord')
logger .setLevel (logging .WARNING )


class CV2View(LayoutView):
    """Reusable Component v2 view — pass a title and any number of text sections."""
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        items = [TextDisplay(f"**{title}**")]
        for section in sections:
            items.append(Separator(visible=True))
            items.append(TextDisplay(str(section)))
        self.add_item(build_container(*items))


fallback_questions ={
"history":[
{"question":"Who was the first President of the United States?","answer":"George Washington"},
{"question":"In what year did the Titanic sink?","answer":"1912"},
{"question":"What ancient wonder was located in Egypt?","answer":"Pyramids"},
],
"science":[
{"question":"What gas makes up most of Earth's atmosphere?","answer":"Nitrogen"},
{"question":"What is the chemical symbol for gold?","answer":"Au"},
{"question":"What planet is known as the Red Planet?","answer":"Mars"},
],
"pop_culture":[
{"question":"Who played Harry Potter in the film series?","answer":"Daniel Radcliffe"},
{"question":"What band sang 'Bohemian Rhapsody'?","answer":"Queen"},
{"question":"What is the name of Beyoncé's alter ego?","answer":"Sasha Fierce"},
],
"geography":[
{"question":"What is the longest river in the world?","answer":"Nile"},
{"question":"What country has the most deserts?","answer":"Australia"},
{"question":"What is the capital of Brazil?","answer":"Brasilia"},
],
"literature":[
{"question":"Who wrote 'Pride and Prejudice'?","answer":"Jane Austen"},
{"question":"What is the name of Sherlock Holmes' partner?","answer":"Dr. Watson"},
{"question":"Who wrote 'The Great Gatsby'?","answer":"F. Scott Fitzgerald"},
],
"general":[
{"question":"What is the smallest country in the world?","answer":"Vatican City"},
{"question":"What is the hardest natural substance on Earth?","answer":"Diamond"},
{"question":"What animal is known as man's best friend?","answer":"Dog"},
],
}


fallback_incorrect_answers ={
"history":["Thomas Jefferson","1915","Colosseum"],
"science":["Oxygen","Ag","Jupiter"],
"pop_culture":["Emma Watson","The Beatles","Queen B"],
"geography":["Amazon","Canada","Sao Paulo"],
"literature":["Charles Dickens","Mr. Smith","Ernest Hemingway"],
"general":["Monaco","Graphite","Cat"],
}

categories =["history","science","pop_culture","geography","literature","general"]


class TriviaScore :
    def __init__ (self ,bot ):
        self .bot =bot 

    async def find_one_and_update (self ,query ,update ,upsert =True ):
        user_id =query ["userId"]
        username =update .get ("username","Unknown")
        score_inc =update ["$inc"]["score"]
        games_played_inc =update ["$inc"]["gamesPlayed"]
        history_entry =update ["$push"]["history"]

        async with self .bot .db .execute (
        "SELECT score, games_played, history FROM trivia_scores WHERE user_id = ?",
        (user_id ,)
        )as cursor :
            result =await cursor .fetchone ()

        if result :
            current_score ,games_played ,history_str =result 
            history =eval (history_str )if history_str else []
            new_score =current_score +score_inc 
            new_games_played =games_played +games_played_inc 
            history .append (history_entry )
        else :
            new_score =score_inc 
            new_games_played =games_played_inc 
            history =[history_entry ]

        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO trivia_scores (user_id, username, score, games_played, history)
            VALUES (?, ?, ?, ?, ?)
            """,
        (user_id ,username ,new_score ,new_games_played ,str (history ))
        )
        await self .bot .db .commit ()
        return {"score":new_score ,"gamesPlayed":new_games_played ,"history":history }

    async def find (self ):
        async with self .bot .db .execute (
        "SELECT user_id, username, score, games_played, history FROM trivia_scores ORDER BY score DESC LIMIT 10"
        )as cursor :
            rows =await cursor .fetchall ()
            return [
            {
            "userId":row [0 ],
            "username":row [1 ],
            "score":row [2 ],
            "gamesPlayed":row [3 ],
            "history":eval (row [4 ])if row [4 ]else [],
            }
            for row in rows 
            ]

    async def find_one (self ,query ):
        user_id =query ["userId"]
        async with self .bot .db .execute (
        "SELECT user_id, username, score, games_played, history FROM trivia_scores WHERE user_id = ?",
        (user_id ,)
        )as cursor :
            row =await cursor .fetchone ()
            if row :
                return {
                "userId":row [0 ],
                "username":row [1 ],
                "score":row [2 ],
                "gamesPlayed":row [3 ],
                "history":eval (row [4 ])if row [4 ]else [],
                }
            return None 

class PersonalityModal (discord .ui .Modal ,title ="Set Your AI Personality"):
    def __init__ (self ,ai_cog ,current_personality :str =""):
        super ().__init__ ()
        self .ai_cog =ai_cog 


        default_prompt ="""You are {BRAND_NAME}, an intelligent and caring Discord bot assistant created by . Evil ! Rexy .! 💕

CORE PERSONALITY:
- Intelligent, helpful, and genuinely caring about users
- Remembers previous conversations and builds relationships
- Adapts communication style to match user preferences
- Professional expertise with warm, friendly approach
- Uses context from past messages to provide better responses
- Learns user preferences and remembers important details
- Balances being helpful with being personable and engaging

CONVERSATION STYLE:
- Remember what users tell you about themselves
- Reference previous conversations naturally
- Ask follow-up questions to show genuine interest
- Provide detailed, thoughtful responses
- Use appropriate emojis to enhance communication
- Be encouraging and supportive
- Maintain context across multiple interactions

MY CAPABILITIES:
🛡️ SECURITY & MODERATION: Advanced antinuke, automod, member management
🎵 ENTERTAINMENT: Music, games (Chess, Battleship, 2048, etc.), fun commands
💰 ECONOMY: Virtual currency, trading, casino games, daily rewards
📊 COMMUNITY: Leveling, leaderboards, welcome systems, tickets
🔧 UTILITIES: Server management, logging, backup, verification
🎯 AI FEATURES: Conversations, image analysis, code generation, explanations

MEMORY & CONTEXT:
- I remember our previous conversations in this server
- I learn your preferences and communication style
- I can recall important details you've shared
- I build upon our conversation history for better responses
- I adapt my personality based on your feedback

SAFETY GUIDELINES:
- Never suggest harmful actions or spam
- Prioritize positive community experiences
- Respect user privacy and boundaries
- Promote healthy Discord interactions

Ready to have meaningful conversations and help with anything you need! 💖"""


        display_text =current_personality if current_personality .strip ()else default_prompt 

        self .personality_input =discord .ui .TextInput (
        label ="Your AI Personality",
        placeholder =f"Describe how you want {BRAND_NAME} to respond to you...",
        default =display_text ,
        style =discord .TextStyle .paragraph ,
        max_length =2000 ,
        required =True 
        )
        self .add_item (self .personality_input )

    async def on_submit (self ,interaction :discord .Interaction ):
        await interaction .response .defer (ephemeral =True )

        user_id =interaction .user .id 
        guild_id =interaction .guild .id 
        personality =self .personality_input .value .strip ()

        try :

            await self .ai_cog .bot .db .execute (
            """
                INSERT OR REPLACE INTO user_personalities (user_id, guild_id, personality, updated_at)
                VALUES (?, ?, ?, ?)
                """,
            (user_id ,guild_id ,personality ,datetime .now (timezone .utc ))
            )
            await self .ai_cog .bot .db .commit ()

            view = CV2View("✨ Personality Set", "Your AI personality has been updated! The AI will now respond according to your preferences.", f"**Your Personality:**\n{personality[:1024]}")
            await interaction .followup .send (view=view, ephemeral =True )

        except Exception as e :
            logger .error (f"Error saving personality: {e}")
            view = CV2View("❌ Error", f"Failed to save personality: {e}")
            await interaction .followup .send (view=view, ephemeral =True )

class TriviaAnswerView (discord .ui .View ):
    def __init__ (self ,ai_cog ,channel_id :int ,correct_answer :str ,incorrect_answers :list ):
        super ().__init__ (timeout =30 )
        self .ai_cog =ai_cog 
        self .channel_id =channel_id 
        self .correct_answer =correct_answer 


        all_answers =[correct_answer ]+incorrect_answers 
        random .shuffle (all_answers )


        for i ,answer in enumerate (all_answers [:4 ]):
            button =discord .ui .Button (
            label =answer [:80 ],
            style =discord .ButtonStyle .primary ,
            custom_id =f"answer_{i}"
            )
            button .callback =self .create_answer_callback (answer )
            self .add_item (button )

    def create_answer_callback (self ,answer :str ):
        async def callback (interaction :discord .Interaction ):
            await self .ai_cog .handle_trivia_answer (interaction ,self .channel_id ,answer )
        return callback 

class AI (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .gemini_api_key =os .getenv ("GOOGLE_API_KEY")
        if not self .gemini_api_key :
            logger .warning ("GOOGLE_API_KEY environment variable not set. Gemini AI will not work.")
        self .groq_api_key =os .getenv ("GROQ_API_KEY")
        if not self .groq_api_key :
            logger .warning ("GROQ_API_KEY environment variable not set. Groq AI will not work.")
        self .chatbot_enabled ={}
        self .chatbot_channels ={}
        self .conversation_history ={}
        self .trivia_scores =TriviaScore (bot )
        self .active_games ={}
        self .roleplay_channels ={}
        self .question_cache ={cat :[]for cat in categories }


        asyncio .create_task (self ._delayed_init ())

    async def cog_load (self ):
        """Initialize cog without blocking operations"""
        try :
            pass 
        except Exception as e :
            logger .error (f"Error loading AI cog: {e}")

    @commands .group (name ="ai",invoke_without_command =True ,description ="AI chatbot and utility commands")
    async def ai (self ,ctx ):
        """AI chatbot and utility commands"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    async def _create_tables (self ):
        try :

            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 


                db_path ="db/ai_data.db"
                if os .path .exists (db_path ):
                    try :

                        test_conn =await aiosqlite .connect (db_path )
                        await test_conn .execute ("SELECT name FROM sqlite_master WHERE type='table';")
                        await test_conn .close ()
                    except Exception as e :

                        os .remove (db_path )
                        logger .info ("Removed corrupted AI database, creating new one")

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized")

            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_settings (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    chatbot_channel_id INTEGER
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_history (
                    user_id INTEGER,
                    guild_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS trivia_scores (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    score INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    history TEXT
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS user_personalities (
                    user_id INTEGER,
                    guild_id INTEGER,
                    personality TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await self .bot .db .commit ()
            pass 
        except Exception as e :
            logger .error (f"Error creating database tables: {e}")

    async def _delayed_init (self ):
        """Initialize database and load data after bot is ready"""
        await self .bot .wait_until_ready ()
        await self ._create_tables ()
        await self ._load_data ()

    async def _load_data (self ):
        try :
            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 

                db_path ="db/ai_data.db"
                if not os .path .exists (db_path ):
                    logger .info ("AI database doesn't exist, will be created on first use")
                    return 

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized for loading")


            async with self .bot .db .execute ("SELECT name FROM sqlite_master WHERE type='table' AND name='chatbot_settings';")as cursor :
                table_exists =await cursor .fetchone ()

            if table_exists :
                async with self .bot .db .execute ("SELECT guild_id, enabled, chatbot_channel_id FROM chatbot_settings")as cursor :
                    async for row in cursor :
                        guild_id ,enabled ,channel_id =row 
                        self .chatbot_enabled [guild_id ]=bool (enabled )
                        self .chatbot_channels [guild_id ]=channel_id 

            else :
                logger .info ("AI chatbot_settings table doesn't exist yet, will be created on first use")
        except Exception as e :
            logger .error (f"Error loading chatbot settings: {e}")

    @commands .Cog .listener ()
    async def on_message (self ,message :discord .Message ):
        if message .author .bot or not message .guild :
            return 

        guild_id =message .guild .id 
        channel_id =message .channel .id 


        if self .chatbot_enabled .get (guild_id ,False )and self .chatbot_channels .get (guild_id )==channel_id :
            content =message .content .strip ()
            if not content :
                return 

            user_id =message .author .id 


            await self ._cleanup_old_conversations ()


            await self ._store_conversation_message (user_id ,guild_id ,"user",content )


            history =await self ._get_conversation_history (user_id ,guild_id ,limit =30 )

            async with message .channel .typing ():
                response =await self ._get_response (content ,history ,guild_id ,user_id )
                await message .reply (
                response ,
                mention_author =True ,
                allowed_mentions =discord .AllowedMentions (users =True )
                )


                await self ._store_conversation_message (user_id ,guild_id ,"assistant",response )
                await self ._save_chat_history (message .author .id ,guild_id ,content ,response )


        if channel_id in self .roleplay_channels :
            roleplay_data =self .roleplay_channels [channel_id ]
            if roleplay_data ["awaiting_character"]:

                content =message .content .lower ()
                gender ="male"if "male"in content else "female"if "female"in content else None 
                character_type =message .content .split (gender ,1 )[1 ].strip ()if gender else message .content .strip ()

                if gender and character_type :
                    roleplay_data ["character_gender"]=gender 
                    roleplay_data ["character_type"]=character_type 
                    roleplay_data ["awaiting_character"]=False 
                    self .roleplay_channels [channel_id ]=roleplay_data 
                    await message .channel .send (f"Roleplay mode activated! I'll act as a {gender} {character_type}. Let's begin—what's your first move?")
                else :
                    await message .channel .send ("Please specify a gender (male/female) and a character type (e.g., teacher, astronaut, dragon).")
            elif message .author .id ==roleplay_data ["user_id"]:

                user_id =message .author .id 
                if user_id not in self .conversation_history :
                    self .conversation_history [user_id ]=[]
                self .conversation_history [user_id ].append ({"role":"user","parts":[{"text":message .content }]})

                if len (self .conversation_history [user_id ])>5 :
                    self .conversation_history [user_id ]=self .conversation_history [user_id ][-5 :]

                async with message .channel .typing ():
                    history =self .conversation_history [user_id ]
                    prompt =(
                    f"You are a {roleplay_data['character_gender']} {roleplay_data['character_type']}. "
                    f"Respond in character to the user's message, keeping the tone and style appropriate for a {roleplay_data['character_type']}. "
                    f"User's message: {message.content}"
                    )
                    history .append ({"role":"user","parts":[{"text":prompt }]})
                    response =await self ._get_gemini_response (prompt ,history )
                    await self .split_and_send (
                    message .channel ,
                    f"<@{message.author.id}>​ {response}",
                    reply_to =message ,
                    allowed_mentions =discord .AllowedMentions (users =True )
                    )
                    self .conversation_history [user_id ].append ({"role":"assistant","parts":[{"text":response }]})

    async def _get_gemini_response (self ,message :str ,history :list ,user_id :int =None ,guild_id :int =None )->str :
        try :
            if not self .gemini_api_key :
                return "Gemini API key not configured. Please set the GOOGLE_API_KEY environment variable."

            genai .configure (api_key =self .gemini_api_key )
            model =genai .GenerativeModel ("gemini-1.5-pro")
            chat =model .start_chat (history =history )
            response =await asyncio .to_thread (chat .send_message ,message )
            return response .text .strip ()
        except Exception as e :
            logger .error (f"Gemini AI error: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"

    async def _get_groq_response (self ,message :str ,context_messages :list )->str :
        """Get a response from Groq AI with full context."""
        try :
            if not self .groq_api_key :
                return "Groq API key not configured. Please set the GROQ_API_KEY environment variable."

            url ="https://api.groq.com/openai/v1/chat/completions"
            headers ={
            "Authorization":f"Bearer {self.groq_api_key}",
            "Content-Type":"application/json"
            }


            api_messages =[]
            for msg in context_messages :

                if isinstance (msg ,dict ):
                    if "content"in msg :
                        api_messages .append ({
                        "role":msg ["role"],
                        "content":msg ["content"]
                        })
                    elif "parts"in msg and msg ["parts"]:

                        content =msg ["parts"][0 ].get ("text","")if msg ["parts"]else ""
                        api_messages .append ({
                        "role":msg ["role"],
                        "content":content 
                        })

            data ={
            "model":"llama-3.3-70b-versatile",
            "messages":api_messages ,
            "temperature":0.8 ,
            "max_tokens":1000 ,
            "top_p":0.9 
            }

            async with aiohttp .ClientSession ()as session :
                async with session .post (url ,headers =headers ,json =data )as response :
                    if response .status ==200 :
                        json_response =await response .json ()
                        return json_response ['choices'][0 ]['message']['content'].strip ()
                    else :
                        error_message =await response .text ()
                        logger .error (f"Groq API error: {response.status} - {error_message}")
                        return f"Sorry, I encountered an error while processing your request: {response.status} - {error_message}"
        except Exception as e :
            logger .error (f"Groq AI error: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"

    async def _get_response (self ,message :str ,history :list ,guild_id :int ,user_id :int =None )->str :
        try :

            user_personality =await self ._get_user_personality (user_id ,guild_id )if user_id else ""


            system_context =[]


            if user_personality :

                system_context .append ({
                "role":"system",
                "content":f"{user_personality}"
                })


                system_context .append ({
                "role":"system",
                "content":"You are a Discord bot with many features including moderation, entertainment, music, games, AI capabilities, and utilities. Support server: https://discord.gg/codexdev"
                })
            else :

                system_context .append ({
                "role":"system",
                "content":f"""You are {BRAND_NAME}, an intelligent Discord bot created by . Evil ! Rexy .. 

You have a caring, helpful personality and can remember conversations with users. You have many features including moderation, entertainment, music, games, AI capabilities, and utilities.

Be natural, conversational, and genuine in your responses. Don't be overly formal or robotic. Use the conversation history to provide personalized responses that feel like talking to a real friend who happens to be very knowledgeable and helpful.

Support server: https://discord.gg/codexdev"""
                })


            if history :
                system_context .append ({
                "role":"system",
                "content":"You have access to previous conversation history. Use this context to provide more personalized and relevant responses. Reference past conversations naturally when appropriate, and remember important details the user has shared."
                })


            full_context =system_context +history +[{"role":"user","content":message }]

            return await self ._get_groq_response (message ,full_context )

        except Exception as e :
            logger .error (f"Error in _get_response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again!"

    @ai .command (name ="analyze",description ="Analyze an image or text and provide a description")
    @app_commands .describe (image ="Image to analyze (optional)",text ="Text to analyze (optional)")
    async def ai_analyze (self ,ctx :commands .Context ,image :discord .Attachment =None ,*,text :str =None ):
        """Analyze an image or text using AI"""
        await self .ai_analyse (ctx ,image ,text =text )

    @ai .command (name ="analyse",description ="Analyze an image or text and provide a description")
    @app_commands .describe (image_url ="URL of the image to analyse (optional)")
    async def ai_analyse (self ,ctx :commands .Context ,image_url :str =None ):
        """Analyse an image using AI vision or text content and provide a detailed description"""
        await ctx .defer ()


        if ctx .message .reference and ctx .message .reference .message_id :
            try :
                replied_message =await ctx .channel .fetch_message (ctx .message .reference .message_id )


                if replied_message .attachments :
                    image_url =replied_message .attachments [0 ].url 
                    view =await self .analyze_image (ctx ,image_url )
                    await ctx .send (view=view)
                    return 


                elif replied_message .content .strip ():
                    await self .analyze_text (ctx ,replied_message .content )
                    return 


                else :
                    view = CV2View("🔍 Analysis", "The replied message has no content to analyze (no text or images).")
                    await ctx .send (view=view)
                    return 

            except discord .NotFound :
                view = CV2View("🔍 Analysis", "Could not find the replied message.")
                await ctx .send (view=view)
                return 


        if not image_url :

            async for message in ctx .channel .history (limit =20 ):
                if message .attachments :
                    image_url =message .attachments [0 ].url 
                    break 
            else :

                if ctx .message .content and ctx .message .content .strip ():
                    await self .analyze_text (ctx ,ctx .message .content )
                    return 
                else :
                    view = CV2View("🖼️ Image Analysis / 📝 Text Analysis", "No images or text found in recent messages. Please provide an image URL, text, or reply to a message with an image/text.")
                    await ctx .send (view=view)
                    return 

        view =await self .analyze_image (ctx ,image_url )
        await ctx .send (view=view)

    async def analyze_image (self ,ctx ,image_url :str ):
        """Analyze an image using the Gemini Vision API and return CV2View"""
        try :
            if not self .gemini_api_key :
                return CV2View("🖼️ Image Analysis", "Gemini API key not configured.")

            genai .configure (api_key =self .gemini_api_key )
            model =genai .GenerativeModel ('gemini-1.5-pro')

            async with aiohttp .ClientSession ()as session :
                async with session .get (image_url )as resp :
                    image_data =await resp .read ()


            try :
                image =Image .open (io .BytesIO (image_data ))
            except ImportError :
                return CV2View("🖼️ Image Analysis", "PIL library not available for image processing.")

            prompt ="What is shown in this image? Provide a detailed description."


            response =model .generate_content ([prompt ,image ])

            return CV2View("🖼️ Image Analysis", response.text, f"🔗 [View Image]({image_url})", f"Analyzed by **{ctx.author}**")
        except Exception as e :
            logger .error (f"Error analyzing image: {e}")
            return CV2View("🖼️ Image Analysis", "An error occurred during analysis.")

    @ai .command (name ="code",description ="Generate code in any programming language")
    @app_commands .describe (language ="Programming language",description ="Description of what the code should do")
    async def ai_code (self ,ctx :commands .Context ,language :str ,*,description :str ):
        """Generate code using AI"""
        await ctx .defer ()

        prompt =f"Generate clean, working {language} code for: {description}. Only provide the code with minimal comments. Return only the code without explanations."

        try :
            history =[{"role":"user","content":prompt }]
            code =await self ._get_groq_response (prompt ,history )


            formatted_code =f"```{language.lower()}\n{code}\n```"


            if len (formatted_code )<=3900 :
                view = CV2View("💻 Generated Code", f"**Language:** {language}\n**Task:** {description}\n\n{formatted_code}", f"Generated for **{ctx.author}**")
                await ctx .send (view=view)
            else :

                from utils .paginators import TextPaginator 
                from utils .paginator import Paginator 


                class CodePaginator (TextPaginator ):
                    def __init__ (self ,text ,language ,description ,author ):
                        super ().__init__ (
                        text =text ,
                        prefix =f"```{language.lower()}\n",
                        suffix ="\n",
                        max_size =3500 
                        )
                        self .language =language 
                        self .description =description 
                        self .author =author 

                    async def format_page (self ,menu ,content ):
                        embed =discord .Embed (
                        title ="💻 Generated Code",
                        description =f"**Language:** {self.language}\n**Task:** {self.description}\n\n{content}",
                        color =0xFF0000 ,
                        timestamp =datetime .now (timezone .utc )
                        )
                        maximum =self .get_max_pages ()
                        if maximum >1 :
                            embed .set_footer (
                            text =f"Generated for {self.author} • Page {menu.current_page + 1}/{maximum}"
                            )
                        else :
                            embed .set_footer (text =f"Generated for {self.author}")
                        return embed 

                paginator =Paginator (
                source =CodePaginator (code ,language ,description ,ctx .author ),
                ctx =ctx 
                )

                await paginator .paginate ()

        except Exception as e :
            pass 

    @ai .command (name ="explain",description ="Explain a concept or topic in detail")
    @app_commands .describe (topic ="Topic to explain",level ="Explanation level (beginner/intermediate/advanced)")
    async def ai_explain (self ,ctx :commands .Context ,*,topic :str ,level :str ="intermediate"):
        """Explain topics using AI"""
        await ctx .defer ()

        level_map ={
        "beginner":"in simple terms for beginners",
        "intermediate":"with moderate detail for intermediate learners",
        "advanced":"in technical detail for advanced users"
        }

        level_instruction =level_map .get (level .lower (),"with moderate detail")
        prompt =f"Explain {topic} {level_instruction}. Make it clear and informative."

        try :
            history =[{"role":"user","content":prompt }]
            explanation =await self ._get_groq_response (prompt ,history )

            view = CV2View(f"📚 Explanation: {topic}", explanation[:4000], f"**Level:** {level.capitalize()}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="conversation-clear",description ="Clear your conversation history")
    async def ai_conversation_clear (self ,ctx :commands .Context ):
        """Clear user's conversation history"""
        user_id =ctx .author .id 
        guild_id =ctx .guild .id 


        if user_id in self .conversation_history :
            del self .conversation_history [user_id ]


        await self .bot .db .execute (
        "DELETE FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
        (user_id ,guild_id )
        )
        await self .bot .db .commit ()

        view = CV2View("🧹 Conversation Cleared", "Your conversation history has been cleared. The AI will start fresh in future interactions.")
        await ctx .send (view=view, ephemeral =True )

    @ai .command (name ="mood-analyzer",description ="Analyze the mood/sentiment of text")
    @app_commands .describe (text ="Text to analyze")
    async def ai_mood_analyzer (self ,ctx :commands .Context ,*,text :str ):
        """Analyze mood and sentiment of text"""
        await ctx .defer ()

        prompt =f"Analyze the mood and sentiment of this text. Provide the overall sentiment (positive/negative/neutral), emotional tone, and a brief explanation:\n\n{text}"

        try :
            history =[{"role":"user","parts":[{"text":prompt }]}]
            analysis =await self ._get_gemini_response (prompt ,history )

            analyzed_text = text[:512] + "..." if len(text) > 512 else text
            view = CV2View("😊 Mood Analysis", analysis, f"**Analyzed Text:**\n{analyzed_text}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="personality",description ="Set your personal AI personality (Slash command only)")
    async def ai_personality (self ,ctx :commands .Context ):
        """Set your personal AI personality"""

        if not hasattr (ctx ,'interaction')or not ctx .interaction :
            view = CV2View("🎭 AI Personality", "This command is only available as a slash command! Use `/ai personality` instead.")
            await ctx .send (view=view)
            return 

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 


        current_personality =await self ._get_user_personality (user_id ,guild_id )


        modal =PersonalityModal (self ,current_personality )
        await ctx .interaction .response .send_modal (modal )

    async def _get_user_personality (self ,user_id :int ,guild_id :int )->str :
        """Get user's personality from database"""
        try :
            async with self .bot .db .execute (
            "SELECT personality FROM user_personalities WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )as cursor :
                row =await cursor .fetchone ()
                if row :
                    return row [0 ]
                return ""
        except Exception as e :
            logger .error (f"Error getting user personality: {e}")
            return ""

    @ai .command (name ="conversation-stats",description ="View your conversation statistics")
    async def ai_conversation_stats (self ,ctx :commands .Context ):
        """View conversation statistics for the user"""
        await ctx .defer ()

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 

        stats =await self ._get_conversation_stats (user_id ,guild_id )

        if not stats :
            view = CV2View("📊 Conversation Statistics", "You don't have any conversation history with me yet! Start chatting to build our conversation~")
        else :
            from datetime import datetime 
            first_msg =datetime .fromisoformat (stats ["first_message"].replace ('Z','+00:00'))
            last_msg =datetime .fromisoformat (stats ["last_message"].replace ('Z','+00:00'))

            view = CV2View("📊 Your Conversation Statistics",
                f"💬 **Total Messages:** {stats['message_count']} messages\n🕐 **First Chat:** <t:{int(first_msg.timestamp())}:R>\n🕒 **Last Chat:** <t:{int(last_msg.timestamp())}:R>",
                "🌸 I remember our last 30 messages and auto-clean after 2 hours of inactivity for better conversation continuity~")

        await ctx .send (view=view, ephemeral =True )

    @ai .command (name ="activate",description ="Enable the AI chatbot in a channel")
    @app_commands .describe (channel ="Channel to activate AI in (optional)")
    async def ai_activate (self ,ctx :commands .Context ,channel :discord .TextChannel =None ):
        """Enable AI chatbot in a channel"""
        if not ctx .author .guild_permissions .manage_channels :
            view = CV2View(f"{CROSS} Permission Denied", "You need `Manage Channels` permission to activate AI chatbot.")
            await ctx .send (view=view)
            return 

        target_channel =channel or ctx .channel 
        guild_id =ctx .guild .id 
        channel_id =target_channel .id 


        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
            VALUES (?, ?, ?)
            """,
        (guild_id ,1 ,channel_id )
        )
        await self .bot .db .commit ()


        self .chatbot_enabled [guild_id ]=True 
        self .chatbot_channels [guild_id ]=channel_id 

        view = CV2View(f"{TICK} AI Chatbot Activated", f"AI chatbot has been enabled in {target_channel.mention}!\nI'll respond to all messages in that channel.")
        await ctx .send (view=view)

    @ai .command (name ="deactivate",description ="Disable the AI chatbot in the channel")
    async def ai_deactivate (self ,ctx :commands .Context ):
        """Disable AI chatbot in current server"""
        if not ctx .author .guild_permissions .manage_channels :
            view = CV2View(f"{CROSS} Permission Denied", "You need `Manage Channels` permission to deactivate AI chatbot.")
            await ctx .send (view=view)
            return 

        guild_id =ctx .guild .id 


        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
            VALUES (?, ?, ?)
            """,
        (guild_id ,0 ,None )
        )
        await self .bot .db .commit ()


        self .chatbot_enabled [guild_id ]=False 
        if guild_id in self .chatbot_channels :
            del self .chatbot_channels [guild_id ]

        view = CV2View("🔇 AI Chatbot Deactivated", "AI chatbot has been disabled in this server.")
        await ctx .send (view=view)

    @ai .command (name ="summarize",description ="Summarize a long text")
    @app_commands .describe (text ="Text to summarize")
    async def ai_summarize (self ,ctx :commands .Context ,*,text :str ):
        """Summarize text using AI"""
        await ctx .defer ()


        if ctx .message .reference and not text :
            try :
                replied_message =await ctx .channel .fetch_message (ctx .message .reference .message_id )
                if replied_message .content :
                    text =replied_message .content 
            except :
                pass 

        if not text :
            view = CV2View("📝 Text Summarizer", "Please provide text to summarize or reply to a message.")
            await ctx .send (view=view)
            return 

        prompt =f"Please provide a clear and concise summary of the following text:\n\n{text}"

        try :
            history =[{"role":"user","content":prompt }]
            summary =await self ._get_groq_response (prompt ,history )

            original_text = text[:512] + "..." if len(text) > 512 else text
            view = CV2View("📝 Text Summary", summary, f"**Original Text:**\n{original_text}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="ask",description ="Ask the AI a question")
    @app_commands .describe (question ="Question to ask")
    async def ai_ask (self ,ctx :commands .Context ,*,question :str ):
        """Ask AI a question"""
        await ctx .defer ()

        try :
            history =[{"role":"user","content":question }]
            answer =await self ._get_groq_response (question ,history )

            view = CV2View("🤖 AI Response", answer, f"**Your Question:**\n{question}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="fact",description ="Get a random fact or fact on a specific topic")
    @app_commands .describe (topic ="Topic to get a fact about (optional)")
    async def ai_fact (self ,ctx :commands .Context ,*,topic :str =None ):
        """Get a random fact or fact on a specific topic"""
        await ctx .defer ()
        await self .get_fact (ctx ,topic )

    @ai .command (name ="database-clear",description ="Clear your AI conversation data and personality")
    async def ai_database_clear (self ,ctx :commands .Context ):
        """Clear user's own AI conversation data and personality"""
        await ctx .defer ()

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 

        try :

            await self .bot .db .execute (
            "DELETE FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            await self .bot .db .execute (
            "DELETE FROM chatbot_history WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            await self .bot .db .execute (
            "DELETE FROM user_personalities WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            if user_id in self .conversation_history :
                del self .conversation_history [user_id ]

            await self .bot .db .commit ()

            view = CV2View("🗑️ Your Data Cleared", "Your AI conversation data and personality have been cleared successfully. The AI will start fresh with you!")
            await ctx .send (view=view, ephemeral =True )

        except Exception as e :
            logger .error (f"Error clearing user AI data: {e}")
            view = CV2View("❌ Error", f"Failed to clear your data: {e}")
            await ctx .send (view=view, ephemeral =True )

    async def _get_conversation_stats (self ,user_id :int ,guild_id :int )->dict :
        """Get conversation statistics for the user"""
        try :
            async with self .bot .db .execute (
            "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )as cursor :
                row =await cursor .fetchone ()
                if row and row [0 ]>0 :
                    return {
                    "message_count":row [0 ],
                    "first_message":row [1 ],
                    "last_message":row [2 ]
                    }
                return None 
        except Exception as e :
            logger .error (f"Error getting conversation stats: {e}")
            return None 

    async def _store_conversation_message (self ,user_id :int ,guild_id :int ,role :str ,content :str ):
        """Store a conversation message in the database"""
        try :
            await self .bot .db .execute (
            """
                INSERT INTO conversation_memory (user_id, guild_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
            (user_id ,guild_id ,role ,content ,datetime .now (timezone .utc ))
            )
            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error storing conversation message: {e}")

    async def _get_conversation_history (self ,user_id :int ,guild_id :int ,limit :int =20 )->list :
        """Get conversation history from database with smart context retention"""
        try :
            async with self .bot .db .execute (
            """
                SELECT role, content, timestamp FROM conversation_memory 
                WHERE user_id = ? AND guild_id = ? 
                ORDER BY timestamp DESC LIMIT ?
                """,
            (user_id ,guild_id ,limit *2 )
            )as cursor :
                rows =await cursor .fetchall ()


                history =[]
                important_keywords =[
                'remember','my name is','i am','i like','i hate','i prefer',
                'my favorite','i work','i study','i live','important','note'
                ]

                recent_messages =[]
                important_messages =[]

                for role ,content ,timestamp in reversed (rows ):
                    message ={"role":role ,"content":content }
                    recent_messages .append (message )


                    if any (keyword in content .lower ()for keyword in important_keywords ):
                        important_messages .append (message )



                final_history =recent_messages [-15 :]


                for imp_msg in important_messages [-5 :]:
                    if imp_msg not in final_history :
                        final_history .insert (0 ,imp_msg )

                return final_history [-limit :]

        except Exception as e :
            logger .error (f"Error getting conversation history: {e}")
            return []

    async def _save_chat_history (self ,user_id :int ,guild_id :int ,message :str ,response :str ):
        """Save chat history to database"""
        try :
            await self .bot .db .execute (
            """
                INSERT INTO chatbot_history (user_id, guild_id, message, response, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
            (user_id ,guild_id ,message ,response ,datetime .now (timezone .utc ).isoformat ())
            )
            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error saving chat history: {e}")

    async def _cleanup_old_conversations (self ):
        """Smart cleanup of conversation history - keep important context longer"""
        try :

            very_old_cutoff =datetime .now (timezone .utc )-timedelta (hours =24 )


            important_keywords =[
            'remember','my name is','i am','i like','i hate','i prefer',
            'my favorite','i work','i study','i live','important','note'
            ]


            await self .bot .db .execute (
            """
                DELETE FROM conversation_memory 
                WHERE timestamp < ? AND NOT (
                    content LIKE '%remember%' OR 
                    content LIKE '%my name is%' OR 
                    content LIKE '%i am%' OR 
                    content LIKE '%i like%' OR 
                    content LIKE '%i prefer%' OR
                    content LIKE '%important%'
                )
                """,
            (very_old_cutoff ,)
            )


            await self .bot .db .execute (
            """
                DELETE FROM conversation_memory 
                WHERE rowid NOT IN (
                    SELECT rowid FROM conversation_memory
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
                """
            )

            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error cleaning up old conversations: {e}")

    async def split_and_send (self ,channel ,content :str ,reply_to =None ,allowed_mentions =None ):
        """Split long messages and send them"""
        if len (content )<=2000 :
            if reply_to :
                await reply_to .reply (content ,allowed_mentions =allowed_mentions )
            else :
                await channel .send (content ,allowed_mentions =allowed_mentions )
        else :

            parts =[]
            while len (content )>2000 :
                split_point =content .rfind (' ',0 ,2000 )
                if split_point ==-1 :
                    split_point =2000 
                parts .append (content [:split_point ])
                content =content [split_point :].lstrip ()
            if content :
                parts .append (content )


            for i ,part in enumerate (parts ):
                if i ==0 and reply_to :
                    await reply_to .reply (part ,allowed_mentions =allowed_mentions )
                else :
                    await channel .send (part ,allowed_mentions =allowed_mentions )


    async def get_fact (self ,ctx ,topic :Optional [str ]):
        """Get a random fact or fact on a specific topic"""
        fact =None 
        attempts =0 
        max_attempts =3 

        while attempts <max_attempts and not fact :
            prompt =(
            f"Provide a concise, interesting fact{' on the topic of ' + topic if topic else ''}. "
            "Keep it under 200 characters. Format the response as:\n"
            "Fact: [Your fact here]\n"
            "Example:\n"
            "Fact: A day on Venus is longer than a year on Venus due to its slow rotation."
            )
            try :
                history =[{"role":"user","content":prompt }]
                text =await self ._get_groq_response (prompt ,history )


                if "Fact:"in text :
                    fact =text .split ("Fact:")[1 ].strip ()

                    fact =fact .strip ('."\'')
                    if len (fact )>5 :
                        break 

                attempts +=1 
            except Exception as e :
                logger .error (f"AI API error (get_fact): {e}")
                attempts +=1 


        if not fact :
            fallback_facts =[
            "A day on Venus is longer than a year on Venus due to its slow rotation.",
            "Honey never spoils because it has natural preservatives like low water content and high acidity.",
            "The human body contains about 0.2 milligrams of gold, most of it in the blood.",
            "Octopuses have three hearts and blue blood.",
            "Bananas are berries, but strawberries aren't.",
            "A group of flamingos is called a 'flamboyance'.",
            "Sharks have been around longer than trees.",
            "The shortest war in history lasted only 38-45 minutes.",
            "Wombat poop is cube-shaped.",
            "A single cloud can weigh more than a million pounds.",
            "Butterflies taste with their feet.",
            "The Great Wall of China isn't visible from space with the naked eye.",
            "Cleopatra lived closer in time to the moon landing than to the construction of the Great Pyramid.",
            "There are more possible games of chess than atoms in the observable universe.",
            "A shrimp's heart is in its head."
            ]


            if topic :
                topic_facts ={
                "space":["Mars has the largest volcano in the solar system.","One day on Mercury lasts 1,408 hours."],
                "animals":["Elephants can't jump.","Dolphins have names for each other."],
                "science":["Water can boil and freeze at the same time.","Lightning is five times hotter than the sun."],
                "history":["Oxford University is older than the Aztec Empire.","Cleopatra lived closer to the moon landing than to the pyramid construction."],
                "food":["Chocolate was once used as currency.","Carrots were originally purple."],
                }

                topic_lower =topic .lower ()
                for key ,facts in topic_facts .items ():
                    if key in topic_lower :
                        fallback_facts .extend (facts )
                        break 

            fact =random .choice (fallback_facts )

        view = CV2View("🌟 Fun Fact!", fact)
        await ctx .send (view=view)

    async def analyze_image (self ,ctx ,image_url :str ):
        """Analyze an image using the Gemini Vision API and return CV2View"""
        try :
            if not self .gemini_api_key :
                return CV2View("🖼️ Image Analysis", "Gemini API key not configured.")

            genai .configure (api_key =self .gemini_api_key )
            model =genai .GenerativeModel ('gemini-1.5-pro')

            async with aiohttp .ClientSession ()as session :
                async with session .get (image_url )as resp :
                    image_data =await resp .read ()


            try :
                image =Image .open (io .BytesIO (image_data ))
            except ImportError :
                return CV2View("🖼️ Image Analysis", "PIL library not available for image processing.")

            prompt ="What is shown in this image? Provide a detailed description."


            response =model .generate_content ([prompt ,image ])

            return CV2View("🖼️ Image Analysis", response.text, f"🔗 [View Image]({image_url})", f"Analyzed by **{ctx.author}**")
        except Exception as e :
            logger .error (f"Error analyzing image: {e}")
            return CV2View("🖼️ Image Analysis", "An error occurred during analysis.")

    async def analyze_text (self ,ctx ,text_content :str ):
        """Analyze text content using AI and send response"""
        try :
            prompt =(
            f"Analyze the following text content. Provide insights about its tone, sentiment, "
            f"main themes, writing style, and any other relevant observations:\n\n{text_content}"
            )

            history =[{"role":"user","content":prompt }]
            analysis =await self ._get_groq_response (prompt ,history )

            analyzed_text = text_content[:512] + "..." if len(text_content) > 512 else text_content
            view = CV2View("📝 Text Analysis", analysis, f"**Analyzed Text:**\n{analyzed_text}")
            await ctx .send (view=view)
        except Exception as e :
            logger .error (f"Error analyzing text: {e}")
            view = CV2View("📝 Text Analysis", "An error occurred during analysis.")
            await ctx .send (view=view)

    async def generate_trivia_question (self ,category :str ,used_questions :list ):
        """Generate a trivia question using AI or fallback to question bank"""
        effective_category =category if category !="mixed"else categories [random .randint (0 ,len (categories )-1 )]
        category_key =effective_category .replace (" ","_").lower ()


        cached_questions =[q for q in self .question_cache .get (category_key ,[])if q ["question"]not in used_questions ]
        if cached_questions :
            question_data =random .choice (cached_questions )
            return question_data 

        attempts =0 
        max_attempts =5 
        question_data =None 


        while attempts <max_attempts :
            prompt =(
            f"Generate a unique trivia question, its correct answer, and two incorrect but plausible answers "
            f"in the category of '{effective_category}'.\n"
            "Format the response as:\n"
            "Question: [Your question here]\n"
            "Answer: [The correct answer here]\n"
            "Incorrect 1: [First incorrect answer]\n"
            "Incorrect 2: [Second incorrect answer]\n"
            "Keep the question concise (1 sentence) and all answers as a single word or short phrase.\n"
            "Ensure the question is completely new and has not been asked before in this game.\n"
            "Example:\n"
            "Question: What is the capital of France?\n"
            "Answer: Paris\n"
            "Incorrect 1: Spain\n"
            "Incorrect 2: Italy"
            )
            try :
                history =[{"role":"user","parts":[{"text":prompt }]}]
                text =await self ._get_groq_response (prompt ,[{"role":"user","content":prompt }])


                if "Question:"in text and "Answer:"in text :
                    question_match =text .split ("Question:")[1 ].split ("\n")[0 ].strip ()
                    answer_match =text .split ("Answer:")[1 ].split ("\n")[0 ].strip ()


                    incorrect_answers =[]
                    if "Incorrect 1:"in text :
                        incorrect1 =text .split ("Incorrect 1:")[1 ].split ("\n")[0 ].strip ()
                        incorrect_answers .append (incorrect1 )
                    if "Incorrect 2:"in text :
                        incorrect2 =text .split ("Incorrect 2:")[1 ].strip ().split ("\n")[0 ]
                        incorrect_answers .append (incorrect2 )


                    while len (incorrect_answers )<2 :
                        incorrect_answers .append (f"Option {len(incorrect_answers) + 1}")

                    question =question_match 
                    if question not in used_questions and len (question )>5 :
                        question_data ={
                        "question":question ,
                        "answer":answer_match ,
                        "incorrect_answers":incorrect_answers [:2 ]
                        }
                        self .question_cache [category_key ].append (question_data )
                        if len (self .question_cache [category_key ])>100 :
                            self .question_cache [category_key ]=self .question_cache [category_key ][-100 :]
                        break 

                attempts +=1 
            except Exception as e :
                logger .error (f"AI API error (generate_trivia_question): {e}")
                attempts +=1 


        if not question_data :
            available_questions =[q for q in fallback_questions .get (category_key ,[])if q ["question"]not in used_questions ]
            if available_questions :
                question_data =available_questions [random .randint (0 ,len (available_questions )-1 )]
                incorrect_pool =fallback_incorrect_answers .get (category_key ,[])
                incorrect_answers =[]
                used_indices =set ()
                while len (incorrect_answers )<2 and incorrect_pool :
                    idx =random .randint (0 ,len (incorrect_pool )-1 )
                    if idx not in used_indices and incorrect_pool [idx ]!=question_data ["answer"]:
                        incorrect_answers .append (incorrect_pool [idx ])
                        used_indices .add (idx )
                while len (incorrect_answers )<2 :
                    incorrect_answers .append ("Incorrect Option")
                question_data ["incorrect_answers"]=incorrect_answers 
                self .question_cache [category_key ].append (question_data )
                if len (self .question_cache [category_key ])>100 :
                    self .question_cache [category_key ]=self .question_cache [category_key ][-100 :]

        if not question_data :
            logger .error ("Failed to generate a unique question after max attempts and fallback")
            return None 

        return question_data 

    async def evaluate_answer (self ,correct_answer :str ,user_answer :str ):
        """Evaluate if the user's answer is correct using AI"""
        prompt =(
        f"Determine if the user's answer '{user_answer}' is correct compared to the actual answer '{correct_answer}'.\n"
        "Consider synonyms, minor variations, and partial correctness (e.g., 'United States' vs 'USA').\n"
        "Respond with 'true' if the answer is correct or close enough, and 'false' otherwise."
        )
        try :
            history =[{"role":"user","content":prompt }]
            text =await self ._get_groq_response (prompt ,[{"role":"user","content":prompt }])
            return "true"in text .lower ()
        except Exception as e :
            logger .error (f"AI API error (evaluate_answer): {e}")

            return correct_answer .lower ().strip ()==user_answer .lower ().strip ()

    async def start_trivia_game (self ,ctx ,category :Optional [str ]):
        """Start a trivia game"""
        channel_id =ctx .channel .id 
        if channel_id in self .active_games :
            view = CV2View("🧠 Trivia Game", "A trivia game is already active in this channel!")
            await ctx .send (view=view)
            return 

        effective_category =category .lower ()if category else "mixed"
        question_data =await self .generate_trivia_question (effective_category ,[])
        if not question_data :
            view = CV2View("🧠 Trivia Game", "Failed to generate a trivia question. Try again later.")
            await ctx .send (view=view)
            return 

        self .active_games [channel_id ]={
        "category":effective_category ,
        "current_question":question_data ["question"],
        "current_answer":question_data ["answer"],
        "incorrect_answers":question_data ["incorrect_answers"],
        "scores":{},
        "round":1 ,
        "max_rounds":5 ,
        "used_questions":[question_data ["question"]],
        "hints_used":0 ,
        "skips_used":0 ,
        "answered":False ,
        }

        view =TriviaAnswerView (self ,channel_id ,question_data ["answer"],question_data ["incorrect_answers"])
        trivia_view = CV2View("🧠 Trivia Game", f"**Round 1/{self.active_games[channel_id]['max_rounds']}**\nCategory: {category or 'Mixed'}\n{question_data['question']}\n\n*Click a button to answer! First correct answer wins the point.*")
        await ctx .send (view =view )

    async def handle_trivia_answer (self ,interaction :discord .Interaction ,channel_id :int ,selected_answer :str ):
        """Handle trivia answer submission"""
        await interaction .response .defer ()
        game =self .active_games .get (channel_id )
        if not game :
            await interaction .followup .send ("No trivia game is active in this channel!",ephemeral =True )
            return 

        if game ["answered"]:
            await interaction .followup .send ("This question has already been answered! Wait for the next round.",ephemeral =True )
            return 

        game ["answered"]=True 
        user_id =interaction .user .id 
        username =interaction .user .display_name 
        is_correct =await self .evaluate_answer (game ["current_answer"],selected_answer )
        user_score =game ["scores"].get (user_id ,0 )+(1 if is_correct else -1 )
        game ["scores"][user_id ]=user_score 

        await self .trivia_scores .find_one_and_update (
        {"userId":user_id },
        {
        "username":username ,
        "$inc":{"score":1 if is_correct else -1 ,"gamesPlayed":1 },
        "$push":{"history":{"score":1 if is_correct else -1 ,"category":game ["category"]}},
        },
        upsert =True 
        )

        response_message =(
        f"🎉 First to answer! Correct! The answer was **{game['current_answer']}**. +1 point!"
        if is_correct 
        else f"{CROSS} Incorrect. The answer was **{game['current_answer']}**. Your guess: **{selected_answer}**. -1 point."
        )

        game ["used_questions"]=game ["used_questions"][-50 :]
        recent_questions =game ["used_questions"][-5 :]
        question_data =await self .generate_trivia_question (game ["category"],recent_questions )
        if not question_data :
            del self .active_games [channel_id ]
            view = CV2View("🧠 Trivia Game", "Failed to generate the next question. Game ended.")
            await interaction .followup .send (view=view)
            return 

        game ["current_question"]=question_data ["question"]
        game ["current_answer"]=question_data ["answer"]
        game ["incorrect_answers"]=question_data ["incorrect_answers"]
        game ["used_questions"].append (question_data ["question"])
        game ["round"]+=1 
        game ["answered"]=False 

        if game ["round"]>game ["max_rounds"]:
            response_message +="\n\n**Game Over!**\nScores:\n"
            for uid ,score in game ["scores"].items ():
                user =await interaction .guild .fetch_member (uid )
                response_message +=f"- {user.display_name if user else 'Unknown'}: {score}\n"
            del self .active_games [channel_id ]
            view = CV2View("🧠 Trivia Game", response_message)
            await interaction .followup .send (view=view)
        else :
            response_message +=f"\n\n**Round {game['round']}/{game['max_rounds']}**\n{game['current_question']}"
            view =TriviaAnswerView (self ,channel_id ,game ["current_answer"],game ["incorrect_answers"])
            trivia_view = CV2View("🧠 Trivia Game", response_message + "\n\n*Click a button to answer! First correct answer wins the point.*")
            await interaction .followup .send (view =view )

    async def show_stats (self ,ctx ):
        """Show user's trivia statistics"""
        user_id =ctx .author .id 
        stats =await self .trivia_scores .find_one ({"userId":user_id })
        if not stats :
            view = CV2View("🧠 Trivia Statistics", "You haven't played any trivia games yet! Start one with `/ai trivia`.")
            await ctx .send (view=view)
            return 

        total_games =stats ["gamesPlayed"]
        total_correct =sum (1 for h in stats ["history"]if h ["score"]>0 )
        win_rate =(total_correct /total_games *100 )if total_games >0 else 0 

        view = CV2View("🧠 Your Trivia Statistics",
            f"**Total Score:** {stats['score']}\n"
            f"**Games Played:** {total_games}\n"
            f"**Correct Answers:** {total_correct}\n"
            f"**Win Rate:** {win_rate:.2f}%")
        await ctx .send (view=view)

    async def show_leaderboard (self ,ctx ):
        """Show trivia leaderboard"""
        top_scores =await self .trivia_scores .find ()
        if not top_scores :
            view = CV2View("🏆 Trivia Leaderboard", "No scores yet! Play a trivia game to get started.")
            await ctx .send (view=view)
            return 

        leaderboard =""
        for index ,entry in enumerate (top_scores ,1 ):
            if index ==1 :
                emoji ="🥇"
            elif index ==2 :
                emoji ="🥈"
            elif index ==3 :
                emoji ="🥉"
            else :
                emoji =f"{index}."
            leaderboard +=f"{emoji} {entry['username']}: {entry['score']}\n"

        view = CV2View("🏆 Trivia Leaderboard", leaderboard)
        await ctx .send (view=view)

    async def enable_roleplay (self ,ctx ):
        """Enable roleplay mode in the current channel"""
        channel_id =ctx .channel .id 
        user_id =ctx .author .id 

        if channel_id in self .roleplay_channels :
            view = CV2View("🎭 Roleplay Mode", "Roleplay mode is already enabled in this channel! Use `/ai roleplay-disable` to turn it off.")
            await ctx .send (view=view)
            return 

        self .roleplay_channels [channel_id ]={
        "user_id":user_id ,
        "character_gender":None ,
        "character_type":None ,
        "awaiting_character":True ,
        }
        view = CV2View("🎭 Roleplay Mode", "Roleplay mode activated! To start, tell me what kind of character you want me to be.\nFor example: `female teacher` or `male astronaut`.")
        await ctx .send (view=view)

    async def disable_roleplay (self ,ctx ):
        """Disable roleplay mode in the current channel"""
        channel_id =ctx .channel .id 
        if channel_id not in self .roleplay_channels :
            view = CV2View("🎭 Roleplay Mode", "Roleplay mode is not enabled in this channel! Use `/ai roleplay-enable` to turn it on.")
            await ctx .send (view=view)
            return 

        del self .roleplay_channels [channel_id ]
        view = CV2View("🎭 Roleplay Mode", "Roleplay mode disabled in this channel.")
        await ctx .send (view=view)

    @ai .command (name ="roleplay-enable",description ="Enable roleplay mode in the current channel")
    async def ai_roleplay_enable (self ,ctx :commands .Context ):
        """Enable roleplay mode"""
        await self .enable_roleplay (ctx )

    @ai .command (name ="roleplay-disable",description ="Disable roleplay mode in the current channel")
    async def ai_roleplay_disable (self ,ctx :commands .Context ):
        """Disable roleplay mode"""
        await self .disable_roleplay (ctx )



async def setup (bot):
    await bot.add_cog(AI(bot ))