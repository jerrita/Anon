import os

from anon import PluginManager
from anon.event.message import PrivateMessage
from anon.message import *
from anon.storage import Storage


@PluginManager().register_event([PrivateMessage])
async def image(event: PrivateMessage):
    if event.sender.user_id == Storage('core')['def_user']:
        if event.raw == '来点涩图':
            await event.reply(Image('https://i.pixiv.re/img-original/img/2020/08/22/21/46/24/83862048_p0.jpg'))
        else:
            await event.reply(Image(f'file://{os.path.join(os.path.dirname(__file__), "test.png")}'))
