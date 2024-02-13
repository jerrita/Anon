import logging

from anon import Bot
from anon.logger import logger

logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    anon = Bot('192.168.5.145:5800', '114514')
    anon.register_plugins([
        'plugins.example.ping',
        'plugins.example.reply'
    ])
    anon.loop()
