# Welcome to Texas Hold'em!
Texas Hold'em is a popular variant of Poker. The game requires at least two players.

[How to play Texas Hold'em](https://bicyclecards.com/how-to-play/texas-holdem-poker/)

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
The betting system will be a simplified version of a normal betting system. After the initial deal, Player 0 can:
- `Bet`: If Player 0 chooses `Bet`, the rest of the players will automatically `Call` the bet amount, and then the game 
  will continue on to the next stage.
- `Check`: If Player 0 chooses `Check`, the turn will go to the next player, Player 1. Player 1 will have the same 
  choices of either `Bet` or `Check`, just as Player 0 did. The turns will continue in this fashion until either one of 
  the players `Bet`s or everyone `Check`s. Then, the game will continue on to the next stage.
