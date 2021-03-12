import asyncio
from asyncio_mqtt import Client, MqttError
from poker_db import AsyncPokerGameDB
from user_db import UserDB
from dataclasses import dataclass

USER_DB = UserDB()
POKER_DB = AsyncPokerGameDB(USER_DB)


async def message_handler():
    """
    Runs the MQTT client and handles messages via topic filters.
    """
    async with Client("localhost") as client:
        await client.subscribe("#")
        async with client.unfiltered_messages() as messages:
            async for message in messages:
                message_str = message.payload.decode()
                if message_str.startswith("create_user"):
                    # Delete the command portion of the message ("create_user")
                    message_params = message_str.replace("create_user", '')
                    # Then feed the remaining message of only the parameter(s) (username).
                    await create_user(client, message_params)
                elif message_str.startswith("create_game"):
                    message_params = message_str.replace("create_game", '')
                    await create_game(client, message_params)
                # elif message_str.startswith("add_player"):
                #     message_params = message_str.replace("add_player", '')
                #     await add_player(client, message_params)


async def create_user(client, message_params):
    """
    Adds a user with the input username to the user database, with a randomly generated password.
    The user must publish a message of his desired username under the designated topic and message format below.

    Topic: "user_command/create"
    Message format: "create_user username"

    Example: User publishes string message "create_user john_doe" under topic "user_command/create" to create a new
             user with username john_doe

    :return: The username and the password
    """
    try:
        new_username, new_password = USER_DB.create_user(message_params)
    except ValueError:
        await client.publish(("users/" + str(message_params) + "/create_success"),
                             "False (detail: That username already exists)", qos=1)
        raise MqttError("That username already exists.")
    await client.publish(("users/" + str(new_username) + "/create_success"), "True", qos=1)


async def create_game(client, message_params):
    """
    Creates a game according to user input parameters, and adds the game to the game database.
    The user must publish a message of his desired username under the designated topic and message format below.

    Topic: "game_command/create"
    Message format: "create_game game_number, num_players, starting_cash" (Important: the three parameters MUST be
                    separated by a comma!"

    Example: User publishes string message "create_game 3, 5, 2000" under topic "game_command/create" to create new game
             with game_number=3, num_players=5, and starting_cash=2000
    """
    message_split = message_params.split(",")
    try:
        await POKER_DB.add_game(room_number=str(message_split[0]),
                                num_players=int(message_split[1]),
                                starting_cash=int(message_split[2]))
        game_info = await POKER_DB.get_game_info(message_split[0])
        await client.publish(("game_rooms/" + str(message_split[0])) + "/create_success", "True", qos=1)
        await client.publish(("game_rooms/" + str(message_split[0])) + "/num_players", game_info.num_players, qos=1)
        await client.publish(("game_rooms/" + str(message_split[0])) + "/starting_cash", game_info.starting_cash, qos=1)
    except KeyError:
        await client.publish(("game_rooms/" + str(message_split[0])) + "/create_success",
                             "False (detail: That game room already exists)", qos=1)
        raise MqttError("That game room already exists.")


async def main():
    # Run the message handler indefinitely. Reconnect automatically if the connection is lost.
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
