import asyncio

from .common import SingletonObject, AnonError
from .event import Event
from .logger import logger

from typing import List, Type


class Plugin:
    interested: List[Type[Event]]
    rev: bool = False

    def __init__(self, interested: List[Type[Event]] = None):
        if interested is None:
            interested = []
        self.interested = interested

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

    async def on_event(self, event: Event):
        self.nop()

    async def on_load(self):
        logger.info(f'plugin {self} loaded.')


class PluginManager(SingletonObject):
    plugins: List[Plugin] = []
    tasks = set()

    def broad_cast(self, event: Event):
        for plugin in self.plugins:
            if not plugin.default_filter(event) and not plugin.event_filter(event):
                task = asyncio.create_task(plugin.on_event(event))
                self.tasks.add(task)
                task.add_done_callback(self.tasks.discard)

    def register_plugin(self, plugin: Plugin):
        if not isinstance(plugin, Plugin):
            logger.critical('Unknown plugin type, please inherit from anon.Plugin')
            raise AnonError('plugin')
        logger.info(f'Plugin {plugin} registered.')
        task = asyncio.get_event_loop().create_task(plugin.on_load())
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        self.plugins.append(plugin)

    def register_event(self, interest: List[Type[Event]] = None, rev: bool = False):
        def register(func):
            plugin = Plugin()
            plugin.interested = interest
            plugin.on_event = func
            self.register_plugin(plugin)

        return register

    def register_onload(self):
        def register(func):
            plugin = Plugin()
            plugin.on_load = func
            self.register_plugin(plugin)

        return register
