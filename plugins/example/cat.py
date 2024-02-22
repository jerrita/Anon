import aiohttp

from anon.event import MessageEvent
from anon.logger import logger
from anon.message import Image
from anon.plugin import PluginManager

pm = PluginManager()


async def fetch_and_save_image(limit: bool = False) -> list:
    params = {}
    num = 10 if limit else 1
    params["limit"] = num

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.thecatapi.com/v1/images/search", params=params) as response:
            logger.info(f"params:{params}")
            datas = await response.json()
        logger.info(datas)

        img_url_list = []
        for i_url in range(num):
            img_url = datas[i_url]["url"]
            img_url_list.append(img_url)
        return img_url_list


@pm.register_event([MessageEvent])
async def cat(event: MessageEvent):
    count = event.raw.count('喵')
    if count:
        img_urls = await fetch_and_save_image(False if count == 1 else True)
        await event.reply([Image(url) for url in img_urls][:count])
