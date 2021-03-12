from uuid import uuid4
from typing import List, Tuple, Dict, Union
from poker.poker import Poker
import asyncio
from user_db import UserDB
from dataclasses import dataclass


@dataclass
class PokerGameInfo:
    num_players: int
    players: List[str]
    termination_password: str


class AsyncPokerGameDB(object):
    def __init__(self, user_db: UserDB):
        self._current_games: Dict[str, Poker] = {}
        self._current_games_info: Dict[str, PokerGameInfo] = {}
        self._QUERY_TIME: float = 0.05
        self._user_db = user_db

    async def add_game(self, num_players: int, starting_cash: int = 1000) -> Tuple[str, str]:
        """
        Asks the database to create a new game.

        :param num_players: number of players
        :param starting_cash: amount of money each player starts with
        :return: the UUID (universally-unique ID) of the game
        """
        await asyncio.sleep(self._QUERY_TIME)  # simulate query time
        game_uuid = str(uuid4())
        game_term_password = str(uuid4())
        self._current_games[game_uuid] = Poker(num_players, starting_cash)
        self._current_games_info[game_uuid] = PokerGameInfo(
            num_players,
            list(),
            game_term_password)
        return game_uuid, game_term_password

    async def list_games(self) -> List[Tuple[str, int]]:
        """
        Asks the database for a list of all active games.

        :return: list of (game_id, number of players in game)
        """
        await asyncio.sleep(self._QUERY_TIME)  # simulate query time
        return [(game_id, game._num_players) for game_id, game in self._current_games.items()]

    async def get_game(self, game_id: str) -> Union[Poker, None]:
        """
        Asks the database for a pointer to a specific game.

        :param game_id: the UUID of the specific game
        :return: None if the game was not found, otherwise pointer to the Poker object
        """
        await asyncio.sleep(self._QUERY_TIME)  # simulate query time
        return self._current_games.get(game_id, None)

    async def get_game_info(self, game_id: str):
        """
        Asks the database for num_players, list of players, and termination password for a specific game.

        :param game_id: the UUID of the specific game
        :return: list of players in the game game_id
        """
        return self._current_games_info[game_id]
