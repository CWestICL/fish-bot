from typing import Final
import os
from dotenv import load_dotenv
import aiohttp
import io
from discord import Intents, Client, Message, File
from responses import get_response, set_fotd

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("Message was empty!")

    if user_message[0] == "?":
        is_private = True
    elif user_message[0] == "!":
        is_private = False
    else:
        return
    
    print(message.channel)
    
    if str(message.channel) == "Direct Message with Unknown User":
        print("User DMs detected!")
        username = None
    else:
        username = message.author


    try:
        response = get_response(user_message, username)
        if type(response) == dict:
            message_text = response["message"]
            image = response["image"]

            async with aiohttp.ClientSession() as session:
                async with session.get(image) as resp:
                    img = await resp.read()
                    with io.BytesIO(img) as file:

                        await message.author.send(message_text, file=File(file, "fotd.jpg")) if is_private else await message.channel.send(message_text, file=File(file, "fotd.jpg"))
        else:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


@client.event
async def on_ready() -> None:
    print(f"{client.user} is now running!")
    set_fotd()


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}] {username}: '{user_message}'")
    await send_message(message, user_message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == "__main__":
    main()