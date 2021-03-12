from poker_db import AsyncPokerGameDB
from user_db import UserDB
import pytest

TEST_USER = 'tester'


@pytest.fixture
def base_user_db():
    the_user_db = UserDB()
    username, passtoken = the_user_db.create_user(TEST_USER)
    return the_user_db, username, passtoken


@pytest.fixture
def base_game_db(base_user_db):
    return AsyncPokerGameDB(base_user_db[0])


@pytest.mark.asyncio
async def test_add_game(base_game_db):
    game_uuid, game_term_password = await base_game_db.add_game(1, 2)
    assert len(game_uuid) == 36
    assert len(game_term_password) == 36
    assert base_game_db._current_games_info[game_uuid].termination_password == game_term_password
    assert base_game_db._current_games[game_uuid]._num_players == 1


@pytest.fixture
async def single_game_db(base_game_db):
    game_uuid, game_term_password = await base_game_db.add_game(1, 2)
    return base_game_db, game_uuid, game_term_password


@pytest.mark.asyncio
async def test_list_games(single_game_db):
    list_of_games = await single_game_db[0].list_games()
    assert len(list_of_games) == 1


@pytest.mark.asyncio
async def test_get_game(single_game_db):
    assert await single_game_db[0].get_game(single_game_db[1]) is not None
    assert await single_game_db[0].get_game(single_game_db[1]) == single_game_db[0]._current_games[single_game_db[1]]


if __name__ == '__main__':
    pytest.main()
