from __future__ import annotations

import asyncio
import json
import uuid
import websockets

from websockets import WebSocketClientProtocol
from .common import AnonError, SingletonObject
from .logger import logger
from .message import Message, Convertable
from typing import TYPE_CHECKING, Dict, Any
from asyncio import Queue

if TYPE_CHECKING:
    from .event import Event


class Protocol(SingletonObject):
    ws: WebSocketClientProtocol
    _pending_requests: Dict[str, Queue] = {}

    def __init__(self, ep: str, token: str):
        self.end_point = f'ws://{ep}'
        self.token = token

    def broad_cast(self, event: Event):
        raise NotImplementedError

    async def send_request(self, func: str, data: dict) -> dict:
        """
        发送请求，若失败，则返回 None

        :param func: 请求服务名
        :param data: params 参数
        :return: 是否成功
        """
        _uuid = str(uuid.uuid4())
        raw = {
            'action': func,
            'params': data,
            'echo': _uuid
        }
        queue = asyncio.Queue()

        self._pending_requests[_uuid] = queue
        await self.ws.send(json.dumps(raw))
        res = await queue.get()
        del self._pending_requests[_uuid]

        if res.get('status') != 'ok':
            logger.warn(f'Send request failed with error: {raw.get("msg")}')

        return res.get('data')

    def validate(self) -> bool:
        """
        检查终端是否有效

        :return:
        """

        from websockets.sync.client import connect
        try:
            with connect(self.end_point, additional_headers={
                "Authorization": self.token
            }, open_timeout=3) as ws:
                ws.recv()
            return True
        except Exception as e:
            logger.warn(f'Validate with error: {e}')
            return False

    async def event_looper(self):
        from .event import EventFactory
        logger.info('Start event looper.')

        while True:
            try:
                async with websockets.connect(self.end_point, extra_headers={
                    "Authorization": self.token
                }) as ws:
                    self.ws = ws
                    while msg := await ws.recv():
                        logger.debug(msg)
                        raw = json.loads(msg)
                        if 'echo' in raw:
                            _uuid = raw['echo']
                            if _uuid in self._pending_requests:
                                logger.debug(f'Session resume: {_uuid}')
                                await self._pending_requests[_uuid].put(raw)
                            else:
                                logger.warn(f'Received a message with unknown UUID: {_uuid}')
                        else:
                            event = EventFactory(raw)
                            self.broad_cast(event)
            except Exception as e:
                # TODO: We can sleep and break here, for timeout error handling
                logger.critical(f'Something went wrong, please open an issue with debug logs.')
                raise AnonError(f'Event loop: {e}')

    async def send_group_message(self, gid: int, msg: Convertable, auto_recall: int = 0) -> bool:
        """
        发送群消息

        :param gid: 群号
        :param msg: 消息
        :param auto_recall: 自动撤回（毫秒），0 为不撤回
        :return:
        """
        msg = Message.convert(msg)
        data = {
            'group_id': gid,
            'message': msg.decode(),
            'auto_escape': True
        }
        if auto_recall:
            data.update({'recall_duration': auto_recall})
        logger.info(f'G({gid}) <- {msg}')
        return await self.send_request('send_group_message', data) is not None

    async def send_private_message(self, uid: int, msg: Convertable, auto_recall: int = 0) -> bool:
        """
        发送私聊

        :param uid: 私聊对象 qq 号
        :param msg: 消息
        :param auto_recall: 自动撤回（毫秒），0 为不撤回
        :return:
        """
        msg = Message.convert(msg)
        data = {
            'user_id': uid,
            'message': msg.decode(),
            'auto_escape': True
        }
        if auto_recall:
            data.update({'recall_duration': auto_recall})
        logger.info(f'F({uid}) <- {msg}')
        return await self.send_request('send_private_msg', data) is not None
