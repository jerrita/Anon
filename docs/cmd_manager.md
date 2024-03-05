# CommandManager

命令管理器是一个内置插件，可用于快速开发，使用方法如 `plugins.example.cmd`：

```python
import datetime

from anon.event import MessageEvent
from anon.plugin import CommandManager

date_usage = """Usage: date
此命令无需任何参数"""


@CommandManager().register_handler('date', '展示现在的时间', usage=date_usage, alter=['现在几点了'])
async def date(event: MessageEvent, args):
    await event.reply(str(datetime.datetime.now()))

```

## 注意事项

1. `CmdManager` 使用内置的 [CommandPlugin](../anon/plugin/builtins/command.py) 插件对消息进行前处理，由于是内置插件，优先级最高。 
2. 在匹配到对应命令后，`CmdManager` 会阻止消息向后优先级的插件传递，意味着每条匹配的消息最多只会有一个处理函数被调用。
3. 这意味着重名命令，以及重名 `alter`，总会用最先注册的插件处理。
4. 如果你仍想让消息继续向下传递，则你应手动重写 `CommandPlugin`