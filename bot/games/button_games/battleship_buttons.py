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

from typing import Optional, Any, Coroutine, Union
import asyncio
import string

import discord
from discord.ext import commands
from utils.emoji import TARGET
from utils.emoji import TARGET

from ..battleship import (
    BattleShip,
    SHIPS,
    Ship,
    Board,
)

from .wordle_buttons import WordInputButton
from ..utils import DiscordColor, DEFAULT_COLOR, BaseView


class Player:
    def __init__(self, player: discord.User, *, game: BetaBattleShip) -> None:
        self.game = game
        self.player = player

        self.embed = discord.Embed(title="Log", description="```\n\u200b\n```")

        self._logs: list[str] = []
        self.log: str = ""

        self.approves_cancel: bool = False

    def update_log(self, log: str) -> None:
        self._logs.append(log)
        log_str = "\n\n".join(self._logs[-self.game.max_log_size :])

        if len(self._logs) > self.game.max_log_size:
            log_str = "...\n\n" + log_str

        self.embed.description = f"```diff\n{log_str}\n```"

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self.player.__getattribute__(name)


class BattleshipInput(discord.ui.Modal, title="Input a coordinate"):
    def __init__(self, view: BattleshipView) -> None:
        super().__init__()
        self.view = view

        self.coord = discord.ui.TextInput(
            label="Enter your target coordinate",
            placeholder="ex: a8",
            style=discord.TextStyle.short,
            required=True,
            min_length=2,
            max_length=3,
        )

        self.add_item(self.coord)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        game = self.view.game
        content = self.coord.value
        content = content.strip().lower()

        if not game.inputpat.fullmatch(content):
            return await interaction.response.send_message(
                f"`{content}` is not a valid coordinate!", ephemeral=True
            )
        else:
            raw, coords = game.get_coords(content)
            self.view.update_views()

            if coords in self.view.player_board.moves:
                return await interaction.response.send_message(
                    "You've attacked this coordinate before!", ephemeral=True
                )
            else:
                await interaction.response.defer()
                return await game.process_move(raw, coords)


class BattleshipButton(WordInputButton):
    view: BattleshipView

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game

        if self.label == "Cancel":
            player = self.view.player
            other_player = (
                game.player2
                if interaction.user == game.player1.player
                else game.player1
            )

            if not player.approves_cancel:
                player.approves_cancel = True

            await interaction.response.defer()

            if not other_player.approves_cancel:
                await player.send("- Waiting for opponent to approve cancellation -")
                await other_player.send(
                    "Opponent wants to cancel, press the `Cancel` button if you approve."
                )
            else:
                game.view1.disable_all()
                game.view2.disable_all()

                await game.player1.send("**GAME OVER**, Cancelled")
                await game.player2.send("**GAME OVER**, Cancelled")

                await game.message1.edit(view=game.view1)
                await game.message2.edit(view=game.view2)

                game.view1.stop()
                return game.view2.stop()
        else:
            if interaction.user != game.turn.player:
                return await interaction.response.send_message(
                    "It is not your turn yet!", ephemeral=True
                )
            else:
                return await interaction.response.send_modal(BattleshipInput(self.view))


