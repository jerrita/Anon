from .event import Event
from ..common import Sender, AnonError
from ..logger import logger
from ..message import Message, Reply, Convertable
from ..protocol import Protocol


class MessageEventFactory:
    @classmethod
    async def factory(cls, proto: Protocol, raw: dict):
        _type = raw.get('message_type')
        if _type == 'private':
            return PrivateMessage(raw)
        if _type == 'group':
            group_info = await proto.get_group_info(raw.get('group_id'))
            raw['group_info'] = group_info
            raw['group_name'] = group_info.group_name
            return GroupMessage(raw)
        logger.warn(f'Unsupported MessageEvent type: {_type}')
        return MessageEvent(raw)


class MessageEvent(Event):
    mid: int
    uid: int
    msg: Message
    raw: str
    sender: Sender

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.category = raw.get('sub_type')
        self.mid = raw.get('message_id')
        self.msg = Message.encode(raw.get('message'))
        self.raw = self.msg.text()
        self.sender = Sender(**raw.get('sender'))

        from ..session import Bot
        self.bot = Bot()

    async def reply(self, msg: Convertable, quote: bool = True):
        """
        向 sender 发送消息

        :param msg: Message
        :param quote: 是否引用原始消息
        :return:
        """
        msg = Message.convert(msg)
        if quote:
            msg.insert(0, Reply(self.mid))

        if isinstance(self, GroupMessage):
            await self.bot.send_group_message(self.gid, msg)
        elif isinstance(self, PrivateMessage):
            await self.bot.send_private_message(self.uid, msg)
        else:
            logger.critical('Unknown message type.')
            raise AnonError('reply')

    def __repr__(self):
        return f'{self.sender.nickname}({self.sender.user_id}): {self.msg}'


class PrivateMessage(MessageEvent):
    def __init__(self, raw):
        super().__init__(raw)
        self.uid = raw.get('user_id')


class GroupMessage(MessageEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.gid = raw.get('group_id')
        self.group_name = raw.get('group_name')
        self.group_info = raw.get('group_info')

    def __repr__(self):
        return f'{self.group_name}({self.gid}) -> ' + super().__repr__()
