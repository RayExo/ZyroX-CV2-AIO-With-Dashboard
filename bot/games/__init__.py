"""Discord-Games

A library designed for simple implementation of various classical games into a discord.py bot
"""
from __future__ import annotations

from typing import NamedTuple

#import os
#os.system("pip install chess")
#os.system("pip install english-words")
#os.system("pip install pillow")
#os.system("pip install typing_extensions")
#from .aki import Akinator
from .battleship import BattleShip
from .chess_game import Chess
from .connect_four import ConnectFour
#from .hangman import Hangman
from .tictactoe import Tictactoe
from .twenty_48 import Twenty48, create_2048_emojis
from .typeracer import TypeRacer
from .rps import RockPaperScissors
from .reaction_test import ReactionGame
from .country_guess import CountryGuesser
from .wordle import Wordle

__all__: tuple[str, ...] = (
    "BattleShip",
    "Chess",
    "ConnectFour",
    "Tictactoe",
    "Twenty48",
    "create_2048_emojis",
    "TypeRacer",
    "RockPaperScissors",
    "ReactionGame",
    "CountryGuesser",
    "Wordle",
)

__title__ = "discord_games"
__version__ = "1.10.6"
__author__ = "Tom-the-Bomb"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present Tom-the-Bomb"


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int


version_info: VersionInfo = VersionInfo(
    major=1,
    minor=10,
    micro=6,
)

del NamedTuple, VersionInfo
