from anon import Bot, Plugin, PluginManager
from anon.event import Event
from anon.storage import Storage
from anon.event.message import PrivateMessage


class StorageTest(Plugin):
    storage: Storage

    def event_filter(self, event: PrivateMessage) -> bool:
        return event.uid != Storage('core')['def_user']

    async def on_event(self, event: PrivateMessage):
        args = event.raw.split(' ')
        cmd = args[0]
        if cmd == 'open':
            self.storage = Storage(args[1])
        if cmd == 'get':
            await event.reply(self.storage[args[1]])
        if cmd == 'set':
            self.storage[args[1]] = args[2]
        if cmd == 'p':
            print(self.storage)


PluginManager().register_plugin(StorageTest([PrivateMessage]))