class CoordButton(discord.ui.Button["BattleshipView"]):
    def __init__(self, letter_or_num: Union[str, int]) -> None:
        super().__init__(
            label=str(letter_or_num),
            style=discord.ButtonStyle.green,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game

        if self.label.isdigit():
            self.view.digit = int(self.label)

            raw = self.view.alpha + str(self.view.digit)
            coords = (game.to_num(self.view.alpha), self.view.digit)
            await interaction.response.defer()

            self.view.alpha = None
            self.view.digit = None

            self.view.update_views()
            return await game.process_move(raw, coords)
        else:
            self.view.alpha = self.label.lower()
            self.view.initialize_view(clear=True)
            return await interaction.response.edit_message(view=self.view)


class BattleshipView(BaseView):
    def __init__(self, game: BetaBattleShip, user: Player, *, timeout: float) -> None:
        super().__init__(timeout=timeout)

        self.game = game
        self.player = user
        self.player_board = self.game.get_board(self.player)

        self.initialize_view(start=True)

        self.alpha: Optional[str] = None
        self.digit: Optional[int] = None

    def disable(self) -> None:
        self.disable_all()
        self.children[-1].disabled = False

    def update_views(self) -> None:
        game = self.game
        self.disable()

        other_view = game.view1 if game.turn == game.player2 else game.view2

        other_view.clear_items()
        other_view.initialize_view()

    def initialize_view(self, *, clear: bool = False, start: bool = False) -> None:
        moves = self.player_board.moves

        if clear:
            self.clear_items()
            for num in range(1, 11):
                button = CoordButton(num)
                coord = (self.game.to_num(self.alpha), num)
                if coord in moves:
                    button.disabled = True
                self.add_item(button)
        else:
            for letter in string.ascii_uppercase[:10]:
                button = CoordButton(letter)
                if all(
                    (self.game.to_num(letter.lower()), i) in moves for i in range(1, 11)
                ):
                    button.disabled = True
                self.add_item(button)

        inpbutton = BattleshipButton()
        inpbutton.label = "\u200b"
        inpbutton.emoji = TARGET

        self.add_item(inpbutton)
        self.add_item(BattleshipButton(cancel_button=True))

        if start and self.player == self.game.player2:
            self.disable()


class SetupInput(discord.ui.Modal):
    def __init__(self, button: SetupButton) -> None:
        self.button = button
        self.ship = self.button.label

        super().__init__(title=f"{self.ship} Setup")

        self.start_coord = discord.ui.TextInput(
            label=f"Enter the starting coordinate",
            placeholder="ex: a8",
            style=discord.TextStyle.short,
            required=True,
            min_length=2,
            max_length=3,
        )

        self.is_vertical = discord.ui.TextInput(
            label=f"Do you want it to be vertical? (y/n)",
            placeholder='"y" or "n"',
            style=discord.TextStyle.short,
            required=True,
            min_length=1,
            max_length=1,
        )

        self.add_item(self.start_coord)
        self.add_item(self.is_vertical)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        game = self.button.view.game

        start = self.start_coord.value.strip().lower()
        vertical = self.is_vertical.value.strip().lower()

        board = game.get_board(interaction.user)

        if not game.inputpat.match(start):
            return await interaction.response.send_message(
                f"{start} is not a valid coordinate!", ephemeral=True
            )

        if vertical not in ("y", "n"):
            return await interaction.response.send_message(
                f"Response for `vertical` must be either `y` or `n`", ephemeral=True
            )

        vertical = vertical != "y"

        _, start = game.get_coords(start)

        new_ship = Ship(
            name=self.ship,
            size=self.button.ship_size,
            start=start,
            vertical=vertical,
            color=self.button.ship_color,
        )

        if board._is_valid(new_ship):
            self.button.disabled = True
            board.ships.append(new_ship)

            embed, file, _, _ = await game.get_file(interaction.user, hide=False)

            await interaction.response.edit_message(
                attachments=[file], embed=embed, view=self.button.view
            )

            if all(
                button.disabled
                for button in self.button.view.children
                if isinstance(button, discord.ui.Button)
            ):
                await interaction.user.send(
                    "**All setup!** (Game will soon start after the opponent finishes)"
                )
                return self.button.view.stop()
        else:
            return await interaction.response.send_message(
                "Ship placement was detected to be invalid, please try again.",
                ephemeral=True,
            )


class SetupButton(discord.ui.Button["SetupView"]):
    def __init__(
        self, label: str, ship_size: int, ship_color: tuple[int, int, int]
    ) -> None:
        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
        )

        self.ship_size = ship_size
        self.ship_color = ship_color

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(SetupInput(self))


class SetupView(BaseView):
    def __init__(self, game: BetaBattleShip, timeout: float) -> None:
        super().__init__(timeout=timeout)

        self.game = game

        for ship, (size, color) in SHIPS.items():
            self.add_item(SetupButton(ship, size, color))


