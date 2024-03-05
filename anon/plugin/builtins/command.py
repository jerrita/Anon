from typing import List

from anon.common import SingletonObject
from anon.event import MessageEvent
from anon.logger import logger
from anon.message import Text, Message
from ..plugin import Plugin


class CommandHandler:
    cmd: str
    alter: list
    brif: str
    usage: str

    def __init__(self, cmd: str, brif: str, usage: str, alter: List[str]):
        self.cmd = cmd
        self.brif = brif
        self.usage = usage
        self.alter = alter

    def interest(self, txt: str) -> bool:
        for word in [self.cmd] + self.alter:
            if txt.startswith(word):
                return True
        return False

    async def handle(self, event: MessageEvent, args: List[str]):
        pass

    def __repr__(self):
        return f'<CmdHandler: {self.cmd}({self.alter})>'


class CommandManager(SingletonObject):
    _key_words = set()
    _tasks = set()
    _handlers: List[CommandHandler] = []

    def __init__(self):
        self._key_words.add('help')
        self._key_words.add('帮助')

    def interest(self, msg: MessageEvent) -> bool:
        for word in self._key_words:
            if msg.raw.startswith(word):
                return True
        return False

    async def broad_cast(self, event: MessageEvent):
        texts = Message(list(filter(lambda x: isinstance(x, Text), event.msg))).text().strip()
        args = texts.split()
        if args[0] in ['help', '帮助']:
            if len(args) > 1 and args[1] in self._key_words:
                for handler in self._handlers:
                    if handler.interest(args[1]):
                        res = f'{handler.cmd}: {handler.brif}\nalter: {"/".join(handler.alter)}'
                        res += '\n---------------------\n' + handler.usage
                        await event.reply(res, quote=False)
                        return
            res = 'Anon 命令帮助\n---------------------\n'
            for handler in self._handlers:
                res += f'{handler.cmd}: {handler.brif}\n'
            res += '---------------------\n'
            await event.reply(res, quote=False)
            return
        for handler in self._handlers:
            if handler.interest(texts):
                logger.debug(f'Command call -> {handler}')
                await handler.handle(event, args)
                return

    def register_handler(self, cmd: str, brif: str, usage: str, alter: List[str]):
        def register(func):
            if cmd in self._key_words:
                logger.warn(f'Command {cmd} registered!')
                return
            self._key_words.add(cmd)
            for i in alter:
                if i in self._key_words:
                    logger.warn(f'Alter name {i} for {cmd} occupied!')
                else:
                    self._key_words.add(i)
            handler = CommandHandler(cmd, brif, usage, alter)
            handler.handle = func
            self._handlers.append(handler)
            logger.info(f'Handler {handler} registered.')

        return register


class CommandPlugin(Plugin):
    _manager: CommandManager

    def prevent_after(self, event: MessageEvent) -> bool:
        return self._manager.interest(event)

    def event_filter(self, event: MessageEvent) -> bool:
        return not self._manager.interest(event)

    async def on_load(self):
        self.interested = [MessageEvent]
        self._manager = CommandManager()

    async def on_event(self, event: MessageEvent):
        await self._manager.broad_cast(event)
