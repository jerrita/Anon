import json
import os

from .common import AnonExtraConfig
from .logger import logger


class Storage:
    _instances = {}
    _cache: dict
    _initialized = False
    flush_after_set = True

    def __new__(cls, module):
        if module not in cls._instances:
            instance = super(Storage, cls).__new__(cls)
            cls._instances[module] = instance
        return cls._instances[module]

    def __init__(self, module: str):
        if self._initialized:
            logger.debug(f'Storage {module} already initialized.')
            return
        logger.info(f'Initializing storage {module}')

        self.module = module
        storage_file_path = os.path.join(AnonExtraConfig().storage_dir, f'{module}.json')
        self._cache = {}
        try:
            if not os.path.isdir(AnonExtraConfig().storage_dir):
                os.makedirs(AnonExtraConfig().storage_dir)
            if os.path.exists(storage_file_path):
                self._cache = json.load(open(storage_file_path, 'r'))
                logger.info(f'Storage module {module} loaded')
            self.fp = open(storage_file_path, 'w+')
            self.flush()
        except Exception as e:
            logger.warning(f'Open storage file {storage_file_path} failed: {e}')
            self.fp = None
        self._initialized = True

    def get_or(self, item, default=None):
        return self._cache.get(item, default)

    def update(self, data: dict):
        self._cache.update(data)
        if self.flush_after_set:
            self.flush()

    def __getitem__(self, item):
        return self._cache.get(item)

    def __setitem__(self, key, value):
        self._cache[key] = value
        if self.flush_after_set:
            self.flush()

    def flush(self):
        if self.fp:
            self.fp.seek(0)
            self.fp.truncate()
            self.fp.write(json.dumps(self._cache))
            self.fp.flush()

    def close(self):
        """
        关闭持久化文件，但是内存中还有缓存，你可以使用 del Storage(xx) 来删除缓存
        当然也可以用此功能实现 IPC

        :return:
        """
        if self.fp:
            self.fp.close()
            self.fp = None

    def shutdown(self):
        """
        Warning!!! Do not call this function unless you known what it will do.

        :return:
        """
        logger.warning('Storage shutdown called!')
        for key, inst in self._instances.items():
            logger.info(f'Storage {key} saving...')
            del inst

    def __del__(self):
        if self.fp:
            self.close()
