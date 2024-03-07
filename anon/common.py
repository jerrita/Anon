# 通用数据结构
VERSION = '0.3.2'


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

    def data(self):
        return {attr: getattr(self, attr) for attr in self.__annotations__ if hasattr(self, attr)}


class Sender(StructClass):
    user_id: int
    nickname: str
    card: str
    level: str
    role: str
    title: str
    tiny_id: str


class GroupInfo(StructClass):
    group_id: int
    group_name: str
    group_remark: str
    group_uin: int
    admins: list
    class_text: str
    is_frozen: bool
    max_member: int
    max_member_count: int
    member_num: int
    member_count: int


class AnonExtraConfig(StructClass):
    storage_dir: str = 'storage'
    log_file: str = '/dev/null'
    def_user: int = 114514191  # 默认用户，某些示例插件会使用
    def_group: int = 114514191  # 默认群组，某些示例插件会使用
