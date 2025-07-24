from functools import cached_property
from typing import List, Union

from .elements import *
from ..logger import logger

MessageRaw = List[dict]


class Message(List[ChainObj]):
    def decode(self) -> MessageRaw:
        """
        将 MessageChain 转为原始链

        :return:
        """
        return [i.decode() for i in self]

    @classmethod
    def encode(cls, raw: MessageRaw) -> 'Message':
        """
        将原始链转化为 MessageChain

        :param raw:
        :return:
        """
        return cls([ChainObj.encode(item) for item in raw])

    @staticmethod
    def convert(origin: Union[str, 'ChainObj', List[Union[str, 'ChainObj']]]) -> 'Message':
        if isinstance(origin, Message):
            return origin
        if isinstance(origin, str):
            return Message([Text(origin)])
        if isinstance(origin, ChainObj):
            return Message([origin])
        res = Message([])
        for i in origin:
            if isinstance(i, str):
                res.append(Text(i))
            elif isinstance(i, ChainObj):
                res.append(i)
            else:
                logger.warning(f'Message convert: unknown type {type(i)}')
                res.append(Text(f'<{type(i)}>'))
        return res

    def text(self) -> str:
        """
        建议取代 event.raw 使用，获取可处理的文本

        :return: str
        """
        return self.__repr__()

    @cached_property
    def text_only(self) -> str:
        """
        获取去除所有非 Text 子类后剩余的文本
        注意，一旦调用，则后续调用不可变
        此函数主要用于解析 CMD 命令

        :return: str
        """
        return ''.join(map(
            lambda x: x.__repr__().strip(),
            list(filter(lambda x: isinstance(x, Text), self))
        ))

    def __repr__(self):
        return ' '.join(i.__repr__() for i in self)


Convertable = Union[str, Message, 'ChainObj', list]

if __name__ == '__main__':
    msg = Message([Text('Hello'), At(123)])
