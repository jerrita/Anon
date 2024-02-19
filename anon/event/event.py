from ..protocol import Protocol


class EventFactory:

    def __new__(cls, proto: Protocol, raw: dict) -> 'Event':
        _type = raw.get('post_type')
        if _type == 'message':
            from .message import MessageEventFactory
            return MessageEventFactory(proto, raw)
        if _type == 'meta_event':
            return MetaEvent(raw)
        return Event(raw)


class Event:
    time: int
    whoami: int
    category: str

    def __init__(self, raw: dict):
        self.time = raw.get('time')
        self.whoami = raw.get('self_id')
        self.category = raw.get('post_type')

    def __repr__(self):
        return f'<{self.category}>'


class MetaEvent(Event):
    def __init__(self, raw: dict):
        super().__init__(raw)


class NoticeEvent(Event):
    def __init__(self, raw: dict):
        super().__init__(raw)


class RequestEvent(Event):
    def __init__(self, raw: dict):
        super().__init__(raw)
