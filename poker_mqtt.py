import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
from poker_db import AsyncPokerGameDB

POKER_DB = AsyncPokerGameDB()

game_uuid = 15


async def create_game():
    async with Client("localhost") as client:
        # Receive messages that match the given filter and store as messages
        async with client.filtered_messages("game/create") as messages:
            await client.subscribe("game/create")
            # For every message received under this filter, create a game room corresponding to the entered number
            async for message in messages:
                message_str = message.payload.decode()
                await client.publish(("game_room/" + str(message_str)) + "/create_success", "True", qos=1)
                await client.publish(("game_room/" + str(message_str)) + "/num_players", 2, qos=1)
                await client.publish(("game_room/" + str(message_str)) + "/starting_cash", 1000, qos=1)
                await POKER_DB.add_game()


async def input_num_players():
    async with Client("localhost") as client:
        async with client.filtered_messages("game_room/+/num_players") as messages:
            await client.subscribe("game_room/+/num_players")
            async for message in messages:
                message_str = message.payload.decode()
                await client.publish("game_room/+/players", str(message_str) + 'players', qos=1)
                await POKER_DB.add_game(num_players=int(message_str))


async def input_starting_cash():
    async with Client("localhost") as client:
        async with client.filtered_messages("game_room/+/starting_cash") as messages:
            await client.subscribe("game_room/+/starting_cash")
            async for message in messages:
                message_str = message.payload.decode()
                await client.publish("game_room/+/starting_cash", str(message_str), qos=1)
                await POKER_DB.add_game(starting_cash=int(message_str))


async def main():
    # Run example() indefinitely. Reconnect automatically if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await create_game()
            # await input_num_players()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())
