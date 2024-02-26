def any_data(data: dict) -> dict:
    """
    处理 data，删除所有的空值
    """
    return {k: v for k, v in data.items() if v}
