import random
from typing import List
from constants import card_emotes, blank_card_emoji


class Card:
    def __init__(self, suit: str, name: str):
        self.suit = suit
        self.name = name
        self.emote = card_emotes[self.suit].get(self.name)


class Player:
    def __init__(self, user_id: int, bet_amount: int, game, is_dealer=False):
        self.user_id = user_id
        self.bet_amount = int(bet_amount)
        self.cards: List[Card] = []
        self.game = game
        self.stay = False
        self.is_dealer = is_dealer
        self.card_value = 0

    def calculate_card_value(self) -> int:
        value = 0
        aces = 0
        for card in self.cards:
            if card.name == "A":
                aces += 1
            elif card.name in ("K", "Q", "J"):
                value += 10
            else:
                value += int(card.name)

        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1

        self.card_value = value
        return value

    def get_emote_string(self, hidden=True) -> str:
        if self.is_dealer and hidden:
            return f"{self.cards[0].emote} {blank_card_emoji}\nValue: ?"

        emote_str = " ".join(card.emote for card in self.cards)
        return f"{emote_str}\nValue: **{self.calculate_card_value()}**"


class Deck:
    suits = ("club", "heart", "diamond", "spade")
    cards_set = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "K", "Q", "J")

    def __init__(self):
        self.cards = [Card(suit, card) for suit in self.suits for card in self.cards_set]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop() if self.cards else None


class Game:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.participants = {}
        self.deck = Deck()
        self.dealer = Player(0, 0, self, is_dealer=True)
