from datetime import datetime

from pytz import timezone

from anon import Bot, PluginManager, Plugin
from anon.logger import logger
from anon.storage import Storage


class CronPlugin(Plugin):
    bot: Bot
    cron = '0 0 * * 1,5'
    group: int

    async def on_load(self):
        self.bot = Bot()
        self.group = Storage('core')['def_group']
        logger.info('CronPlugin loaded')

    async def on_cron(self):
        shanghai_tz = timezone('Asia/Shanghai')
        current_time = datetime.now(shanghai_tz)
        weekday = current_time.weekday()

        if weekday == 0:  # Monday
            await self.bot.send_group_message(self.group, "周一啦！")
        elif weekday == 4:  # Friday
            await self.bot.send_group_message(self.group, "周五啦！")
        else:
            logger.info('Cron triggered but not on Monday or Friday')


# 注册插件
PluginManager().register_plugin(CronPlugin())
