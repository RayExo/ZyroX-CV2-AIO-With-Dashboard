import discord
from discord.ext import commands
import random
import os
import uuid
from PIL import Image
import bisect
from utils.Tools import *


class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['slot'])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slots(self, ctx: commands.Context):
        try:
            path = os.path.join('data/pictures/')
            facade = Image.open(f'{path}slot-face.png').convert('RGBA')
            reel = Image.open(f'{path}slot-reel.png').convert('RGBA')

            rw, rh = reel.size
            item = 180
            items = rh // item

            s1 = random.randint(1, items - 1)
            s2 = random.randint(1, items - 1)
            s3 = random.randint(1, items - 1)

            win_rate = 25 / 100

            if random.random() < win_rate:
                symbols_weights = [3.5, 7, 15, 25, 55]
                x = round(random.random() * 100, 1)
                pos = bisect.bisect(symbols_weights, x)
                s1 = pos + (random.randint(1, (items // 6) - 1) * 6)
                s2 = pos + (random.randint(1, (items // 6) - 1) * 6)
                s3 = pos + (random.randint(1, (items // 6) - 1) * 6)
                s1 = s1 - 6 if s1 == items else s1
                s2 = s2 - 6 if s2 == items else s2
                s3 = s3 - 6 if s3 == items else s3

            images = []
            speed = 6
            for i in range(1, (item // speed) + 1):
                bg = Image.new('RGBA', facade.size, color=(255, 255, 255))
                bg.paste(reel, (25 + rw * 0, 100 - (speed * i * s1)))
                bg.paste(reel, (25 + rw * 1, 100 - (speed * i * s2)))
                bg.paste(reel, (25 + rw * 2, 100 - (speed * i * s3)))
                bg.alpha_composite(facade)
                images.append(bg)

            unique_filename = str(uuid.uuid4()) + '.gif'
            fp = os.path.join('data/pictures/', unique_filename)

            images[0].save(
                fp,
                save_all=True,
                append_images=images[1:],
                duration=50
            )

            file = discord.File(fp, filename=unique_filename)
            message = await ctx.reply(file=file)

            if (1 + s1) % 6 == (1 + s2) % 6 == (1 + s3) % 6:
                result = 'won'
            else:
                result = 'lost'

            embed = discord.Embed(
                title=f'{ctx.author.display_name}, You {result}!',
                color=discord.Color.green() if result == "won" else discord.Color.red()
            )

            embed.set_image(url=f"attachment://{unique_filename}")
            await message.edit(content=None, embed=embed)

            os.remove(fp)
        except Exception as e:
            print(e)


 