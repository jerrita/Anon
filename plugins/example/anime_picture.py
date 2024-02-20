import os

import aiohttp
from anon.event import MessageEvent
from anon.logger import logger
from anon.message import Image, ImageCategory
from anon.plugin import PluginManager

pm = PluginManager()

async def fetch_and_save_image(tag: list):
    params = {
        "r18": 0,
        "level": 0-3
    }
    if tag:
        params["tag"] = tag
    logger.info(f"tag:{tag},params:{params}")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://lolisuki.cn/api/setu/v1", params=params) as response:
            logger.info(f"params:{params}")
            datas = await response.json()
        logger.info(datas)

        # 检查是否有数据返回
        if not datas["data"]:
            return None

        img_url = datas["data"][0]["urls"]["original"]
        img_url = img_url.replace('i.pixiv.cat', 'i.pixiv.re')
        return img_url

@pm.register_event([MessageEvent])
async def handle_message(event: MessageEvent):
    message = event.msg.text()
    parts = message.split()

    if parts and parts[0] in ['help', '帮助'] and len(parts) > 1 and parts[1] in ['色图', '涩图']:
        await event.reply("来点色图/涩图 后跟你的偏好标签，标签之间用空格隔开")

    elif parts and parts[0] in ['来点色图', '来点涩图']:
        tag = parts[1:]  # 获取所有的标签
        logger.info(tag)
        img_url = await fetch_and_save_image(tag)
        if img_url is None:
            await event.reply("图库查找无结果", quote=True)
        else:
                await event.reply(Image(img_url,sub_type=ImageCategory.MEME), quote=False)
