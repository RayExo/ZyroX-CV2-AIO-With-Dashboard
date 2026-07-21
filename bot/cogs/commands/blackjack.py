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
from discord.ext import commands
import os
import random
from typing import List, Tuple, Union
from PIL import Image
from utils.Tools import *
from utils.cv2 import CV2, build_container
from discord.ui import LayoutView, TextDisplay, Separator, Container

class CV2(LayoutView):
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        items = [TextDisplay(f"**{title}**")]
        for s in sections:
            if s:
                items.append(Separator(visible=True))
                items.append(TextDisplay(str(s)))
        self.add_item(build_container(*items))

CARDS_PATH = 'data/cards/'

class Card:
    suits = ["clubs", "diamonds", "hearts", "spades"]

    def __init__(self, suit: str, value: int, down=False):
        self.suit = suit
        self.value = value
        self.down = down
        self.symbol = self.name[0].upper()

    @property
    def name(self) -> str:
        if self.value <= 10:
            return str(self.value)
        else:
            return {
                11: 'jack',
                12: 'queen',
                13: 'king',
                14: 'ace',
            }[self.value]

    @property
    def image(self):
        return (
            f"{self.symbol if self.name != '10' else '10'}" \
            f"{self.suit[0].upper()}.png" \
            if not self.down else "red_back.png"
        )

    def flip(self):
        self.down = not self.down
        return self

    def __str__(self) -> str:
        return f'{self.name.title()} of {self.suit.title()}'

    def __repr__(self) -> str:
        return str(self)


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def hand_to_images(hand: List[Card]) -> List[Image.Image]:
        return [Image.open(os.path.join(CARDS_PATH, card.image)) for card in hand]

    @staticmethod
    def center(*hands: Tuple[Image.Image]) -> Image.Image:
        bg: Image.Image = Image.open(os.path.join(CARDS_PATH, 'table.png'))
        bg_center_x = bg.size[0] // 2
        bg_center_y = bg.size[1] // 2

        img_w = hands[0][0].size[0]
        img_h = hands[0][0].size[1]

        start_y = bg_center_y - (((len(hands) * img_h) + ((len(hands) - 1) * 15)) // 2)

        for hand in hands:
            start_x = bg_center_x - (((len(hand) * img_w) + ((len(hand) - 1) * 10)) // 2)
            for card in hand:
                bg.alpha_composite(card, (start_x, start_y))
                start_x += img_w + 10
            start_y += img_h + 15

        return bg

    def output(self, name, *hands: Tuple[List[Card]]) -> None:
        self.center(*map(self.hand_to_images, hands)).save(f'data/{name}.png')

    @staticmethod
    def calc_hand(hand: List[Card]) -> int:
        non_aces = [c for c in hand if c.symbol != 'A']
        aces = [c for c in hand if c.symbol == 'A']
        total_sum = 0
        for card in non_aces:
            if not card.down:
                if card.symbol in 'JQK':
                    total_sum += 10
                else:
                    total_sum += card.value
        for card in aces:
            if not card.down:
                if total_sum <= 10:
                    total_sum += 11
                else:
                    total_sum += 1
        return total_sum

    @commands.command(aliases=['bj', 'blackjacks'], help="Play a simple game of blackjack.", usage="blackjack")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blackjack(self, ctx: commands.Context):
        try:
            deck = [Card(suit, num) for num in range(2, 15) for suit in Card.suits]
            random.shuffle(deck)

            player_hand: List[Card] = []
            dealer_hand: List[Card] = []

            player_hand.append(deck.pop())
            dealer_hand.append(deck.pop())
            player_hand.append(deck.pop())
            dealer_hand.append(deck.pop())

            dealer_hand[1] = dealer_hand[1].flip() 

            player_score = self.calc_hand(player_hand)
            dealer_score = self.calc_hand(dealer_hand)

            async def out_table(**kwargs) -> discord.Message:
                self.output(ctx.author.id, dealer_hand, player_hand)
                file = discord.File(f"data/{ctx.author.id}.png", filename=f"{ctx.author.id}.png")
                view = CV2(kwargs.get('title', 'Blackjack'), kwargs.get('description', ''))
                msg: discord.Message = await ctx.send(file=file, view=view)
                return msg

            def check(reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> bool:
                return all((
                    str(reaction.emoji) in ("🇸", "🇭"),
                    user == ctx.author,
                    user != self.bot.user,
                    reaction.message == msg
                ))

            standing = False

            while True:
                player_score = self.calc_hand(player_hand)
                dealer_score = self.calc_hand(dealer_hand)

                if player_score == 21:  
                    result = ("Blackjack!", 'won')
                    break

                elif player_score > 21: 
                    result = ("Player busts", 'lost')
                    break

                msg = await out_table(
                    title="Your Turn",
                    description=f"Your hand: {player_score}\nDealer's hand: {dealer_score}"
                )

                await msg.add_reaction("🇭")
                await msg.add_reaction("🇸")

                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return

                if str(reaction.emoji) == "🇭":
                    player_hand.append(deck.pop())
                    await msg.delete()
                    continue

                elif str(reaction.emoji) == "🇸":
                    standing = True
                    break

            if standing:
                dealer_hand[1] = dealer_hand[1].flip()  
                player_score = self.calc_hand(player_hand)
                dealer_score = self.calc_hand(dealer_hand)

                while dealer_score < 17:
                    dealer_hand.append(deck.pop())
                    dealer_score = self.calc_hand(dealer_hand)

                if dealer_score == 21:
                    result = ('Dealer blackjack', 'lost')
                elif dealer_score > 21:
                    result = ("Dealer busts", 'won')
                elif dealer_score == player_score:
                    result = ("Tie!", 'kept')
                elif dealer_score > player_score:
                    result = ("You lose!", 'lost')
                elif dealer_score < player_score:
                    result = ("You win!", 'won')

            color = (
                discord.Color.red() if result[1] == 'lost'
                else discord.Color.green() if result[1] == 'won'
                else discord.Color.blue()
            )
            try:
                await msg.delete()
            except:
                pass
            msg = await out_table(
                title=result[0],
                color=color,
                description=(
                    f"**You {result[1]}**\nYour hand: {player_score}\n" +
                    f"Dealer's hand: {dealer_score}"
                )
            )
            os.remove(f'data/{ctx.author.id}.png')
        except Exception as e:
            print(e)


 