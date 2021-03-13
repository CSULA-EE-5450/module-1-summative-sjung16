from unittest import TestCase, mock
from poker import Poker, Card


class TestPoker(TestCase):
    def setUp(self) -> None:
        """
        Sample game and hands with 3 players
        """
        self.poker = Poker(num_players=3, starting_cash=1000)
        self.poker._community_stack = [Card('S', 13), Card('H', 12), Card('H', 10), Card('H', 9), Card('S', 6)]
        self.poker._player_stacks = [[Card('S', 13), Card('S', 13)],    # Player 0: Three of a Kind
                                     [Card('S', 13), Card('D', 12)],    # Player 1: Two Pair
                                     [Card('H', 5), Card('H', 8)]]      # Player 2: Flush

    def test__calculate_score(self):
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('S', 13), Card('S', 12),
                                                      Card('S', 11), Card('S', 10)]), ('Royal Flush', 135))
        self.assertEqual(self.poker._calculate_score([Card('S', 13), Card('S', 12), Card('S', 11),
                                                      Card('S', 10), Card('S', 9)]), ('Straight Flush', 133))
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('S', 14), Card('S', 14),
                                                      Card('S', 14), Card('S', 10)]), ('Four of a Kind', 119.10))
        self.assertEqual(self.poker._calculate_score([Card('S', 10), Card('S', 10), Card('S', 10),
                                                      Card('S', 12), Card('S', 12)]), ('Full House', 100.12))
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('S', 5), Card('S', 4),
                                                      Card('S', 8), Card('S', 10)]), ('Flush', 75.14))
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 14), Card('H', 14),
                                                      Card('S', 11), Card('C', 9)]), ('Three of a Kind', 59.1109))
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 14), Card('H', 13),
                                                      Card('S', 13), Card('C', 9)]), ('Two Pair', 44.1309))
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 14), Card('H', 13),
                                                      Card('S', 5), Card('C', 3)]), ('Pair', 29.130503))
        self.assertEqual(self.poker._calculate_score([Card('S', 10), Card('D', 9), Card('H', 8),
                                                      Card('S', 7), Card('C', 6)]), ('Straight', 75))
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 12), Card('H', 10),
                                                      Card('S', 6), Card('C', 2)]), ('High Card', 14.12100602))

    def test__create_stack(self):
        self.assertEqual(len(self.poker._create_stack()), 52)

    def test__draw_card(self):
        drawn_card = self.poker._draw_card()
        self.assertLess(drawn_card.number, 15)
        self.assertGreater(drawn_card.number, 0)

    def test__player_draw(self):
        self.assertEqual(self.poker._player_draw(0), self.poker._player_stacks[0][-1])

    def test__combinations(self):
        self.assertEqual(len(self.poker._combinations([Card('S', 2), Card('D', 2), Card('H', 2),
                                                       Card('C', 2), Card('S', 3), Card('S', 4),
                                                       Card('S', 5)], 5)), 21)  # 7 Choose 5 = 21

    def test__get_best_hand(self):
        combinations = self.poker._combinations([Card('S', 13), Card('D', 13), Card('H', 13),
                                                Card('C', 2), Card('S', 3), Card('S', 12),
                                                Card('S', 13)], 5)
        # Best hand should be Four of a Kind of Kings (13) with remaining card Queen (12)
        best_hand = {'hand': (Card('S', 13), Card('D', 13), Card('H', 13), Card('S', 13), Card('S', 12)),
                     'hand type': 'Four of a Kind',
                     'score': 118.12}
        # Wanted to assertDictEqual, but the order of dict elements matters; compared score only instead:
        self.assertEqual(self.poker._get_best_hand(combinations)['score'], best_hand['score'])

    def test__compute_winner(self):
        """
        From setUp:
        self.poker._community_stack = [Card('S', 13), Card('H', 12), Card('H', 10), Card('H', 9), Card('S', 6)]
        self.poker._player_stacks = [[Card('S', 13), Card('S', 13)],    # Player 0: Three of a Kind
                                     [Card('S', 13), Card('D', 12)],    # Player 1: Two Pair
                                     [Card('H', 5), Card('H', 8)]]      # Player 2: Flush
        """
        self.assertEqual(self.poker.compute_winner(), 2)   # Player 2 should win with his Flush
