import asyncio
import json
from datetime import datetime

import aiohttp
from pytz import timezone

from anon import Bot, PluginManager, Plugin
from anon.event import MessageEvent
from anon.logger import logger
from anon.storage import Storage


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def get_zhihu_hot_list(date_str):
    url = f'https://raw.githubusercontent.com/justjavac/zhihu-trending-hot-questions/master/raw/{date_str}.json'
    logger.info(url)
    async with aiohttp.ClientSession() as session:
        retries = 3
        while retries > 0:
            try:
                html = await fetch(session, url)
                json_data = json.loads(html)
                return json_data
            except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
                logger.info(f"网络请求错误: {e}")
                retries -= 1
                if retries > 0:
                    logger.info("将在一分钟后重试...")
                    await asyncio.sleep(60)
                else:
                    logger.info("多次尝试获取知乎热榜失败，跳过此次尝试。")
                    return None
            except Exception as e:
                logger.info(f"解析JSON时出错: {e}")
                retries -= 1
                if retries > 0:
                    logger.info("将在一分钟后重试...")
                    await asyncio.sleep(60)
                else:
                    logger.info("多次尝试解析知乎热榜失败，跳过此次尝试。")
                    return None


class ZhihuPlugin(Plugin):
    bot: Bot
    cron = '10 8-20/4 * * *'
    group: int
    storage: Storage
    brif = '定时知乎热榜'
    usage = 'Usage: zhihu set/get <num>\n设置知乎热榜 topn'
    keywords = ['zhihu']

    async def on_load(self):
        self.bot = Bot()
        self.group = Storage('core')['def_group']
        self.storage = Storage('example.zhihu')
        if not self.storage['topn']:
            self.storage['topn'] = 5
        logger.info('CronPlugin loaded')

    async def on_cron(self):
        shanghai_tz = timezone('Asia/Shanghai')
        today = datetime.now(shanghai_tz)
        date_str = today.strftime('%Y-%m-%d')

        logger.info('Cron triggered on the xth minute of specified hours')

        # 获取知乎热榜并发送消息
        hot_list = await get_zhihu_hot_list(date_str)
        top_n = self.storage['topn']
        if hot_list:
            # 将热榜切分为每 10 个一组，应对手机 QQ 一条消息超过 10 个就无法渲染超链接的 bug
            chunk_size = 10
            for i in range(0, len(hot_list[:top_n]), chunk_size):
                logger.info(f'第{i + 1}组, chunk_size={chunk_size}, len(hot_list[:top_n])={len(hot_list[:top_n])}')
                message_chunk = "知乎热榜:\n" + "\n".join(
                    [f"{index}. {item['title']}\n链接: {item['url']}" for index, item in
                     enumerate(hot_list[i:i + chunk_size], i + 1)])
                try:
                    await self.bot.send_group_message(self.group, message_chunk)

                except Exception as e:
                    logger.error(f"发送消息时出错: {e}")

    async def on_cmd(self, event: MessageEvent, args) -> bool:
        if len(args) < 2:
            return True

        if args[1] == 'get':
            await event.reply(f'当前 topn 设置为: {self.storage["topn"]}')
        else:
            try:
                n = int(args[2])
                self.storage['topn'] = n
                await event.reply(f'知乎 topn 设置为: {n}')
            except:
                return True


# 注册插件
PluginManager().register_plugin(ZhihuPlugin([MessageEvent]))
