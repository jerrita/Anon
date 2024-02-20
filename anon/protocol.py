from __future__ import annotations

import asyncio
import json
import uuid
from asyncio import Queue
from typing import TYPE_CHECKING, Dict, List

import websockets
from websockets import WebSocketClientProtocol

from .common import *
from .logger import logger
from .message import Message, Convertable

if TYPE_CHECKING:
    from .event import Event


class Protocol:
    ws: WebSocketClientProtocol
    _group_cache: Dict[int, GroupInfo]
    _pending_requests: Dict[str, Queue] = {}

    def __init__(self, ep: str, token: str):
        self.end_point = f'ws://{ep}'
        self.token = token
        self._loop = asyncio.new_event_loop()
        self._group_cache = {}

    def broad_cast(self, event: Event):
        raise NotImplementedError

    async def send_request(self, func: str, data: dict) -> dict | list:
        """
        发送请求，若失败，则返回 None

        :param func: 请求服务名
        :param data: params 参数
        :return: data 字段
        """
        _uuid = str(uuid.uuid4())
        raw = {
            'action': func,
            'params': data,
            'echo': _uuid
        }
        queue = asyncio.Queue()
        logger.debug(f'Session created: {_uuid}')

        self._pending_requests[_uuid] = queue
        await self.ws.send(json.dumps(raw))
        res = await queue.get()
        del self._pending_requests[_uuid]

        if res.get('status') != 'ok':
            logger.warn(f'Send request failed with error: {raw.get("msg")}')

        return res.get('data')

    async def validate(self) -> bool:
        """
        检查终端是否有效

        :return:
        """
        try:
            self.ws = await websockets.connect(self.end_point, extra_headers={
                "Authorization": self.token
            })
            await self.ws.recv()
            return True
        except Exception as e:
            logger.warn(f'Validate with error: {e}')
            return False

    async def event_looper(self):
        from .event import EventFactory
        logger.info('Start event looper.')

        while True:
            try:
                while msg := await self.ws.recv():
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
                        event = EventFactory(self, raw)
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
        logger.info(f'{self.cached_group_name(gid)}({gid}) <- {msg}')
        if gid == 114514191:
            logger.warn('Maybe this msg is sent from example plugins, ignored.')
            return False
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
        if uid == 114514191:
            logger.warn('Maybe this msg is sent from example plugins, ignored.')
            return False
        return await self.send_request('send_private_msg', data) is not None

    def cached_group_name(self, gid: int) -> str:
        if gid in self._group_cache:
            return self._group_cache[gid].group_name
        self._loop.create_task(self.get_group_info(gid))
        return '<loading>'

    async def get_group_info(self, gid: int) -> GroupInfo:
        """
        获取群信息

        :param gid: 群号
        :return:
        """
        data: dict = await self.send_request('get_group_info', {'group_id': gid})
        group = GroupInfo(**data)
        self._group_cache[gid] = group
        return group

    async def get_group_list(self) -> List[GroupInfo]:
        """
        获取群列表

        :return:
        """
        data: list = await self.send_request('get_group_list', {})
        res = []
        for i in data:
            group = GroupInfo(**i)
            self._group_cache[group.group_id] = group
            res.append(group)
        return res
