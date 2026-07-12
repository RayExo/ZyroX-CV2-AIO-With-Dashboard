"""This folder contains games that require discord.py v2.0.0 + to be used
they utilize UI components such as buttons.
"""
from __future__ import annotations

#from .aki_buttons import BetaAkinator
from .twenty_48_buttons import BetaTwenty48
from .wordle_buttons import BetaWordle
from .tictactoe_buttons import BetaTictactoe
from .memory_game import MemoryGame
from .rps_buttons import BetaRockPaperScissors
#from .hangman_buttons import BetaHangman
from .reaction_test_buttons import BetaReactionGame
from .country_guess_buttons import BetaCountryGuesser
from .chess_buttons import BetaChess
from .battleship_buttons import BetaBattleShip
from .number_slider import NumberSlider
from .lights_out import LightsOut
#from .boggle import Boggle
from .connect_four_buttons import BetaConnectFour


__all__: tuple[str, ...] = (
    "BetaConnectFour",
    "BetaTwenty48",
    "BetaWordle",
    "BetaTictactoe",
    "MemoryGame",
    "BetaRockPaperScissors",
    "BetaReactionGame",
    "BetaCountryGuesser",
    "BetaChess",
    "BetaBattleShip",
    "NumberSlider",
    "LightsOut",
)
