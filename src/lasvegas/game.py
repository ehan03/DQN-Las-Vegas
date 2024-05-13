# standard library imports
from collections import Counter
from random import randint, shuffle

# third party imports

# local imports


class LasVegas:
    """
    Class for the Las Vegas dice game
    """

    MAX_PLAYERS = 5
    NUM_DICE = 8
    NUM_ROUNDS = 4

    # Number of bills for each bill value (divided by 1000) in the game
    # There should be a total of 54 bills in the game
    BILL_COUNTS = {
        10: 6,
        20: 8,
        30: 8,
        40: 6,
        50: 6,
        60: 5,
        70: 5,
        80: 5,
        90: 5,
    }
    CASH_NORM = 100

    def __init__(self, num_players):
        """
        Initialize the game
        """

        assert 2 <= num_players <= self.MAX_PLAYERS, "Invalid number of players"

        self.num_players = num_players
        self.players = [
            (
                {"cash": 0, "dice": self.NUM_DICE}
                if i < num_players
                else {"cash": 0, "dice": 0}
            )
            for i in range(self.MAX_PLAYERS)
        ]
        self.deck = [
            bill for bill, count in self.BILL_COUNTS.items() for _ in range(count)
        ]
        shuffle(self.deck)
        self.casinos = self.deal_bills()
        self.first_player = 0
        self.round = 1

    def deal_bills(self):
        """
        Deal bills to casinos
        """

        bills = [[] for _ in range(6)]
        for i in range(6):
            while sum(bills[i]) < 50:
                bills[i].append(self.deck.pop())
            while len(bills[i]) < 5:
                bills[i].append(0)
            bills[i].sort(reverse=True)

        casinos = [
            {"bills": bills[i], "dice": [0] * self.MAX_PLAYERS} for i in range(6)
        ]

        return casinos

    def roll_dice(self, player):
        """
        Roll dice for a player given index
        """

        roll = [randint(1, 6) for _ in range(self.players[player]["dice"])]
        roll_counts = [roll.count(i + 1) for i in range(6)]  # index 0 is for 1

        return roll_counts

    def play_move(self, player, action, roll_counts):
        """
        Make a move for a player given index, action, and dice counts
        """

        assert 0 <= player < self.num_players, "Invalid player"
        assert 0 <= action < 6, "Invalid casino"
        assert roll_counts[action] > 0, "No dice to play"

        self.players[player]["dice"] -= roll_counts[action]
        self.casinos[action]["dice"][player] += roll_counts[action]

    def is_end_round(self):
        """
        Check if the round is over
        """

        is_end_round = all(
            self.players[i]["dice"] == 0 for i in range(self.num_players)
        )

        return is_end_round

    def is_end_game(self):
        """
        Check if the game is over
        """

        is_end_game = (self.round == self.NUM_ROUNDS) and self.is_end_round()

        return is_end_game

    def advance_round(self):
        """
        Start the next round
        """

        assert self.is_end_round(), "Round is not over"

        for casino in self.casinos:
            counts = Counter(casino["dice"])
            ranked = sorted(enumerate(casino["dice"]), key=lambda x: x[1])

            while len(ranked) > 0:
                player, count = ranked.pop()

                if counts[count] == 1 and casino["bills"]:
                    self.players[player]["cash"] += casino["bills"].pop(0)

            for bill in casino["bills"]:
                if bill:
                    self.deck.append(bill)

        if self.round < self.NUM_ROUNDS:
            shuffle(self.deck)
            self.casinos = self.deal_bills()
            for i in range(self.num_players):
                self.players[i]["dice"] = self.NUM_DICE
            self.first_player = (self.first_player + 1) % self.num_players
            self.round += 1

    def get_game_state(self, player, roll_counts):
        """
        Get the current game state
        """

        vec = []

        vec.append(self.num_players / self.MAX_PLAYERS)
        vec.append(self.round / self.NUM_ROUNDS)

        order = (
            player - self.first_player
            if player >= self.first_player
            else self.num_players - self.first_player + player
        )
        vec.append(order / self.num_players)

        cash = [player["cash"] for player in self.players]
        cash_shifted = cash[player:] + cash[:player]
        vec.extend(c / self.CASH_NORM for c in cash_shifted)

        for casino in self.casinos:
            dice = casino["dice"]
            dice_shifted = dice[player:] + dice[:player]
            vec.extend(d / self.NUM_DICE for d in dice_shifted)

            bills = casino["bills"]
            bills_shifted = bills[player:] + bills[:player]
            vec.extend(b / max(self.BILL_COUNTS.keys()) for b in bills_shifted)

        vec.extend(r / self.NUM_DICE for r in roll_counts)

        return vec
