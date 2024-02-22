import json
import re
import chinese2digits as c2d
import aiohttp

from anon import Storage
from anon.event import MessageEvent
from anon.logger import logger
from anon.message import Image, ImageCategory
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


async def fetch_and_save_image(tag: list, num:int = 1)->list :
    params = storage['param'].copy()
    params["num"] = num if 1 < num <= 5 else 1
    if tag:
        params["tag"] = tag
    logger.info(f"tag:{tag},params:{params}")
    proxy_url = "http://111.177.63.86:8888"
    async with aiohttp.ClientSession() as session:
        async with session.get("https://lolisuki.cn/api/setu/v1", params=params, proxy=proxy_url) as response:
            logger.info(f"params:{params}")
            datas = await response.json()
        logger.info(datas)

        # 检查是否有数据返回
        if not datas["data"]:
            return None

        img_url_list = []
        for i_url in range(num):
            img_url = datas["data"][i_url]["urls"]["original"]
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
        if img_url is None:
            await event.reply("图库查找无结果", quote=True)
        else:
            await event.reply(Image(img_url[0]), quote=False)
    elif parts:
        match = re.match(r'来(\d+|零|两|一|二|三|四|五|六|七|八|九)(张|份)(色图|涩图)', parts[0])
        if match:
            quantity = match.group(1)
            try:
                num = int(quantity)
            except:
                num = int(c2d.chineseToDigits(quantity))
            tag = parts[1:] if len(parts) > 1 else None
            logger.info(f"数量: {num}, 标签: {tag}")
            img_url = await fetch_and_save_image(tag, num)
            if img_url is None:
                await event.reply("图库查找无结果", quote=True)
            else:
                index = 1
                for i_url in img_url:
                    logger.info(f"第{index}份色图发送中")
                    index += 1
                    await event.reply(Image(i_url), quote=False)