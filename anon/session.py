import asyncio
import signal
import sys

from .common import AnonError, VERSION, SingletonObject, AnonExtraConfig
from .event import MessageEvent, EventFactory
from .logger import logger
from .plugin import PluginManager, Plugin
from .protocol import Protocol
from .storage import Storage


class Bot(Protocol, SingletonObject):
    pm: PluginManager
    timeout: int
    _group_cache: dict
    _loop: asyncio.AbstractEventLoop
    _initialized: bool = False

    def __init__(self, ep: str = '127.0.0.1:5800', token: str = '', timeout: int = 3, **kwargs):
        """
        Anon 实例

        :param ep: 主动 ws 地址，格式为 domain:port
        :param token: token
        :param timeout: 收到 SIGTERM 的等待插件停止时间
        """

        if self._initialized:
            return
        super().__init__(ep, token)
        logger.info(f'Welcome to use Anon/{VERSION} framework! Have fun!')
        self.extras = AnonExtraConfig(**kwargs)
        logger.debug(f'Extras: {self.extras.data()}')
        Storage('core').update(self.extras.data())
        logger.info(f'Anon created => {ep}, validating...')
        self._loop = asyncio.get_event_loop()
        if sys.platform != 'win32':  # 如果不是 Windows 平台
            self._loop.add_signal_handler(signal.SIGTERM, lambda: self._loop.create_task(self.sig_term()))
        if not self._loop.run_until_complete(self.validate()):
            logger.critical('Something wrong, check your endpoint and token.')
            raise AnonError('Bot init')
        logger.info(f'Bot Connected!')
        self.pm = PluginManager(self._loop)
        self.timeout = timeout
        self._initialized = True

    async def sig_term(self):
        logger.critical('SIGTERM received, stopping...')
        logger.warning(f'Pending tasks: {len(asyncio.all_tasks())}')
        Storage('core').shutdown()
        await self.pm.shutdown(self.timeout)
        logger.critical('Anon stopped.')
        self._loop.stop()

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

    async def broad_cast(self, event_raw: dict):
        event = await EventFactory.factory(self, event_raw)
        if isinstance(event, MessageEvent):
            logger.info(event)
        else:
            logger.debug(f'recv: {event}')
        self.pm.broad_cast(event)

    def loop(self):
        try:
            self._loop.run_until_complete(self.event_loop())
        except Exception as e:
            logger.critical(f'Loop error: {e}')
