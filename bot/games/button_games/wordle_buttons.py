from __future__ import annotations

from typing import Optional

import discord
from discord.ext import commands

from ..wordle import Wordle
from ..utils import DiscordColor, DEFAULT_COLOR, BaseView


class WordInput(discord.ui.Modal, title="Word Input"):
    word = discord.ui.TextInput(
        label=f"Input your guess",
        style=discord.TextStyle.short,
        required=True,
        min_length=5,
        max_length=5,
    )

    def __init__(self, view: WordleView) -> None:
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction) -> None:
        content = self.word.value.lower()
        game = self.view.game

        if content not in game._valid_words:
            return await interaction.response.send_message(
                "That is not a valid word!", ephemeral=True
            )
        else:
            won = game.parse_guess(content)
            buf = await game.render_image()

            embed = discord.Embed(title="Wordle!", color=self.view.game.embed_color)
            embed.set_image(url="attachment://wordle.png")
            file = discord.File(buf, "wordle.png")

            if won:
                await interaction.message.reply(
                    "Game Over! You won!", mention_author=True
                )
            elif lost := len(game.guesses) >= 6:
                await interaction.message.reply(
                    f"Game Over! You lose, the word was: **{game.word}**",
                    mention_author=True,
                )

            if won or lost:
                self.view.disable_all()
                self.view.stop()

            return await interaction.response.edit_message(
                embed=embed, attachments=[file], view=self.view
            )


class WordInputButton(discord.ui.Button["WordleView"]):
    def __init__(self, *, cancel_button: bool = False):
        super().__init__(
            label="Cancel" if cancel_button else "Make a guess!",
            style=discord.ButtonStyle.red
            if cancel_button
            else discord.ButtonStyle.blurple,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game
        if interaction.user != game.player:
            return await interaction.response.send_message(
                "This isn't your game!", ephemeral=True
            )
        else:
            if self.label == "Cancel":
                await interaction.response.send_message(
                    f"Game Over! the word was: **{game.word}**"
                )
                await interaction.message.delete()
                return self.view.stop()
            else:
                return await interaction.response.send_modal(WordInput(self.view))


class WordleView(BaseView):
    def __init__(self, game: BetaWordle, *, timeout: float):
        super().__init__(timeout=timeout)

        self.game = game
        self.add_item(WordInputButton())
        self.add_item(WordInputButton(cancel_button=True))


class BetaWordle(Wordle):
    player: discord.User
    """
    Wordle(buttons) game
    """

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        embed_color: DiscordColor = DEFAULT_COLOR,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        """
        starts the wordle(buttons) game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.embed_color = discord.Color.random()
        self.player = ctx.author

        buf = await self.render_image()
        embed = discord.Embed(title="Wordle!", color=self.embed_color)
        embed.set_image(url="attachment://wordle.png")

        self.view = WordleView(self, timeout=timeout)
        self.message = await ctx.send(
            embed=embed,
            file=discord.File(buf, "wordle.png"),
            view=self.view,
        )
        await self.view.wait()
        return self.message
