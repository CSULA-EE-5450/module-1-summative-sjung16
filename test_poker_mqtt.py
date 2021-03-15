import asyncio
import pytest
import poker_mqtt
from asyncio_mqtt import Client, MqttError


@pytest.mark.asyncio
async def test_create_game():
    async with Client("localhost") as client:
        await client.subscribe("#")
        message1 = "2, 3, 5000"
        message_split = message1.split(", ")
        game_room = message_split[0]
        await poker_mqtt.create_game(client, message1)
        async with client.filtered_messages("game_room/" + str(game_room) + "/create_success") as messages:
            async for message_mqtt in messages:
                message = message_mqtt.payload.decode()
        assert message == "True"


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
