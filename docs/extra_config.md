# 高级配置

你可以在 anon 启动时传入一些高级参数，例如

```python
from anon import Bot

anon = Bot('127.0.0.1:5800', '1114514',
           storage_dir='/var/run/anon',
           log_file='/dev/null',
           def_user=114514191,
           cmd_prefix='%')
```

可选项顾名思义，所有可配置项参见 `anon.common.AnonExtraConfig`