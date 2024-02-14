from anon import PluginManager, Plugin, Bot
from anon.event import MessageEvent
from anon.message import *


class ReplyPlugin(Plugin):
    async def on_load(self):
        logger.info('ping plugin loaded.')
        # await Bot().send_private_message(your_qq, 'Bot started!')

    async def on_event(self, event: MessageEvent):
        if event.raw == 'anon':
            await event.reply('哈？')
        if event.raw == 'soyo':
            await event.reply('我什么都愿意做的！')
        if event.raw == 'rikki':
            await event.reply('は？')
        if event.raw == 'saki':
            await event.reply('你这个人，心里永远只有自己呢')
        if event.raw == 'ranna':
            await event.reply('芭菲～芭菲～')


PluginManager().register_plugin(ReplyPlugin([MessageEvent]))
