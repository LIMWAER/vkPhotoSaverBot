import asyncio
import os
import base64

from aiovk.exceptions import VkAPIError
from aiovk.api import LazyAPI
from dotenv import load_dotenv

from aiovk import TokenSession


load_dotenv()

TG_TOKEN = base64.b64decode(os.getenv("TG_TOKEN")).decode("utf-8")
VK_TOKEN = base64.b64decode(os.getenv("VK_TOKEN")).decode("utf-8")
VK_API_VER = os.getenv("VK_API_VER")


async def func():
    session = TokenSession(access_token=VK_TOKEN)
    api = LazyAPI(session)
    try:
        message = api('photos.getAlbums', owner_id=-910828, v=VK_API_VER)
        albums = await message()
        for album in albums['items']:
            print(album['id'])
    except VkAPIError:
        pass
    await session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())
