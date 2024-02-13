import asyncio

from .protocol import Protocol
from .logger import logger
from .common import AnonError, VERSION, SingletonObject
from .event import Event, MessageEvent
from .plugin import PluginManager, Plugin
from typing import List


class Bot(Protocol, SingletonObject):
    pm: PluginManager
    _initialized: bool = False

    def __init__(self, ep: str = '127.0.0.1:5800', token: str = ''):
        """
        Anon 实例

        :param ep: 主动 ws 地址，格式为 domain:port
        :param token: token
        """
        if self._initialized:
            return
        super().__init__(ep, token)
        logger.info(f'Welcome to use Anon/{VERSION} framework! Have fun!')
        logger.info(f'Anon created => {ep}, validating...')
        if not asyncio.get_event_loop().run_until_complete(self.validate()):
            logger.critical('Something wrong, check your endpoint and token.')
            raise AnonError('Bot init')
        logger.info(f'Bot Connected!')
        self.pm = PluginManager()
        self._initialized = True

    def register_plugins(self, plugins: list):
        for plugin in plugins:
            logger.info(f'Loading plugin: {plugin}')
            if isinstance(plugin, Plugin):
                self.pm.register_plugin(plugin)
            else:
                try:
                    __import__(plugin)
                except Exception as e:
                    logger.critical(f'Plugin register error: {e}')
                    raise AnonError('plugin')

    def broad_cast(self, e: Event):
        if isinstance(e, MessageEvent):
            logger.info(e)
        else:
            logger.debug(f'recv: {e}')
        self.pm.broad_cast(e)

    def loop(self):
        asyncio.get_event_loop().run_until_complete(self.event_looper())
