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

from typing import Optional
import random

import discord
from utils.emoji import WARNING_ALT
from discord.ext import commands

from ..rps import RockPaperScissors
from ..utils import DiscordColor, DEFAULT_COLOR, BaseView


class RPSButton(discord.ui.Button["RPSView"]):
    def __init__(self, emoji: str, *, style: discord.ButtonStyle) -> None:
        super().__init__(
            label="\u200b",
            emoji=emoji,
            style=style,
        )

    def get_choice(self, user: discord.User, other: bool = False) -> Optional[str]:
        game = self.view.game
        if other:
            return game.player2_choice if user == game.player2 else game.player1_choice
        else:
            return game.player1_choice if user == game.player1 else game.player2_choice

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game
        players = (game.player1, game.player2) if game.player2 else (game.player1,)

        if interaction.user not in players:
            return await interaction.response.send_message(
                "This is not your game!", ephemeral=True
            )
        else:
            if not game.player2:
                bot_choice = random.choice(game.OPTIONS)
                user_choice = self.emoji.name

                if user_choice == bot_choice:
                    game.embed.description = f"**Tie!**\nWe both picked {user_choice}"
                else:
                    if game.check_win(bot_choice, user_choice):
                        game.embed.description = f"**You Won!**\nYou picked {user_choice} and I picked {bot_choice}."
                    else:
                        game.embed.description = f"**You Lost!**\nI picked {bot_choice} and you picked {user_choice}."

                self.view.disable_all()
                self.view.stop()

            else:
                if self.get_choice(interaction.user):
                    return await interaction.response.send_message(
                        "You have already chosen!", ephemeral=True
                    )

                other_player_choice = self.get_choice(interaction.user, other=True)

                if interaction.user == game.player1:
                    game.player1_choice = self.emoji.name

                    if not other_player_choice:
                        game.embed.description += f"\n\n{game.player1.mention} has chosen...\n*Waiting for {game.player2.mention} to choose...*"
                else:
                    game.player2_choice = self.emoji.name

                    if not other_player_choice:
                        game.embed.description += f"\n\n{game.player2.mention} has chosen...\n*Waiting for {game.player1.mention} to choose...*"

                if game.player1_choice and game.player2_choice:
                    if game.player1_choice == game.player2_choice:
                        game.embed.description = f"**Tie!**\nBoth {game.player1.mention} and {game.player2.mention} picked {game.player1_choice}."
                    else:
                        who_won = (
                            game.player1
                            if game.check_win(game.player2_choice, game.player1_choice)
                            else game.player2
                        )

                        game.embed.description = (
                            f"**{who_won.mention} Won!**"
                            f"\n\n{game.player1.mention} chose {game.player1_choice}."
                            f"\n{game.player2.mention} chose {game.player2_choice}."
                        )

                    self.view.disable_all()
                    self.view.stop()

            return await interaction.response.edit_message(
                embed=game.embed, view=self.view
            )


class RPSView(BaseView):
    game: BetaRockPaperScissors

    def __init__(
        self,
        game: BetaRockPaperScissors,
        *,
        button_style: discord.ButtonStyle,
        timeout: float,
    ) -> None:

        super().__init__(timeout=timeout)

        self.button_style = button_style
        self.game = game

        for option in self.game.OPTIONS:
            self.add_item(RPSButton(option, style=self.button_style))


class BetaRockPaperScissors(RockPaperScissors):
    """
    RockPaperScissors(buttons) game
    """

    player1: discord.User
    embed: discord.Embed

    def __init__(self, other_player: Optional[discord.User] = None) -> None:
        self.player2 = other_player

        if self.player2:
            self.player1_choice: Optional[str] = None
            self.player2_choice: Optional[str] = None

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        button_style: discord.ButtonStyle = discord.ButtonStyle.blurple,
        embed_color: DiscordColor = DEFAULT_COLOR,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        if ctx.author == self.player2:
            embed = discord.Embed(title=f"{WARNING_ALT}   Access Denied", description="You cannot play against yourself!", color=0x000000)
            return await ctx.reply(embed=embed)
            
        """
        Starts the Rock Paper Scissors (buttons) game.

        Parameters
        ----------
        ctx : commands.Context
            The context of the invoking command.
        button_style : discord.ButtonStyle, optional
            The primary button style to use, by default discord.ButtonStyle.blurple.
        embed_color : DiscordColor, optional
            The color of the game embed, by default DEFAULT_COLOR.
        timeout : Optional[float], optional
            The timeout for the view, by default None.

        Returns
        -------
        discord.Message
            Returns the game message.
        """
        self.player1 = ctx.author

        self.embed = discord.Embed(
            title="Rock Paper Scissors",
            description="Select a button to play!",
            color=discord.Color.random(),
        )

        self.view = RPSView(self, button_style=button_style, timeout=timeout)
        self.message = await ctx.send(embed=self.embed, view=self.view)

        await self.view.wait()
        return self.message
