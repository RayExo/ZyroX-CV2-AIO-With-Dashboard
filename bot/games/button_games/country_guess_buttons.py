from __future__ import annotations

from typing import Optional

import discord
from discord.ext import commands

from ..country_guess import CountryGuesser
from ..utils import DiscordColor, DEFAULT_COLOR, BaseView


class CountryInput(discord.ui.Modal, title="Input your guess!"):
    def __init__(self, view: CountryView) -> None:
        super().__init__()
        self.view = view

        self.guess = discord.ui.TextInput(
            label="Input your guess",
            style=discord.TextStyle.short,
            required=True,
            max_length=self.view.game.accepted_length,
        )

        self.add_item(self.guess)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        guess = self.guess.value.strip().lower()
        game = self.view.game

        if guess == game.country:
            game.update_guesslog("+ GAME OVER, you won! +")
            await interaction.response.send_message(
                f"That is correct! The country was `{game.country.title()}`"
            )

            self.view.disable_all()
            game.embed.description = f"```fix\n{game.country.title()}\n```"
            await interaction.message.edit(view=self.view, embed=game.embed)
            return self.view.stop()
        else:
            game.guesses -= 1

            if not game.guesses:
                self.view.disable_all()
                game.update_guesslog("- GAME OVER, you lost -")

                await interaction.message.edit(embed=game.embed, view=self.view)
                await interaction.response.send_message(
                    f"Game Over! you lost, The country was `{game.country.title()}`"
                )
                return self.view.stop()
            else:
                acc = game.get_accuracy(guess)
                game.update_guesslog(
                    f"- [{guess}] was incorrect! but you are ({acc}%) of the way there!\n"
                    f"+ You have {game.guesses} guesses left.\n"
                )

                await interaction.response.edit_message(embed=game.embed)


class CountryView(BaseView):
    def __init__(
        self, game: BetaCountryGuesser, *, user: discord.User, timeout: float
    ) -> None:
        super().__init__(timeout=timeout)

        self.game = game
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message(
                f"This is not your game!", ephemeral=True
            )
            return False
        else:
            return True

    @discord.ui.button(label="Make a guess!", style=discord.ButtonStyle.blurple)
    async def guess_button(self, interaction: discord.Interaction, _) -> None:
        return await interaction.response.send_modal(CountryInput(self))

    @discord.ui.button(label="hint", style=discord.ButtonStyle.green)
    async def hint_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        hint = self.game.get_hint()
        self.game.hints -= 1
        await interaction.response.send_message(
            f"Here is your hint: `{hint}`", ephemeral=True
        )

        if not self.game.hints:
            button.disabled = True
            await interaction.message.edit(view=self)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, _) -> None:
        self.disable_all()

        self.game.embed.description = f"```fix\n{self.game.country.title()}\n```"
        self.game.update_guesslog("- GAME OVER, CANCELLED -")

        await interaction.response.send_message(
            f"Game Over! The country was `{self.game.country.title()}`"
        )
        await interaction.message.edit(view=self, embed=self.game.embed)
        return self.stop()


class BetaCountryGuesser(CountryGuesser):
    """
    Country Guesser(buttons) Game
    """

    guesslog: str = ""

    def update_guesslog(self, entry: str) -> None:
        self.guesslog += entry + "\n"
        self.embed.set_field_at(
            1, name="Guess Log", value=f"```diff\n{self.guesslog}\n```"
        )

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        embed_color: DiscordColor = DEFAULT_COLOR,
        ignore_diff_len: bool = False,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        """
        starts the Country Guesser(buttons) Game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        ignore_diff_len : bool, optional
            specifies whether or not to ignore guesses that are not of the same length as the correct answer, by default False
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.accepted_length = len(self.country) if ignore_diff_len else None

        file = await self.get_country()

        self.embed_color = discord.Color.random()
        self.embed = self.get_embed()
        self.embed.add_field(
            name="Guess Log", value="```diff\n\u200b\n```", inline=False
        )

        self.view = CountryView(self, user=ctx.author, timeout=timeout)
        self.message = await ctx.send(embed=self.embed, file=file, view=self.view)

        await self.view.wait()
        return self.message
