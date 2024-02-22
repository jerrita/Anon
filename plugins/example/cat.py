import re

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
    message = event.msg.text()
    if re.fullmatch(r'喵+', message):
        # 计算“喵”的数量
        count = len(message) // len('喵')
        if count == 1:
            img_url = await fetch_and_save_image(False)
            logger.info('喵')
        elif count > 1:
            img_url = await fetch_and_save_image(True)
            await event.reply("不管多少个喵，只要大于1个都会返回10张图的喵~", quote=True)
            logger.info(f'收到了{count}个喵！')
        else:
            return
        index = 1
        for i_url in img_url:
            logger.info(f"第{index}份猫图发送中")
            index += 1
            await event.reply(Image(i_url), quote=False)
