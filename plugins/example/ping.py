from anon.event import MessageEvent
from anon.plugin import PluginManager

pm = PluginManager()


@pm.register_event([MessageEvent])
async def ping(event: MessageEvent):
    if event.raw == 'ping':
        await event.reply('pong')
