import asyncio
import json
import uuid
from asyncio import Queue
from typing import Dict, List, Union

import websockets
from websockets import ConnectionClosedError
from websockets import WebSocketClientProtocol

from .common import *
from .logger import logger
from .message import Message, Convertable
from .utils import any_data


class Protocol:
    ws: WebSocketClientProtocol
    _group_cache: Dict[int, GroupInfo]
    _pending_requests: Dict[str, Queue] = {}

    def __init__(self, ep: str, token: str):
        self.end_point = f'ws://{ep}' if not ep.startswith('ws') else ep
        self.token = token
        self._loop = asyncio.new_event_loop()
        self._group_cache = {}

    async def broad_cast(self, event_raw: dict):
        raise NotImplementedError

    async def send_request(self, func: str, data: dict) -> Union[dict, list]:
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
            return {}

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

    async def event_loop(self):
        logger.info('Start event looper.')

        tasks = set()

        while True:
            try:
                while msg := await self.ws.recv():
                    logger.debug(msg)
                    raw = json.loads(msg)
                    if 'echo' in raw:
                        _uuid = raw['echo']
                        if _uuid in self._pending_requests:
                            logger.debug(f'Session resume: {_uuid}')
                            self._pending_requests[_uuid].put_nowait(raw)
                        else:
                            logger.warn(f'Received a message with unknown UUID: {_uuid}')
                    else:
                        task = asyncio.create_task(self.broad_cast(raw))
                        tasks.add(task)
                        task.add_done_callback(tasks.discard)
            except ConnectionClosedError:
                logger.warn('WS Closed. Reconnecting...')
                self.ws = await websockets.connect(self.end_point, extra_headers={
                    "Authorization": self.token
                })
            except Exception as e:
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
        return await self.send_request('send_group_msg', data) is not None

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
        if gid in self._group_cache:
            return self._group_cache[gid]
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

    async def shamrock_download_file(self, url: str = None, name: str = None, base64: str = None, thread_cnt: int = 2,
                                     headers: str = None) -> str:
        """
        用法二选一：

        1.仅发送url，由Shamrock自己访问该url来下载文件

        2.仅发送文件base64，Shamrock解码后直接转存为文件

        url和base64至少一个不能为空，同时发送url和base64时，使用url

        :param url: 文件链接
        :param name: 保存文件重命名（可选）
        :param base64: 文件 base64
        :param thread_cnt: 下载线程数
        :param headers: headers
        :return: 文件存储路径（Shamrock 中）
        """
        if not url and not base64:
            logger.warn('Download file without url and base64!')
            return ''

        data = any_data({
            "url": url,
            "name": name,
            "base64": base64,
            "thread_cnt": thread_cnt,
            "headers": headers
        })

        res = await self.send_request('download_file', data)
        return res.get('file')

    async def upload_private_file(self, uid: int, file: str = None, name: str = None) -> int:
        """
        上传私聊文件

        :param uid: 私聊对象 qq 号
        :param file: 文件路径
        :param name: 文件名
        :return: file md5
        """
        data = any_data({
            "user_id": uid,
            "file": file,
            "name": name
        })
        return (await self.send_request('upload_private_file', data)).get('md5')

    async def upload_group_file(self, gid: int, file: str = None, name: str = None) -> int:
        """
        上传群文件

        :param gid: 群号
        :param file: 文件路径
        :param name: 文件名
        :return: file md5
        """
        data = any_data({
            "group_id": gid,
            "file": file,
            "name": name
        })
        return (await self.send_request('upload_group_file', data)).get('md5')
