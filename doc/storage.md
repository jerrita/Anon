# 存储管理

```python
from anon.storage import Storage

storage = Storage('core')
```

Storage 是一个特殊的组件，你可以用此类进行数据持久化等操作。插件的高级配置会存在 `core` 存储中。

## 建议用法

- Storage 名称设置为 `<author>-<plugin_name>`
- 谨慎使用 `core` 存储

## 特殊操作

- 你可以使用 `storage.close()` 来关闭文件刷新来使数据仅存在内存中，可以用此方式实现插件间 `IPC`。
- 若对数据丢失不敏感，可以设置 `storage.flush_after_set = False` 来关闭实时刷新。