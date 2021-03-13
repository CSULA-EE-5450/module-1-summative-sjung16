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
    room_number = await base_game_db.add_game('1', 2, 1000)
    assert base_game_db._current_games[room_number]._num_players == 2


if __name__ == '__main__':
    pytest.main()
