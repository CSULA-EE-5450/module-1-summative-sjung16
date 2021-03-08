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

Todo:
- print player stack
- print community stack
- calculate winner
    - _get_best_hand for each player (store into self_player_best_hand)
    - 
- run
- main
    - Remember that player stacks should be private.
    - For now, make it public, but later make it private with FastAPI