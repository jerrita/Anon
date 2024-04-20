from anon.event import MessageEvent
from ..plugin import Plugin, PluginManager

usage = """Usage: help <command>"""


class HelpPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.brif = '获取可用帮助列表'
        self.usage = usage
        self.keywords = ['help', '帮助列表', '指令列表']
        self.prefix = self.extras.cmd_prefix

    async def on_cmd(self, event: MessageEvent, args: list):
        pm = PluginManager()
        res = ''
        key = 'D1nGzhEn' if len(args) < 2 else args[1]
        for plugin in pm.plugins:
            if len(plugin.keywords):
                if key in plugin.keywords:
                    await event.reply(plugin.usage, quote=False)
                    return
                res += f'{plugin.keywords[0]}: {plugin.brif}\n'
        res = 'Anon 命令帮助\n---------------------\n' + res
        res += '---------------------\n'
        await event.reply(res, quote=False)
