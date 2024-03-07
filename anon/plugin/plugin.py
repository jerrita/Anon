import asyncio
from typing import List, Type

import aiocron

from ..common import SingletonObject, AnonError, StructClass
from ..event import Event, MessageEvent
from ..logger import logger


class CronThread:
    loop: asyncio.AbstractEventLoop
    tasks = set()

    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def add_cron(self, cron: str, func, *args):
        async def wrapper():
            logger.info(f'Cron triggered: {cron}')
            await func(*args)

        task = aiocron.crontab(cron, func=wrapper, loop=self.loop)
        self.tasks.add(task)


class Plugin(StructClass):
    interested: List[Type[Event]] = []
    rev: bool = False
    enabled: bool = True  # WIP
    cron: str = None
    brif: str = ''
    usage: str = ''
    keywords: list = []

    def __init__(self, interested: List[Type[Event]] = None, **kwargs):
        super().__init__(**kwargs)
        if interested is not None:
            self.interested = interested

    def match_cmd(self, txt: str) -> bool:
        """
        是否需要响应 CMD
        """
        return any(map(lambda x: txt.startswith(x), self.keywords))

    def nop(self):
        pass

    def default_filter(self, event: Event) -> bool:
        """
        默认事件过滤器，返回 interested 事件

        :param event: 事件
        :return: 是否需要过滤
        """
        if len(self.interested) == 0:
            return self.rev

        for i in self.interested:
            if isinstance(event, i):
                return self.rev
        return True

    def event_filter(self, event: Event) -> bool:
        """
        自定义事件过滤规则

        :param event: 事件
        :return: 是否需要过滤
        """
        self.nop()
        return False

    def prevent_after(self, event: Event) -> bool:
        """
        是否阻止事件后向传递，插件优先级为加载顺序
        """
        return (isinstance(event, MessageEvent)
                and self.match_cmd(event.msg.text_only))

    async def on_cmd(self, event: MessageEvent, args: list):
        pass

    async def on_event(self, event: Event):
        pass

    async def on_load(self):
        pass

    async def on_cron(self):
        pass

    async def on_shutdown(self):
        pass


class PluginManager(SingletonObject):
    plugins: List[Plugin] = []
    tasks = set()
    _initialized: bool = False
    _loop: asyncio.AbstractEventLoop
    _cron: CronThread

    def __init__(self, *args):
        if not self._initialized:
            self._loop = args[0]
            self._cron = CronThread(self._loop)
            self._initialized = True
            logger.info('Loading builtin plugins...')
            from .builtins import BUILTIN_PLUGINS
            for plugin in BUILTIN_PLUGINS:
                self.register_plugin(plugin)
            logger.info('PluginManager initialized.')

    def broad_cast(self, event: Event):
        for plugin in self.plugins:
            if not plugin.default_filter(event) and not plugin.event_filter(event):
                if isinstance(event, MessageEvent) and plugin.match_cmd(event.msg.text_only):
                    task = asyncio.create_task(plugin.on_cmd(event, event.msg.text_only.split()))
                else:
                    task = asyncio.create_task(plugin.on_event(event))
                self.tasks.add(task)
                task.add_done_callback(self.tasks.discard)
                if plugin.prevent_after(event):
                    return

    async def shutdown(self, timeout: int):
        logger.info(f'Plugins shutting down, timeout = {timeout}s...')
        for plugin in self.plugins:
            await self._loop.create_task(plugin.on_shutdown())
        for i in range(timeout):
            logger.warn(f'PluginManager waiting... {timeout - i}s')
            await asyncio.sleep(1)
        logger.info('PluginManager Shutdown.')

    def register_plugin(self, plugin: Plugin):
        if not isinstance(plugin, Plugin):
            logger.critical('Unknown plugin type, please inherit from anon.Plugin')
            raise AnonError('plugin')
        logger.info(f'Plugin {plugin} registered.')
        task = self._loop.create_task(plugin.on_load())
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        if plugin.cron is not None:
            logger.info(f'Plugin {plugin} has cron: {plugin.cron}')
            self._cron.add_cron(plugin.cron, plugin.on_cron)
        self.plugins.append(plugin)

    def register_event(self, interest: List[Type[Event]] = None, rev: bool = False, **kwargs):
        def register(func):
            plugin = Plugin(**kwargs)
            plugin.interested = interest
            plugin.rev = rev
            plugin.on_event = func
            self.register_plugin(plugin)

        return register

    def register_onload(self, **kwargs):
        def register(func):
            plugin = Plugin(**kwargs)
            plugin.on_load = func
            self.register_plugin(plugin)

        return register

    def register_cmd(self, keys: List[str], **kwargs):
        def register(func):
            plugin = Plugin(**kwargs)
            plugin.keywords = keys
            plugin.on_cmd = func
            self.register_plugin(plugin)

        return register

    def register_cron(self, cron: str, **kwargs):
        def register(func):
            plugin = Plugin(**kwargs)
            plugin.on_cron = func
            plugin.cron = cron
            self.register_plugin(plugin)

        return register
