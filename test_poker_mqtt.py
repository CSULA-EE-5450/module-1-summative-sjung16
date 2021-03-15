import asyncio
import pytest
import poker_mqtt
from asyncio_mqtt import Client, MqttError


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def create_sample_game():
    async with Client("localhost") as client:
        await poker_mqtt.create_game(client, "2, 3, 5000", test=True)


@pytest.mark.asyncio
async def test_create_game():
    async with Client("localhost") as client:
        test_message = "2,3,5000"
        test_response = await poker_mqtt.create_game(client, test_message, test=True)
        assert test_response == ("game_rooms/2/num_players=3",
                                 "game_rooms/2/starting_cash=$5000",
                                 "game_rooms/2/players")


@pytest.mark.asyncio
async def test_create_user():
    async with Client("localhost") as client:
        test_message = "player1"
        test_response = await poker_mqtt.create_user(client, test_message, test=True)
        assert test_response == "users/player1/create_success=True"


@pytest.mark.asyncio
async def test_add_player_to_game():
    async with Client("localhost") as client:
        await create_sample_game()
        test_message = "2,player1"
        test_response = await poker_mqtt.add_player_to_game(client, test_message, test=True)
        assert test_response == "game_rooms/2/players/player1=player_idx: 0"


# @pytest.mark.asyncio
# async def bet():
#     async with Client("localhost") as client:
#         await create_sample_game()
#         test_message = "bet 2,felix,200"
#         test_response = await poker_mqtt.get_game(client, test_message, test=True)
#         assert test_response == "game_rooms/2/players/player1=player_idx: 0"
