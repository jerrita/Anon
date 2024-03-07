import datetime

from anon.event import MessageEvent
from anon.plugin import PluginManager

date_usage = """Usage: date
此命令无需任何参数"""


@PluginManager().register_cmd(['date', '几点了'],
                              brif='获取现在的时间',
                              usage=date_usage)
async def date(event: MessageEvent, args):
    await event.reply(str(datetime.datetime.now()), quote=False)
