# Plugin

若需直接使用示例插件，你可能需要启动时在 [高级配置](./extra_config.md) 中指定：

```yaml
def_user: int
def_group: int
```

来定义发送消息时的默认操作，未定义时无需担心，向 `114514191` 发送消息在 protocol 实现中会被忽略 (x

# PluginManager

- 一切插件将由 `PluginManager` 管理，并在相应的生命周期中调用对应函数。
- Plugin 实现了默认事件过滤器，可通过事件类型过滤事件调用响应函数。
- 在 `register_event` 中，你可以不传参以监听所有事件，或是传如感兴趣的事件类型以进行基础过滤。
- 若你采用自定义插件的形式，基础过滤器会以 `self.interested` 为基准，此基准将在插件实例化时传入，你也可在生命周期内动态更改。
- 所有 Plugin 事件均为异步。
- 若你需要高级过滤，可以重载 `self.event_filter` 函数，同时满足默认过滤器与此过滤器的事件才会被传入 `on_event`。
- 若你需要获取当前 bot 实例，放心使用 `from anon import Bot` 然后 `bot = Bot()` 即可，这是单例模式。
