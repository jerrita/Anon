# 通用数据结构
VERSION = '0.1.0'


class AnonError(Exception):
    pass


class SingletonObject:
    def __new__(cls, *args, **kwargs):
        name = '_ins_' + cls.__name__
        if not hasattr(SingletonObject, name):
            setattr(SingletonObject, name, object.__new__(cls))
        return getattr(SingletonObject, name)


class StructClass:
    def __init__(self, **kwargs):
        for k, _ in self.__annotations__.items():
            if k in kwargs:
                self.__setattr__(k, kwargs[k])


class Sender(StructClass):
    user_id: int
    nickname: str
    card: str
    level: str
    role: str
    title: str
    tiny_id: str
