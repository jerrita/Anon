# Anon Framework

> 开发中

这是 QQ Bot 框架 [saaya](https://github.com/jerrita/saaya) 的 next
版本，用于对接 [OpenShamrock](https://github.com/whitechi73/OpenShamrock) 的 OneBot 协议变体。

## OneBot Connect 支持

- [x] 正向 WebSocket

## 快速开始

> 本项目采用代码内文档形式，插件开发请采用 PyCharm 获得良好的体验。

### OpenShamrock 部署

略，你需要打开 `正向 Websocket` 并暴露出可被 anon 访问的接口

### 插件开发规范

基本入口文件如 `main.py`, 你可以通过 `register_plugin` 来基于当前目录注册插件:

```python
import logging

from anon import Bot
from anon.logger import logger

logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    anon = Bot('192.168.5.145:5800', '114514')
    anon.register_plugins([
        'plugins.example.ping',
        'plugins.example.reply'
    ])
    anon.loop()
```

你可以采用以下两种方式编写插件：

1. 匿名插件

```python
from anon.plugin import PluginManager
from anon.event import MessageEvent

pm = PluginManager()


@pm.register_event([MessageEvent])
async def ping(event: MessageEvent):
    if event.raw == 'ping':
        await event.reply('pong')
```

2. 自定义插件类型

```python
from anon.plugin import Plugin, PluginManager
from anon.event import MessageEvent


class MyPlugin(Plugin):
    def on_load(self):
        self.interested = [MessageEvent]

    async def on_event(self, event: MessageEvent):
        if event.raw == 'ping':
            await event.reply('pong')


PluginManager().register_plugin(MyPlugin())
```

### PluginManager 说明

- 一切插件将由 `PluginManager` 管理，并在相应的生命周期中调用对应函数。
- Plugin 实现了默认事件过滤器，可通过事件类型过滤事件调用响应函数。
- 在 `register_event` 中，你可以不传参以监听所有事件，或是传如感兴趣的事件类型以进行基础过滤。
- 若你采用自定义插件的形式，基础过滤器会以 `self.interested` 为基准，你可能需要在 `on_load` 中对其进行初始化。
- 所有的 `on_event` 事件均为异步，`on_load` 均为同步。
- 若你需要高级过滤，可以重载 `self.event_filter` 函数，同时满足默认过滤器与此过滤器的事件才会被传入 `on_event`。
- 若你需要获取当前 bot 实例，放心使用 `from anon import Bot` 然后 `bot = Bot()` 即可，这是单例模式。

## Roadmap

- [x] 基础功能 (插件系统，基本组件)
- [ ] 权限管理 
- [ ] 容器化部署
- [ ] 视频/语音
- [ ] 元事件/系统消息
- [ ] ???

## Resources

- [OpenShamrock](https://github.com/whitechi73/OpenShamrock)