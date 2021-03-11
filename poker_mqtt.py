import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError


async def example():
    async with Client("localhost") as client:
        async with client.filtered_messages("game/create") as messages:
            await client.subscribe("game/#")
            async for message in messages:
                message_str = message.payload.decode()
                if message_str == 'create_game':
                    print('creating game')
                    # create game here
                    # publish game_uuid, term_pass and a message
        async with client.filtered_messages("game/+/stacks") as messages:
            await client.subscribe("game/#")
            async for message in messages:
                message_str = message.payload.decode()
                if message_str == 'my_hand':
                    print('Your hand is (Card1), (Card2)')


async def main():
    # Run example() indefinitely. Reconnect automatically
    # if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await example()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())
