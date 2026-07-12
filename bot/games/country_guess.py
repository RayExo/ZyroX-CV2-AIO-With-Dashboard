import asyncio
import difflib
import os
import pathlib
import random
from typing import Union, Optional
from io import BytesIO

import discord
from discord.ext import commands
from PIL import Image, ImageFilter, ImageOps

from .utils import *


class CountryGuesser:
    """
    CountryGuesser Game
    """

    embed: discord.Embed
    accepted_length: Optional[int]
    country: str

    def __init__(
        self,
        *,
        is_flags: bool = False,
        light_mode: bool = False,
        hard_mode: bool = False,
        hints: int = 1,
    ) -> None:
        self.embed_color: Optional[DiscordColor] = None
        self.hints = hints
        self.is_flags = is_flags
        self.hard_mode = hard_mode

        if self.is_flags:
            self.light_mode = False
        else:
            self.light_mode = light_mode

        folder = "assets/country-flags" if self.is_flags else "assets/country-data"
        self._countries_path = pathlib.Path(__file__).parent / folder
        self.all_countries = os.listdir(self._countries_path)
        self.responses_count = 0

    @executor()
    def invert_image(self, image_path: Union[BytesIO, os.PathLike, str]) -> BytesIO:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.invert(rgb)
            rgb = rgb.split()
            img = Image.merge("RGBA", rgb + (a,))

            buf = BytesIO()
            img.save(buf, "PNG")
            buf.seek(0)
            return buf

    @executor()
    def blur_image(self, image_path: Union[BytesIO, os.PathLike, str]) -> BytesIO:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            img = img.filter(ImageFilter.GaussianBlur(10))

            buf = BytesIO()
            img.save(buf, "PNG")
            buf.seek(0)
            return buf

    async def get_country(self) -> discord.File:
        country_file = random.choice(self.all_countries)
        self.country = country_file.strip()[:-4].lower()

        file = os.path.join(self._countries_path, country_file)

        if self.hard_mode:
            file = await self.blur_image(file)

        if self.light_mode:
            file = await self.invert_image(file)

        return discord.File(file, "country.png")

    def get_blanks(self) -> str:
        return " ".join("_" if char != " " else " " for char in self.country)

    def get_hint(self) -> str:
        blanks = ["_" if char != " " else " " for char in self.country]
        times = round(len(blanks) / 3)

        for _ in range(times):
            idx = random.choice(range(len(self.country)))
            blanks[idx] = self.country[idx]
        return " ".join(blanks)

    def get_accuracy(self, guess: str) -> int:
        return round(difflib.SequenceMatcher(None, guess, self.country).ratio() * 100)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Guess that country!",
            description=f"```fix\n{self.get_blanks()}\n```",
            color=discord.Color.random(),
        )
        embed.add_field(
            name="\u200b",
            value=f"```yml\nblurred: {str(self.hard_mode).lower()}\nflag-mode: {str(self.is_flags).lower()}\n```",
            inline=False,
        )
        embed.set_image(url="attachment://country.png")
        return embed

    async def wait_for_response(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        options: tuple[str, ...] = (),
        length: Optional[int] = None,
    ) -> Optional[tuple[discord.Message, str]]:
        def check(m: discord.Message) -> bool:
            if length:
                return (
                    m.channel == ctx.channel
                    and m.author != ctx.bot.user
                    and len(m.content) == length
                )
            else:
                return m.channel == ctx.channel and m.author != ctx.bot.user

        message: discord.Message = await ctx.bot.wait_for(
            "message", timeout=self.timeout, check=check
        )
        content = message.content.strip().lower()

        if options:
            if not content in options:
                return

        return message, content

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        timeout: Optional[float] = 100.0,
        embed_color: DiscordColor = discord.Color.random(),
    ) -> discord.Message:
        file = await self.get_country()

        self.timeout = timeout
        self.embed_color = discord.Color.random()
        self.embed = self.get_embed()
        self.embed.set_footer(text="send your guess within 100 seconds into the chat now!")

        self.message = await ctx.send(embed=self.embed, file=file)

        self.accepted_length = None
        start_time = asyncio.get_event_loop().time()

        while not ctx.bot.is_closed() and asyncio.get_event_loop().time() - start_time < self.timeout:
            try:
                msg, response = await self.wait_for_response(ctx)
            except asyncio.TimeoutError:
                break

            self.responses_count += 1

            if response == self.country:
                elapsed_time = round(asyncio.get_event_loop().time() - start_time, 2)
                await msg.reply(
                    f"That is correct! The country was `{self.country.title()}`"
                )
                return await self.end_game(ctx, msg.author, elapsed_time)
            else:
                acc = self.get_accuracy(response)

                if self.responses_count % 10 == 0 and self.hints:
                    hint = self.get_hint()
                    await ctx.send(f"Hint: `{hint}`")

                await msg.reply(
                    f"That was incorrect! but you are `{acc}%` of the way there!",
                    mention_author=False,
                )

        # Check if the time has exceeded the timeout
        #if asyncio.get_event_loop().time() - start_time > timeout:
            #return await self.end_game(ctx)  # Call end_game when timeout occurs
          

        return await self.end_game(ctx)

    async def end_game(
        self,
        ctx: commands.Context[commands.Bot],
        winner: Optional[discord.User] = None,
        time_taken: Optional[float] = None, manual_end: bool = False
    ) -> discord.Message:
        embed = discord.Embed(title="Game Over", color=self.embed_color)
        if winner and time_taken:
            embed.add_field(
                name="Winner",
                value=f"{winner.mention} ({winner.name})",
                inline=False,
            )
            embed.add_field(name="Time Taken", value=f"{time_taken} seconds", inline=False)
        elif manual_end:
            embed.description = "The game was manually ended."
        else:
            embed.description = f"Time's up! No one guessed the country. The correct answer was `{self.country.title()}`."
          
        return await ctx.send(embed=embed)

    
    async def end_game_manually(self, ctx: commands.Context):
        await self.end_game(ctx, manual_end=True)


    