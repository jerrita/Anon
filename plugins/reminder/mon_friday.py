import asyncio
import aiohttp
from datetime import datetime
from pytz import timezone
from anon import Bot, PluginManager, Plugin
from anon.logger import logger
from bs4 import BeautifulSoup

class CronPlugin(Plugin):
    bot: Bot
    # 定义两个定时任务，分别在周一和周五的凌晨0点1分触发
    cron = ['1 0 * * 1', '1 0 * * 5']
    async def on_load(self):
        self.bot = Bot()
        logger.info('CronPlugin loaded')

    async def on_cron(self):
        shanghai_tz = timezone('Asia/Shanghai')
        current_time = datetime.now(shanghai_tz)
        weekday = current_time.weekday()
        logger.info('东八区已经判定')

        # 判断今天是周一还是周五
        if weekday == 0:  # Monday
            await self.bot.send_private_message(114514, "周一啦")
            logger.info('Sent message: 周一啦')
        elif weekday == 4:  # Friday
            await self.bot.send_private_message(114514, "周五啦！")
            logger.info('Sent message: 周五啦！')
        else:
            logger.info('Cron triggered but not on Monday or Friday')


# 注册插件
PluginManager().register_plugin(CronPlugin())
