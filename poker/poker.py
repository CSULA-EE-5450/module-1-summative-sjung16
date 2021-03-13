from typing import List, Tuple, Dict
import random
from dataclasses import dataclass
import itertools

POKER_INSTRUCTIONS = {
    'English': {
        'WELCOME': "Welcome to Texas Hold'em! ",
        'NUM_PLAYERS': 'How many players? ',
        'START': 'Starting game... ',
        'PLAYER_CHOICE': 'Type b to bet, or k to check: ',
        'PLAYER_BET_AMT': 'Type amount to bet: ',
        'PLAY_AGAIN': 'Type y to play another game: '
    }
}


@dataclass
class Card(object):
    suit: str
    number: int

    @staticmethod
    def _convert_card_num_to_str(num) -> str:
        if num == 11:
            return 'Jack'
        elif num == 12:
            return 'Queen'
        elif num == 13:
            return 'King'
        elif num == 14:
            return 'Ace'
        else:
            return str(num)

    def __str__(self):
        return f'{self._convert_card_num_to_str(self.number)} of {self.suit}'


class Poker(object):
    """
    Poker game object.
    """
    def __init__(self, num_players: int = 2, starting_cash: int = 1000):
        """
        Constructor for the poker game object.

        :param num_players: number of players in this game; defaults to 2 players
        :param starting_cash: amount of cash each player starts with
        """
        self._SUITS = ("S", "H", "C", "D")
        self._NUMBERS = list(range(2, 15))
        self._num_players = num_players
        self._card_stack = self._create_stack()
        self._player_stacks = [[] for _ in range(self._num_players)]
        self._community_stack = []
        self._best_hands = {}
        self._player_cash = [starting_cash for _ in range(self._num_players)]
        self.the_pot = 0
        self._bet_amount = 0
        self._player_dones = [False for _ in range(self._num_players)]

    @staticmethod
    def _score_four_of_a_kind(numbers) -> float:
        """
        Takes a hand of a Four of a Kind and calculates its score.

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        for i in numbers:
            if numbers.count(i) == 4:
                repeat_four = i     # i = the number that repeats 4 times
            elif numbers.count(i) == 1:
                remaining_card = i  # i = the one remaining number
        return 105 + repeat_four + remaining_card / 100

    @staticmethod
    def _score_full_house(numbers) -> float:
        """
        Takes a hand of a Full House and calculates its score.

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        for i in numbers:
            if numbers.count(i) == 3:
                repeat_three = i    # i = the number that repeats 3 times
            elif numbers.count(i) == 2:
                repeat_two = i      # i = the number that repeats 2 times
        return 90 + repeat_three + repeat_two / 100

    @staticmethod
    def _score_flush(numbers) -> float:
        """
        Takes a hand of a Flush and calculates its score

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        return 75 + max(numbers) / 100

    @staticmethod
    def _score_straight(numbers) -> float:
        """
        Takes a hand of a Straight and calculates its score

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        return 65 + max(numbers)

    @staticmethod
    def _score_three_of_a_kind(numbers) -> float:
        """
        Takes a hand of a Three of a Kind and calculates its score.

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        remaining_cards = []
        for i in numbers:
            if numbers.count(i) == 3:
                repeat_three = i    # i = the number that repeats 3 times
            else:
                remaining_cards.append(i)   # remaining two cards only
        return round((45 + repeat_three + max(remaining_cards)/100 + min(remaining_cards) / 10000), 4)

    @staticmethod
    def _score_two_pair(numbers) -> float:
        """
        Takes a hand of a Two Pair and calculates its score.

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        pairs = []
        remaining_cards = []
        for i in numbers:
            if numbers.count(i) == 2:
                pairs.append(i)     # i = the number that repeats once
            elif numbers.count(i) == 1:
                remaining_cards.append(i)   # remaining one card only
        return round(30 + max(pairs) + min(pairs) / 100 + remaining_cards[0] / 10000, 4)

    @staticmethod
    def _score_pair(numbers) -> float:
        """
        Takes a hand of a Pair and calculates its score.

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        pair = []
        remaining_cards = []
        for i in numbers:
            if numbers.count(i) == 2:
                pair.append(i)  # i = the number that repeats once
            elif numbers.count(i) == 1:
                remaining_cards.append(i)  # remaining three cards only
                remaining_cards = sorted(remaining_cards, reverse=True)
        return round(15 + pair[0] + remaining_cards[0] / 100 +
                     remaining_cards[1] / 10000 + remaining_cards[2] / 1000000, 6)

    @staticmethod
    def _score_high_card(numbers) -> float:
        """
        Takes a hand of a High Card and calculates its score

        :param numbers: List of only the numbers of a hand of 5 cards
        :return: The score
        """
        n = sorted(numbers, reverse=True)
        return round((n[0] + n[1] / 100 + n[2] / 10000 + n[3] / 1000000 + n[4] / 100000000), 8)

    def _calculate_score(self, stack: List[Card]) -> Tuple[str, float]:
        """
        Calculates the score of a given hand according to the following metrics:
        (Decimal points are given for remainder cards)

            | Hand Type        | Score      |
            | ---------------- | ---------- |
            | High Card        | 0 to 14    |
            | Pair             | 15 to 29   |
            | Two Pair         | 30 to 44   |
            | Three of a Kind  | 45 to 59   |
            | Straight         | 60 to 74   |
            | Flush            | 75 to 89   |
            | Full House       | 90 to 104  |
            | Four of a Kind   | 105 to 119 |
            | Straight Flush   | 120 to 134 |
            | Royal Flush      | 135        |

        :param stack: The 5 card hand
        :return: The score of the hand
        """
        suits = [stack[i].suit for i in range(5)]           # List of suits for each card in the hand
        numbers = [stack[i].number for i in range(5)]       # List of numbers for each card in the hand
        repeated_num = [numbers.count(i) for i in numbers]  # Repetitions for each number
        repeated_suit = [suits.count(i) for i in suits]     # Repetitions for each suit
        diff = max(numbers) - min(numbers)
        if 5 in repeated_suit:
            # Checks if the flush hand has something higher than a flush as well. If it doesn't, it's a flush.
            if numbers == [14, 13, 12, 11, 10]:
                hand_type = 'Royal Flush'
                score = 135
            elif diff == 4 and max(repeated_num) == 1:
                hand_type = 'Straight Flush'
                score = 120 + max(numbers)
            elif 4 in repeated_num:
                hand_type = 'Four of a Kind'
                score = self._score_four_of_a_kind(numbers)
            elif sorted(repeated_num) == [2, 2, 3, 3, 3]:
                hand_type = 'Full House'
                score = self._score_full_house(numbers)
            else:
                hand_type = 'Flush'
                score = self._score_flush(numbers)
        elif 4 in repeated_num:
            hand_type = 'Four of a Kind'
            score = self._score_four_of_a_kind(numbers)
        elif sorted(repeated_num) == [2, 2, 3, 3, 3]:
            hand_type = 'Full House'
            score = self._score_full_house(numbers)
        elif 3 in repeated_num:
            hand_type = 'Three of a Kind'
            score = self._score_three_of_a_kind(numbers)
        elif repeated_num.count(2) == 4:
            hand_type = 'Two Pair'
            score = self._score_two_pair(numbers)
        elif repeated_num.count(2) == 2:
            hand_type = 'Pair'
            score = self._score_pair(numbers)
        elif diff == 4:
            hand_type = 'Straight'
            score = self._score_straight(numbers)
        else:
            hand_type = 'High Card'
            score = self._score_high_card(numbers)
        return hand_type, score

    def _create_stack(self) -> List[Card]:
        """
        Creates the stack of the cards (52 * num_decks), shuffled.

        :return: stack of all card objects, shuffled.
        """
        stack = []
        for suit in self._SUITS:
            stack.extend([Card(suit, num) for num in self._NUMBERS])
        random.shuffle(stack)
        return stack

    def _draw_card(self) -> Card:
        """
        Draw a card from the main stack.

        :return: Card object
        """
        return self._card_stack.pop()

    def _player_draw(self, player_idx: int) -> Card:
        """
        Draw a card for the player.

        :param player_idx: The player to which a card should be drawn
        :return: The drawn card (already placed in the player's stacks)
        """
        drawn_card = self._draw_card()
        self._player_stacks[player_idx].append(drawn_card)
        return drawn_card

    def community_draw(self) -> Card:
        """
        Draw a community card and adds it to the community card stack.

        :return: The drawn card (already placed in the community card stack)
        """
        drawn_card = self._draw_card()
        self._community_stack.append(drawn_card)
        return drawn_card

    def initial_deal(self):
        """
        Draws two cards per player.
        """
        for player_idx in range(self._num_players):
            for _ in range(2):
                self._player_draw(player_idx)

    def _print_player_stack(self, player_idx: int):
        """
        Prints player_idx's stack.
        :param player_idx: Player index
        """
        player_stack = self._player_stacks[player_idx]
        print(f"Player {player_idx}: {', '.join([str(card) for card in player_stack])}")

    def _print_community_stack(self):
        """
        Prints the current community stack.
        """
        community_stack = self._community_stack
        print(f"Community cards: {', '.join([str(card) for card in community_stack])}")

    def get_player_stacks(self):
        return self._player_stacks

    def get_community_stack(self):
        return self._community_stack

    def get_player_cash(self):
        return self._player_cash

    def get_the_pot(self):
        return self.the_pot

    def get_best_hands(self):
        return self._best_hands

    def _print_cash_standing(self, num_players: int):
        """
        Prints every player's cash standing
        """
        for player_idx in range(num_players):
            print(f"Player {player_idx} has ${self._player_cash[player_idx]}. ")

    @staticmethod
    def _combinations(stack: List[Card], length: int):
        """
        Lists all combinations of the specified length from the stack (for Texas Hold'em, use 7 Choose 5).

        :param stack: The player's stack plus the community stack
        :param length: Length of the combination
        :return: The list of all combinations of specified length
        """
        combination_list = list(itertools.combinations(stack, length))
        return combination_list

    def _get_best_hand(self, combinations) -> Dict[str, float]:
        """
        Takes in a list of combinations of cards, ranks them according to their score, and returns the best hand.

        :param combinations: List of combinations of cards
        :return: The best hand out of all the combinations
        """
        hands = [{'hand': i,
                  'hand type': self._calculate_score(i)[0],
                  'score': self._calculate_score(i)[1]}
                 for i in combinations]
        ranked_hands = sorted(hands, key=lambda k: k['score'], reverse=True)  # Rank hands by value, descending
        best_hand = ranked_hands[0]
        return best_hand

    def compute_winner(self) -> int:
        """
        Creates a nested dictionary of each player and their best hand (along with their hand type and score), and
        returns the winning player's index number.

        player_best_hands = {player 1: {'hand': hand 1, 'hand type': hand type 1, 'score': score 1},
                             player 2: {'hand': hand 2, 'hand type': hand type 2, 'score': score 2}, ...}

        :return: The winning player
        """
        for player_idx in range(self._num_players):
            seven_card_combination = self._player_stacks[player_idx] + self._community_stack
            five_card_combinations = self._combinations(seven_card_combination, 5)
            self._best_hands[player_idx] = self._get_best_hand(five_card_combinations)
        # Get the winning player's index from the nested dictionary, according to 'score':
        winning_player_idx = max(self._best_hands, key=lambda x: self._best_hands[x].get('score'))
        return winning_player_idx

    def _player_choice(self, player_idx: int):
        """
        Asks the player for the choice.

        :param player_idx: Player index
        """
        player_input = 'g'
        while player_input not in ('b', 'k'):
            player_input = input(f"Player {player_idx}: {POKER_INSTRUCTIONS['English']['PLAYER_CHOICE']} ")
            if player_input == 'b':
                self._bet_amount = int(input(f"Player {player_idx}: "
                                             f"{POKER_INSTRUCTIONS['English']['PLAYER_BET_AMT']} "))
                self._player_cash[player_idx] -= self._bet_amount
                self.the_pot += self._bet_amount
                print(f"Player {player_idx} bets for ${self._bet_amount}. Pot: ${self._the_pot}. "
                      f"Player {player_idx} now has ${self._player_cash[player_idx]} ")
                # Automatically 'Call' for everyone but player_idx
                for idx in range(self._num_players):
                    if idx == player_idx:
                        continue
                    else:
                        self._player_cash[idx] -= self._bet_amount
                        self.the_pot += self._bet_amount
                        print(f"Player {idx} has called. Pot: ${self.the_pot}. "
                              f"Player {idx} now has ${self._player_cash[idx]}. ")
                return 'bet'
            elif player_input == 'k':
                print(f"Player {player_idx} checks. Pot: ${self.the_pot}. ")
                return 'check'

    def run(self):
        print(POKER_INSTRUCTIONS['English']['START'])
        self._print_cash_standing(self._num_players)

        """ ************************** INITIAL DEAL ************************** """

        self.initial_deal()
        for player_idx in range(self._num_players):
            self._print_player_stack(player_idx)
        while not all(self._player_dones):                          # While not everyone is done
            for player_idx in range(self._num_players):             # For each player
                if not self._player_dones[player_idx]:              # If player_idx is not done
                    if self._player_choice(player_idx) == 'bet':    # If player_idx's choice is bet
                        self._player_dones[player_idx] = True       # player_idx is done
                        break                                       # Break the loop and go to next stage of game
                    else:
                        self._player_dones[player_idx] = True
                        continue
            break
        self._player_dones = [False for _ in range(self._num_players)]

        """ **************************** THE FLOP **************************** """

        for i in range(3):
            self.community_draw()
        self._print_community_stack()
        while not all(self._player_dones):                          # While not everyone is done
            for player_idx in range(self._num_players):             # For each player
                if not self._player_dones[player_idx]:              # If player_idx is not done
                    if self._player_choice(player_idx) == 'bet':    # If player_idx's choice is bet
                        self._player_dones[player_idx] = True       # player_idx is done
                        break                                       # Break the loop and go to next stage of game
                    else:   # If player_idx's choice is 'Check'
                        self._player_dones[player_idx] = True
                        continue
            break
        self._player_dones = [False for _ in range(self._num_players)]

        """ **************************** THE TURN **************************** """

        self.community_draw()
        self._print_community_stack()   # The Turn
        while not all(self._player_dones):                          # While not everyone is done
            for player_idx in range(self._num_players):             # For each player
                if not self._player_dones[player_idx]:              # If player_idx is not done
                    if self._player_choice(player_idx) == 'bet':    # If player_idx's choice is bet
                        self._player_dones[player_idx] = True       # player_idx is done
                        break                                       # Break the loop and go to next stage of game
                    else:   # If player_idx's choice is 'Check'
                        self._player_dones[player_idx] = True
                        continue
            break
        self._player_dones = [False for _ in range(self._num_players)]

        """ *************************** THE RIVER *************************** """

        self.community_draw()
        self._print_community_stack()
        while not all(self._player_dones):                          # While not everyone is done
            for player_idx in range(self._num_players):             # For each player
                if not self._player_dones[player_idx]:              # If player_idx is not done
                    if self._player_choice(player_idx) == 'bet':    # If player_idx's choice is bet
                        self._player_dones[player_idx] = True       # player_idx is done
                        break                                       # Break the loop and go to next stage of game
                    else:   # If player_idx's choice is 'Check'
                        self._player_dones[player_idx] = True
                        continue
            break
        # Winner computation:
        winner_player_idx = self.compute_winner()
        self._player_cash[winner_player_idx] += self.the_pot
        print(f"Player {winner_player_idx} wins ${self.the_pot}, "
              f"with a {self._best_hands[winner_player_idx]['hand type']}! "
              f"(score: {self._best_hands[winner_player_idx]['score']}) ")
        self._print_cash_standing(self._num_players)
        return


def main():
    play_another = True
    while play_another:
        print(f"{POKER_INSTRUCTIONS['English']['WELCOME']}")
        num_players_input = int(input(f"{POKER_INSTRUCTIONS['English']['NUM_PLAYERS']}"))
        the_game = Poker(num_players_input)
        the_game.run()
        play_another_input = input(f"{POKER_INSTRUCTIONS['English']['PLAY_AGAIN']}")
        if play_another_input != 'y':
            play_another = False
    return False


if __name__ == '__main__':
    main()
