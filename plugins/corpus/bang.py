import random
import json
import os

from anon import PluginManager
from anon.event import MessageEvent


def choose_motto(mottos, first_prob=0.0):
    """
    从列表中选择一个人物台词，可以为列表中的第一个元素设置更高的选择概率。
    :param mottos: 人物台词列表，不应为空。
    :param first_prob: 第一个元素被选中的概率。应当在0到1之间。如果为0, 则所有元素被选中的概率相等。
                       如果大于0, 则第一个元素有指定的概率被选中。
    :return: 根据指定概率随机选择的人物台词。
    """
    if not mottos:
        return None
    if len(mottos) == 1:
        return mottos[0]
    elif first_prob <= 0:
        return random.choice(mottos)
    else:
        return mottos[0] if random.random() <= first_prob else random.choice(mottos[1:])


pm = PluginManager()


@pm.register_event([MessageEvent])
async def on_event(event: MessageEvent):
    file_path = os.path.join(os.path.dirname(__file__), 'bang.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    match_string = event.msg.text().lower()

    # 直接匹配
    for group in data.values():
        for member in group:
            names = [name.lower() for name in member['name']]
            if any(match_string == name for name in names):  # 检查 match_string 是否在转换后的任一名字中
                motto = choose_motto(member['motto'], first_prob=0.5)
                await event.reply(motto)
                break
