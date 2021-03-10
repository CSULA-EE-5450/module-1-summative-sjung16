# Welcome to Texas Hold'em!
Texas Hold'em is a popular variant of Poker. The game requires at least two players. The rules of the game are outside 
the scope of this project, and it will be assumed that you already know how the game works.

## Scoring
The score will be calculated to the following metrics:

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

The range of scores for each hand type helps distinguish the winner. For example, a hand with a high card of 13 (King)
will beat a hand with a high card of 11 (Jack). To further distinguish the scores between similar hands with differing
remainder cards, decimal points will be given for the remaining cards (each subsequent card weighing less and less to 
the overall score).

## Betting
The betting system will be a simplified version of a normal betting system. After the initial deal Player 0 can:
- Bet: If Player 0 chooses Bet, the rest of the players will automatically call the bet amount.
- Check: If Player 0 chooses Check, the rest of the players will also check.

Essentially, Player 0 is the main player of the game and everyone else must follow suit. I wanted to implement the real
betting system, but it was a bit too complex for the scope of this project. I may try to implement it in the future.