from unittest import TestCase, mock
from poker import Poker, Card


class TestPoker(TestCase):
    def setUp(self) -> None:
        self.poker = Poker()

    def test__combinations(self):
        self.assertEqual(len(self.poker._combinations([Card('S', 2), Card('D', 2), Card('H', 2),
                                                       Card('C', 2), Card('S', 3), Card('S', 4),
                                                       Card('S', 5)], 5)), 21)  # 7 choose 5

    def test__get_best_hand(self):
        combinations = self.poker._combinations([Card('S', 13), Card('D', 13), Card('H', 13),
                                                Card('C', 2), Card('S', 3), Card('S', 12),
                                                Card('S', 13)], 5)
        # Best hand should be Four of a Kind of Kings (13) with remaining card Queen (12)
        self.assertEqual(self.poker._get_best_hand(combinations),
                         {'hand': (Card(suit='S', number=13), Card(suit='D', number=13), Card(suit='H', number=13),
                                   Card(suit='S', number=12), Card(suit='S', number=13)), 'score': 118.12})

    def test__calculate_score(self):
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('S', 13), Card('S', 12),
                                                      Card('S', 11), Card('S', 10)]), 135)          # Royal Flush
        self.assertEqual(self.poker._calculate_score([Card('S', 13), Card('S', 12), Card('S', 11),
                                                      Card('S', 10), Card('S', 9)]), 133)           # Straight Flush
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('S', 14), Card('S', 14),
                                                      Card('S', 14), Card('S', 10)]), 119.10)       # Four of a Kind
        self.assertEqual(self.poker._calculate_score([Card('S', 10), Card('S', 10), Card('S', 10),
                                                      Card('S', 12), Card('S', 12)]), 100.12)       # Full House
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('S', 5), Card('S', 4),
                                                      Card('S', 8), Card('S', 10)]), 75.14)         # Flush
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 14), Card('H', 14),
                                                      Card('S', 11), Card('C', 9)]), 59.1109)       # Three of a Kind
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 14), Card('H', 13),
                                                      Card('S', 13), Card('C', 9)]), 44.1309)       # Two Pair
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 14), Card('H', 13),
                                                      Card('S', 5), Card('C', 3)]), 29.130503)      # Pair
        self.assertEqual(self.poker._calculate_score([Card('S', 10), Card('D', 9), Card('H', 8),
                                                      Card('S', 7), Card('C', 6)]), 75)             # Straight
        self.assertEqual(self.poker._calculate_score([Card('S', 14), Card('D', 12), Card('H', 10),
                                                      Card('S', 6), Card('C', 2)]), 14.12100602)    # High Card

    def test__create_stack(self):
        self.assertEqual(len(self.poker._create_stack()), 52)

    def test__draw_card(self):
        drawn_card = self.poker._draw_card()
        self.assertLess(drawn_card.number, 15)
        self.assertGreater(drawn_card.number, 0)

    def test__player_draw(self):
        self.assertEqual(self.poker._player_draw(0), self.poker._player_stacks[0][-1])


