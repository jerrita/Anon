from anon import Bot, PluginManager, Plugin
from anon.logger import logger


class CronPlugin(Plugin):
    bot: Bot
    cron = '* * * * *'

    async def on_load(self):
        self.bot = Bot()
        logger.info('CronPlugin loaded')

    async def on_cron(self):
        logger.info('Cron triggered')
        await self.bot.send_private_message(114514191, 'Cron triggered')


PluginManager().register_plugin(CronPlugin())
