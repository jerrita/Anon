from anon import PluginManager, Permission
from anon.event import MessageEvent
from anon.message import Node, Message

@PluginManager().register_cmd(['node'],
                              perm=Permission.Owner)
async def node(event: MessageEvent, args):
    await event.reply(Node(
        Message.convert('Hello world'),
        user_id=10001000,
        nick_name='某人'
    ))