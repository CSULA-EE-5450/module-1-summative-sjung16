import asyncio
from asyncio_mqtt import Client, MqttError
from poker_db import AsyncPokerGameDB
from user_db import UserDB

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

                elif message_str.startswith("add_player_to_game"):
                    message_params = message_str.replace("add_player_to_game", '')
                    await add_player_to_game(client, message_params)

                elif message_str.startswith("init_game"):
                    message_params = message_str.replace("init_game", '')
                    await init_game(client, message_params)

                elif message_str.startswith("bet"):
                    message_params = message_str.replace("bet", '')
                    await bet(client, message_params)

                elif message_str.startswith("the_flop"):
                    message_params = message_str.replace("the_flop", '')
                    await the_flop(client, message_params)

                elif message_str.startswith("the_turn"):
                    message_params = message_str.replace("the_turn", '')
                    await the_turn(client, message_params)

                elif message_str.startswith("the_river"):
                    message_params = message_str.replace("the_river", '')
                    await the_river(client, message_params)


async def create_user(client, message_params):
    """
    Adds a user with the input username to the user database, with a randomly generated password.
    The user must publish a message of his desired username under the designated topic and message format below.

    Topic: "game_command"
    Message format: "create_user username"

    Example: User publishes string message "create_user john_doe" under topic "user_command/create" to create a new
             user with username john_doe

    :param client: The MQTT client
    :param message_params: The parameters portion of the message string
    :return: The username and the password
    """
    try:
        new_username, new_password = USER_DB.create_user(message_params)
    except ValueError:
        await client.publish(("users/" + str(message_params) + "/error"),
                             "That username already exists!", qos=1)
        raise MqttError("That username already exists!")
    await client.publish(("users/" + str(new_username) + "/create_success"), "True", qos=1)


async def create_game(client, message_params):
    """
    Creates a game according to user input parameters, and adds the game to the game database.

    Topic: "game_command"
    Message format: "create_game game_number, num_players, starting_cash" (Important: the three parameters MUST be
                    separated by a comma!"

    Example: User publishes string message "create_game 2, 3, 5000" under topic "game_command/create" to create new game
             with room_number=2, num_players=3, and starting_cash=5000

    :param client: The MQTT client
    :param message_params: The parameters portion of the message string
    """
    message_split = message_params.split(",")
    try:
        await POKER_DB.add_game(room_number=str(message_split[0]),
                                num_players=int(message_split[1]),
                                starting_cash=int(message_split[2]))
        game_info = await POKER_DB.get_game_info(message_split[0])
        await client.publish(("game_rooms/" + str(message_split[0])) + "/num_players", game_info.num_players, qos=1)
        await client.publish(("game_rooms/" + str(message_split[0])) + "/starting_cash",
                             "$" + str(game_info.starting_cash), qos=1)
        await client.publish(("game_rooms/" + str(message_split[0])) + "/players", "", qos=1)
    except KeyError:
        await client.publish(("game_rooms/" + str(message_split[0])) + "/error",
                             "Please enter message in the correct format!", qos=1)
        raise MqttError("Please enter message in the correct format!")


async def add_player_to_game(client, message_params):
    """
    Adds a player to a game that exists in the database.

    Topic: "game_command"
    Message format: "add_player_to_game game_number, username" (Important: the parameters MUST be
                    separated by a comma!"

    Example: User publishes string message "add_player_to_game 3, john_doe" under topic "game_command"
             to add user john_doe to game room number 3

    :param client: The MQTT client
    :param message_params: The parameters portion of the message string
    """
    message_split = message_params.split(",")
    room_number = message_split[0]
    username = message_split[1]
    try:
        game_info = await POKER_DB.get_game_info(room_number)
        player_list = game_info.players
    except KeyError:
        await client.publish("game_rooms/" + str(room_number) + "/error/",
                             "Please enter message in correct format!", qos=1)
        raise MqttError("Please enter message in correct format!")
    if len(player_list) == game_info.num_players:
        await client.publish("game_rooms/" + str(room_number) + "Error", "Room is full; cannot add player!", qos=1)
        raise MqttError("Room is full; cannot add player!")
    player_list.append(username)
    player_idx = player_list.index(username)
    await client.publish("game_rooms/" + str(room_number) + "/players/" + str(username),
                         "player_idx: "+str(player_idx), qos=1)


async def get_game(room_number):
    """
    Gets a game from the poker game database.

    :param room_number: Game room number
    :return: The room's game of poker
    """
    the_game = await POKER_DB.get_game(room_number)
    if the_game is None:
        raise MqttError("Game not found!")
    return the_game


async def get_player_idx(room_number, username):
    """
    Gets the player index of a particular user within a game.

    :param room_number: Room number
    :param username: The target username
    :return: The index of the user within the game room number
    """
    game_info = await POKER_DB.get_game_info(room_number)
    player_list = game_info.players
    player_idx = player_list.index(username)
    return player_idx


