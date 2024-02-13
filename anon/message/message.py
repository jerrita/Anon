from .elements import *
from ..logger import logger
from typing import List, Union, Type

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
    def convert(origin: Union[str, List[Union[str, Type[ChainObj]]]]) -> 'Message':
        if isinstance(origin, Message):
            return origin
        if isinstance(origin, str):
            return Message([Text(origin)])
        res = Message([])
        for i in origin:
            if isinstance(i, str):
                res.append(Text(i))
            elif isinstance(i, ChainObj):
                res.append(i)
            else:
                logger.warn(f'Message convert: unknown type {type(i)}')
                res.append(Text(f'<{type(i)}>'))
        return res

    def __repr__(self):
        return ' '.join(i.__repr__() for i in self)


Convertable = Union[str, Message, List[Union[str, Type[ChainObj]]]]

if __name__ == '__main__':
    msg = Message([Text('Hello'), At(123)])
    print(msg.decode())
