import datetime

from anon.event import MessageEvent
from anon.plugin import CommandManager

date_usage = """Usage: date
此命令无需任何参数"""


@CommandManager().register_handler('date', '展示现在的时间', usage=date_usage, alter=['现在几点了'])
async def date(event: MessageEvent, args):
    await event.reply(str(datetime.datetime.now()))
