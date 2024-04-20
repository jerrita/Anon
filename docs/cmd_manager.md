# CommandManager

命令管理器是一种 Plugin 的特殊用法，可用于快速开发，使用方法如 `plugins.example.cmd`：

```python
import datetime

from anon.event import MessageEvent
from anon.plugin import PluginManager

date_usage = """Usage: date
此命令无需任何参数"""


@PluginManager().register_cmd(['date', '几点了'], brif='获取现在的时间',
                              usage=date_usage)
async def date(event: MessageEvent, args):
    await event.reply(str(datetime.datetime.now()), quote=False)

```

## 注意事项
- 在匹配到对应命令后，`PluginManager` 会阻止消息向后优先级的插件传递，意味着每条匹配的消息最多只会有一个处理函数被调用。 
- 这意味着重名命令，总会用最先注册的插件处理。
- on_cmd 若返回 True 值，则会自动回复此插件的 Usage，这在错误处理中应该有用。
- 默认 `cmd` 消息的 `prefix` 为 `%`，如果你想更改，请在 anon 注册时，加入额外启动参数 `cmd_prefix`
- 如果你仍想让消息继续向下传递，则你应手动创建插件，例如:

```python
from anon.event import MessageEvent, Event
from anon.plugin import PluginManager, Plugin


class ExamplePlugin(Plugin):
    async def on_cmd(self, event: MessageEvent, args: list):
        pass

    def prevent_after(self, event: Event) -> bool:
        return False


PluginManager().register_plugin(ExamplePlugin(
    keywords=['example'],
    brif='example plugin',
    usage='Usage: example'
))
```