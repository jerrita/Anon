import logging
import colorlog

log_colors_config = {
    'DEBUG': 'white',  # cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

logger = logging.getLogger('anon_logger')

# Console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# File
# file_handler = logging.FileHandler(filename=config.example['log_path'], mode='a', encoding='utf8')
# file_handler.setLevel(logging.INFO)

# 日志输出格式
console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s[%(asctime)s.%(msecs)03d %(filename)11s:%(lineno)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S',
    log_colors=log_colors_config
)
console_handler.setFormatter(console_formatter)

# file_formatter = logging.Formatter(
#     fmt='[%(asctime)s.%(msecs)03d %(filename)s] [%(levelname)s] : %(message)s',
#     datefmt='%Y-%m-%d  %H:%M:%S'
# )
# file_handler.setFormatter(file_formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    # logger.addHandler(file_handler)

console_handler.close()
# file_handler.close()
