# 通用数据结构
VERSION = '0.1.1'


class AnonError(Exception):
    pass


class SingletonObject:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


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
