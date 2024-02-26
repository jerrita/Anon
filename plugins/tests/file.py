from anon import Plugin, Bot, PluginManager
from anon.event import PrivateMessage
from anon.storage import Storage


class FilePlugin(Plugin):
    file: str = ''
    storage: Storage

    def event_filter(self, event: PrivateMessage) -> bool:
        return event.sender.user_id != self.storage['def_user']

    def on_load(self):
        self.storage = Storage('core')

    async def on_event(self, event: PrivateMessage):
        if event.raw == 'file':
            await event.reply(self.file)
        if event.raw == 'download':
            self.file = await Bot().shamrock_download_file(
                url='https://i.pixiv.re/img-original/img/2021/07/30/22/23/51/91606424_p0.jpg'
                , name='test.jpg')
            await event.reply(f'[FilePlugin] file downloaded: {self.file}')
        if event.raw == 'upload':
            await Bot().upload_private_file(self.storage['def_user'], self.file, 'test.jpg')
        if event.raw == 'group':
            await Bot().upload_group_file(self.storage['def_group'], self.file, 'test.jpg')


PluginManager().register_plugin(FilePlugin([PrivateMessage]))
