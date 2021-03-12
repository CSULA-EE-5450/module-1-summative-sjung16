import asyncio
from asyncio_mqtt import Client, MqttError
from poker_db import AsyncPokerGameDB
from user_db import UserDB

USER_DB = UserDB()
POKER_DB = AsyncPokerGameDB(USER_DB)


async def message_handler():
    """
    Runs the mqtt client and handles messages via topic filters.
    """
    async with Client("localhost") as client:
        await client.subscribe("#")
        async with client.unfiltered_messages() as messages:
            async for message in messages:
                message_str = message.payload.decode()
                if message_str.startswith("create_user"):
                    message_params = message_str.replace("create_user", '')
                    await create_user(client, message_params)
                elif message_str.startswith("create_game"):
                    message_params = message_str.replace("create_game", '')
                    await create_game(client, message_params)
        # async with client.filtered_messages("game_command/create") as messages:
        #     await client.subscribe("game_command/create")
        #     async for message in messages:
        #         await create_user(client, message)


async def create_user(client, message_params):
    """
    Adds a user with the input username to the user database, with a randomly generated password.
    The user must publish a message of his desired username under topic "user_command/create".

    :return: The username and the password
    """
    # async with Client("localhost") as client:
    #     # Receive messages that match the given filter and store as messages
    #     async with client.filtered_messages("user_command/create") as messages:
    #         await client.subscribe("user_command/create")
    #         async for message in messages:
    #             # Convert bytes to string
    #                 message_str = message.payload.decode()
    try:
        new_username, new_password = USER_DB.create_user(message_params)
    except ValueError:
        await client.publish(("users/" + str(message_params) + "/create_success"),
                             "False (detail: That username already exists)", qos=1)
        raise MqttError("That username already exists.")
    await client.publish(("users/" + str(new_username) + "/create_success"), "True", qos=1)


async def create_game(client, message_params):
    """
    Creates a game according to user input parameters.
    The user must publish a message with the three input parameters under topic "game_command/create".

    User input parameters: game_rooms, num_players, starting_cash
                           (Important: parameters must be separated by a comma!)

    Example: If the user publishes to topic "game_command/create" the message "3, 5, 2000", it will create a game with
             number title 3, 5 players and starting cash of 2000 per player.

    A game_uuid and termination password will be automatically generated for the game room.
    """
    # async with Client("localhost") as client:
    #     # Receive messages that match the given filter and store as messages
    #     async with client.filtered_messages("game_command/create") as messages:
    #         await client.subscribe("game_command/create")
    #         async for message in messages:
    #             # Convert bytes to string
    # Split the message string to three parameters: room number, num_players, and starting_cash
    message_split = message_params.split(",")
    if message_split[0] in await client.subscribe("game_rooms"):
        raise MqttError("That room number already exists.")
    game_uuid, term_pass = await POKER_DB.add_game(num_players=int(message_split[1]),
                                                   starting_cash=int(message_split[2]))
    await client.publish(("game_rooms/" + str(message_split[0])) + "/game_uuid", game_uuid, qos=1)
    await client.publish(("game_rooms/" + str(message_split[0])) + "/term_pass", term_pass, qos=1)
    await client.publish(("game_rooms/" + str(message_split[0])) + "/create_success", "True", qos=1)
    await client.publish(("game_rooms/" + str(message_split[0])) + "/num_players", message_split[1], qos=1)
    await client.publish(("game_rooms/" + str(message_split[0])) + "/starting_cash", message_split[2], qos=1)


async def main():
    # Run example() indefinitely. Reconnect automatically if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await message_handler()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())