class BetaBattleShip(BattleShip):
    """
    BattleShip(buttons) Game
    """

    embed: discord.Embed

    def __init__(
        self,
        player1: discord.User,
        player2: discord.User,
        *,
        random: bool = True,
    ) -> None:

        super().__init__(player1, player2, random=random)

        self.player1: Player = Player(player1, game=self)
        self.player2: Player = Player(player2, game=self)

        self.turn: Player = self.player1

    def get_board(self, player: discord.User, other: bool = False) -> Board:
        player = getattr(player, "player", player)
        if other:
            return (
                self.player2_board
                if player == self.player1.player
                else self.player1_board
            )
        else:
            return (
                self.player1_board
                if player == self.player1.player
                else self.player2_board
            )

    async def get_ship_inputs(self, user: Player) -> Coroutine[Any, Any, bool]:
        embed, file, _, _ = await self.get_file(user)

        embed1 = discord.Embed(
            description="**Press the buttons to place your ships!**",
            color=self.embed_color,
        )

        view = SetupView(self, timeout=self.timeout)
        await user.send(file=file, embeds=[embed, embed1], view=view)

        return view.wait()

    async def process_move(self, raw: str, coords: tuple[int, int]):
        sunk, hit = self.place_move(self.turn, coords)
        next_turn = self.player2 if self.turn == self.player1 else self.player1

        if hit and sunk:
            self.turn.update_log(
                f"+ ({raw}) was a hit!, you also sank one of their ships! :)"
            )
            next_turn.update_log(
                f"- They went for ({raw}), and it was a hit!\n- One of your ships also got sunk! :("
            )
        elif hit:
            self.turn.update_log(f"+ ({raw}) was a hit :)")
            next_turn.update_log(f"- They went for ({raw}), and it was a hit! :(")
        else:
            self.turn.update_log(f"- ({raw}) was a miss :(")
            next_turn.update_log(f"+ They went for ({raw}), and it was a miss! :)")

        e1, f1, e2, f2 = await self.get_file(self.player1)
        e3, f3, e4, f4 = await self.get_file(self.player2)

        self.turn = next_turn

        self.player1.embed.set_field_at(
            0, name="\u200b", value=f"```yml\nturn: {self.turn.player}\n```"
        )
        self.player2.embed.set_field_at(
            0, name="\u200b", value=f"```yml\nturn: {self.turn.player}\n```"
        )

        await self.message1.edit(
            view=self.view1,
            content="**Battleship**",
            embeds=[e2, e1, self.player1.embed],
            attachments=[f2, f1],
        )
        await self.message2.edit(
            view=self.view2,
            content="**Battleship**",
            embeds=[e4, e3, self.player2.embed],
            attachments=[f4, f3],
        )

        if winner := self.who_won():
            await winner.send("Congrats, you won! :)")

            other = self.player2 if winner == self.player1 else self.player1
            await other.send("You lost, better luck next time :(")

            self.view1.stop()
            return self.view2.stop()

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        max_log_size: int = 10,
        embed_color: DiscordColor = DEFAULT_COLOR,
        timeout: Optional[float] = None,
    ) -> tuple[discord.Message, discord.Message]:
        """
        starts the battleship(buttons) game

        Parameters
        ----------
        ctx : commands.Context[commands.Bot]
            the context of the invokation command
        max_log_size : int, optional
            indicates the length of the move log to show, by default 10
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        tuple[discord.Message, discord.Message]
            returns the game messages respectively
        """
        self.max_log_size = max_log_size
        self.timeout = timeout
        self.embed_color = embed_color

        await ctx.send("**Game Started!**\nI've setup the boards in your dms!")

        if not self.random:
            await asyncio.gather(
                await self.get_ship_inputs(self.player1),
                await self.get_ship_inputs(self.player2),
            )

        self.player1.embed.color = self.embed_color
        self.player2.embed.color = self.embed_color

        e1, f1, e2, f2 = await self.get_file(self.player1)
        e3, f3, e4, f4 = await self.get_file(self.player2)

        self.view1 = BattleshipView(self, user=self.player1, timeout=timeout)
        self.view2 = BattleshipView(self, user=self.player2, timeout=timeout)

        self.player1.embed.add_field(
            name="\u200b", value=f"```yml\nturn: {self.turn.player}\n```"
        )
        self.player2.embed.add_field(
            name="\u200b", value=f"```yml\nturn: {self.turn.player}\n```"
        )

        self.message1 = await self.player1.send(
            content="**Game starting!**",
            view=self.view1,
            embeds=[e2, e1, self.player1.embed],
            files=[f2, f1],
        )
        self.message2 = await self.player2.send(
            content="**Game starting!**",
            view=self.view2,
            embeds=[e4, e3, self.player2.embed],
            files=[f4, f3],
        )

        await asyncio.gather(
            self.view1.wait(),
            self.view2.wait(),
        )
        return self.message1, self.message2
