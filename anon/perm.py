from enum import IntEnum

class Permission(IntEnum):
    """
    用于调用权限过滤？
    """
    Owner = 0
    Administrator = 1
    Moderator = 2
    User = 3
