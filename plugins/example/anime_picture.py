from anon.event import MessageEvent
from anon.message import Image
from anon.plugin import PluginManager
import aiohttp
import asyncio

pm = PluginManager()



async def fetch_and_save_image():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.lolicon.app/setu/v2") as response:
            datas = await response.json()

        img_url = datas["data"][0]["urls"]["original"]
        img_url = img_url.replace('i.pixiv.cat', 'i.pixiv.re')
        return img_url


@pm.register_event([MessageEvent])
async def handle_message(event: MessageEvent):
    if event.msg.text() == '来点色图':
        img_url = await fetch_and_save_image()
        await event.reply(Image(img_url))