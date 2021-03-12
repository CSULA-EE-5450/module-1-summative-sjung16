from typing import List, Tuple, Dict, Union
from poker.poker import Poker
import asyncio
from user_db import UserDB
from dataclasses import dataclass


@dataclass
class PokerGameInfo:
    room_number: str
    num_players: int
    starting_cash: int
    players: List[str]


class AsyncPokerGameDB(object):
    def __init__(self, user_db: UserDB):
        self._current_games: Dict[str, Poker] = {}
        self._current_games_info: Dict[str, PokerGameInfo] = {}
        self._QUERY_TIME: float = 0.05
        self._user_db = user_db

    async def add_game(self, room_number: str, num_players: int, starting_cash: int = 1000) -> str:
        """
        Asks the database to create a new game.

        :param room_number: room number
        :param num_players: number of players
        :param starting_cash: amount of money each player starts with
        :return: the room number of the game
        """
        if room_number in self._current_games_info:
            raise KeyError('That room number is taken.')
        await asyncio.sleep(self._QUERY_TIME)  # simulate query time
        self._current_games[room_number] = Poker(num_players, starting_cash)
        self._current_games_info[room_number] = PokerGameInfo(
            room_number,
            num_players,
            starting_cash,
            list(),
            )
        return room_number

    # async def list_games(self) -> List[Tuple[str, int]]:
    #     """
    #     Asks the database for a list of all active games.
    #
    #     :return: list of (game_id, number of players in game)
    #     """
    #     await asyncio.sleep(self._QUERY_TIME)  # simulate query time
    #     return [(game_id, game._num_players) for game_id, game in self._current_games.items()]

    async def get_game(self, room_number: str) -> Union[Poker, None]:
        """
        Asks the database for a pointer to a specific game.

        :param room_number: the room number
        :return: None if the game was not found, otherwise pointer to the Poker object
        """
        await asyncio.sleep(self._QUERY_TIME)  # simulate query time
        return self._current_games.get(room_number, None)

    async def get_game_info(self, room_number: str):
        """
        Asks the database for num_players, list of players, and termination password for a specific game.

        :param room_number: the room number of the specific game
        :return: list of players in the game game_id
        """
        return self._current_games_info[room_number]