async def init_game(client, room_number):
    """
    Deals the initial hands for each player.

    Topic: "game_command"
    Message format: "init_game room_number"

    Example: To do the initial deal for game room 2, the user would publish "init_game 2" under topic "game_command".

    :param client: The MQTT client
    :param room_number: The room number
    """
    the_game = await get_game(room_number)
    the_game.initial_deal()
    game_info = await POKER_DB.get_game_info(room_number)
    player_list = game_info.players
    player_stacks = the_game.get_player_stacks()
    player_cash = the_game.get_player_cash()

    for player in player_list:
        player_idx = await get_player_idx(room_number, player)
        await client.publish("game_rooms/" + room_number + "/players/" + player + "/hand",
                             str(player_stacks[player_idx]), qos=1)
        await client.publish("game_rooms/" + room_number + "/players/" + player + "/cash",
                             "$"+str(player_cash[player_idx]), qos=1)

    await client.publish("game_rooms/" + room_number + "/community_cards_and_pot/the_pot",
                         "$0", qos=1)


async def bet(client, message_params):
    """
    Deals the initial hands for each player.

    Topic: "game_command"
    Message format: "bet room_number, username, bet_amount"

    Example: To do the initial deal for game room 2, the user would publish "init_game 2" under topic "game_command".

    :param client: The MQTT client
    :param message_params: The parameters portion of the message string
    """
    # Split message_params into three parameters
    message_split = message_params.split(",")
    room_number = message_split[0]
    username = message_split[1]
    bet_amount = int(message_split[2])

    # Get the necessary game information
    the_game = await get_game(room_number)
    player_idx = await get_player_idx(room_number, username)
    player_cash = the_game.get_player_cash()

    # Money flow
    player_cash[player_idx] -= bet_amount
    the_game.the_pot += bet_amount
    await client.publish("game_rooms/" + room_number + "/players/" + username + "/cash",
                         "$" + str(player_cash[player_idx]), qos=1)
    await client.publish("game_rooms/" + room_number + "/community_cards_and_pot/the_pot",
                         str(the_game.the_pot), qos=1)


async def the_flop(client, room_number):
    """
    Draw three community cards to reveal the flop.

    Topic: "game_command"
    Message format: "the_flop room_number"

    Example: To reveal the flop for game room 2, the user would publish "the_flop 2" under topic "game_command".

    :param client: The MQTT client
    :param room_number: The room number
    """
    the_game = await get_game(room_number)
    for _ in range(3):
        the_game.community_draw()
    community_stack = the_game.get_community_stack()
    await client.publish("game_rooms/" + room_number + "/community_cards_and_pot/community_cards",
                         str(community_stack), qos=1)


async def the_turn(client, room_number):
    """
    Draw one community card to reveal the turn.

    Topic: "game_command"
    Message format: "the_flop room_number"

    Example: To reveal the flop for game room 2, the user would publish "the_flop 2" under topic "game_command".

    :param client: The MQTT client
    :param room_number: The room number
    """
    the_game = await get_game(room_number)
    the_game.community_draw()
    community_stack = the_game.get_community_stack()
    await client.publish("game_rooms/" + room_number + "/community_cards_and_pot/community_cards",
                         str(community_stack), qos=1)


async def the_river(client, room_number):
    """
    Draw one community card to reveal the river and computes the winner. The pot goes to the winner.

    Topic: "game_command"
    Message format: "the_flop room_number"

    Example: To reveal the flop for game room 2, the user would publish "the_flop 2" under topic "game_command".

    :param client: The MQTT client
    :param room_number: The room number
    """
    the_game = await get_game(room_number)
    the_game.community_draw()
    community_stack = the_game.get_community_stack()
    await client.publish("game_rooms/" + room_number + "/community_cards_and_pot/community_cards",
                         str(community_stack), qos=1)
    # Compute winner
    game_info = await POKER_DB.get_game_info(room_number)
    player_list = game_info.players
    winning_player_idx = the_game.compute_winner()
    winning_player_username = player_list[winning_player_idx]
    player_cash = the_game.get_player_cash()
    best_hands = the_game.get_best_hands()
    player_stacks = the_game.get_player_stacks()

    # Money flow
    player_cash[winning_player_idx] += the_game.the_pot
    await client.publish("game_rooms/" + room_number + "/players/" + winning_player_username + "/hand",
                         str(player_stacks[winning_player_idx]) + "   WINNER! Wins $" +
                         str(the_game.the_pot) + " with hand type " +
                         str(best_hands[winning_player_idx]['hand type']) + " (score: " +
                         str(best_hands[winning_player_idx]['score']) + ")", qos=1)
    await client.publish("game_rooms/" + room_number + "/players/" + winning_player_username + "/cash",
                         "$" + str(player_cash[winning_player_idx]), qos=1)
    # Clear the pot
    the_game.the_pot = 0
    await client.publish("game_rooms/" + room_number + "/community_cards_and_pot/the_pot",
                         "$" + str(the_game.the_pot), qos=1)


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
