import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
from poker_db import AsyncPokerGameDB
from user_db import UserDB

USER_DB = UserDB()
POKER_DB = AsyncPokerGameDB()


async def create_user():
    async with Client("localhost") as client:
        # Receive messages that match the given filter and store as messages
        async with client.filtered_messages("user/create") as messages:
            await client.subscribe("user/create")
            async for message in messages:
                # Convert bytes to string
                message_str = message.payload.decode()
                try:
                    new_username, new_password = USER_DB.create_user(message_str)
                except ValueError:
                    print("That username already exists.")
                return {'success': True, 'username': new_username, 'password': new_password}


async def create_game():
    """
    Creates a game according to user input parameters.

    User input parameters: game_room, num_players, starting_cash
                           (Important: parameters must be separated by a comma!)

    Example: If the user publishes to topic "game/create" the message "3, 5, 2000", it will create a game with number
             title 3, 5 players and starting cash of 2000 per player.

    A random game_uuid and termination password will be generated for the game room.
    """
    async with Client("localhost") as client:
        # Receive messages that match the given filter and store as messages
        async with client.filtered_messages("game/create") as messages:
            await client.subscribe("game/create")
            async for message in messages:
                # Convert bytes to string
                message_str = message.payload.decode()
                # Split the message string to three parameters: room number, num_players, and starting_cash
                message_split = message_str.split(",")
                game_uuid, term_pass = await POKER_DB.add_game(num_players=int(message_split[1]),
                                                               starting_cash=int(message_split[2]))
                await client.publish(("game_room/" + str(message_split[0])) + "/game_uuid", game_uuid, qos=1)
                await client.publish(("game_room/" + str(message_split[0])) + "/term_pass", term_pass, qos=1)
                await client.publish(("game_room/" + str(message_split[0])) + "/create_success", "True", qos=1)
                await client.publish(("game_room/" + str(message_split[0])) + "/num_players", message_split[1], qos=1)
                await client.publish(("game_room/" + str(message_split[0])) + "/starting_cash", message_split[2], qos=1)


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
