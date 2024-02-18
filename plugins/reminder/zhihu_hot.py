import asyncio
import aiohttp
from datetime import datetime
from pytz import timezone
from anon import Bot, PluginManager, Plugin
from anon.logger import logger
from bs4 import BeautifulSoup


class CronPlugin(Plugin):
    bot: Bot
    cron = '12 * * * *'

    async def on_load(self):
        self.bot = Bot()
        logger.info('CronPlugin loaded')

    async def on_cron(self):
        shanghai_tz = timezone('Asia/Shanghai')
        current_time = datetime.now(shanghai_tz)
        hour = current_time.hour
        logger.info('东八区已经判定')

        if hour in [8, 10, 12, 14, 16, 18, 20, 22]:
            logger.info('Cron triggered on the xth minute of specified hours')

            # 获取知乎热榜并发送消息
            hot_list = await self.get_zhihu_hot_list()
            message = "知乎热榜:\n" + "\n".join(
                [f"{index}: {title}\n链接: {url}" for index, (title, url) in enumerate(hot_list, 1)])
            await self.bot.send_private_message(114514, message)
        else:
            logger.info('Cron triggered but not at the xth minute of specified hours')

    async def get_zhihu_hot_list(self):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, 'https://github.com/justjavac/zhihu-trending-hot-questions')
            return await self.parse_hot_list(html)

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def parse_hot_list(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        hot_list = []
        ol = soup.find('ol')  # 找到包含热门话题的ol标签
        for li in ol.find_all('li')[:15]:  # 只获取前15个li标签
            a_tag = li.find('a')
            question_url = a_tag['href']
            question_title = a_tag.get_text()
            hot_list.append((question_title, question_url))
        return hot_list


# 注册插件
PluginManager().register_plugin(CronPlugin())