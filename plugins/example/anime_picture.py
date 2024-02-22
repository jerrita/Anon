import json
import re

import aiohttp
import chinese2digits as c2d

from anon import Storage
from anon.event import MessageEvent
from anon.logger import logger
from anon.message import Image
from anon.plugin import PluginManager

pm = PluginManager()
storage = Storage('example.setu')
if not storage['param']:
    storage['param'] = {
        "r18": 0,
        "ai": 0,
        "level": "0-2",
        "taste": "1,2",
    }


async def fetch_and_save_image(tag: list, num: int = 1) -> list:
    params = storage['param'].copy()
    params["num"] = num if 1 < num <= 5 else 1
    if tag:
        params["tag"] = tag
    logger.info(f"tag:{tag},params:{params}")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://lolisuki.cn/api/setu/v1", params=params) as response:
            logger.info(f"params:{params}")
            datas = await response.json()
        logger.info(datas)

        img_url_list = []
        for data in datas['data']:
            img_url = data['urls']['original']
            img_url = img_url.replace('i.pixiv.cat', 'i.pixiv.re')
            img_url_list.append(img_url)
        return img_url_list


@pm.register_event([MessageEvent])
async def handle_message(event: MessageEvent):
    message = event.msg.text()
    parts = message.split()

    if message.startswith('s/setu'):
        storage['param'] = json.loads(message[6:].strip())
        await event.reply(f'Setu param set to:{storage["param"]}')
    if message.startswith('g/setu'):
        await event.reply(json.dumps(storage['param']))

    if parts and parts[0] in ['help', '帮助'] and len(parts) > 1 and parts[1] in ['色图', '涩图']:
        await event.reply("来点色图/涩图 后跟你的偏好标签，标签之间用空格隔开")
    elif parts and parts[0] in ['来点色图', '来点涩图']:
        tag = parts[1:]  # 获取所有的标签
        logger.info(tag)
        img_url = await fetch_and_save_image(tag)
        if not img_url:
            await event.reply("图库查找无结果", quote=True)
        else:
            await event.reply(Image(img_url[0]), quote=False)
    elif parts:
        match = re.match(r'[色涩]图 *([\d零两一二三四五六七八九])[张份](.*)', message)
        if match:
            quantity = match.group(1)
            if quantity in '零两一二三四五六七八九':
                num = int(c2d.chineseToDigits(quantity))
            else:
                num = int(quantity)
            tag = match.group(2).strip().split(' ')
            logger.info(f"数量: {num}, 标签: {tag}")
            img_url = await fetch_and_save_image(tag, num)
            if not img_url:
                await event.reply("图库查找无结果", quote=True)
            else:
                images = [Image(url) for url in img_url]
                await event.reply(images)
