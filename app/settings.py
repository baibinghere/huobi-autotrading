import logging

# 日志配置文件
_filename = None
_format = "%(asctime)-15s [%(levelname)s] [%(name)s] %(message)s"
_datefmt = "%Y/%m/%d %H:%M:%S"
_level = logging.INFO

if _filename:
    handlers = [logging.StreamHandler(), logging.FileHandler(_filename)]
else:
    handlers = [logging.StreamHandler()]

logging.basicConfig(format=_format, datefmt=_datefmt, level=_level, handlers=handlers)

# 目前查询的$symbol均为：<货币>USTD (可选：{ USDT, BTC })
# 时间间隔均为1min(可选：{ 1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year })
SYMBOL = "USDT"
PERIOD = "1min"

# 计算n分钟内的涨跌幅
N_MINUTES_STATE = 10

# 设定参考货币的类型及权重
CURRENCIES = {
    "BTC": {
        "WEIGHT": 1
    },
    "BCH": {
        "WEIGHT": 1
    },
    "ETH": {
        "WEIGHT": 1
    },
    "LTC": {
        "WEIGHT": 1
    },
    "XRP": {
        "WEIGHT": 1
    },
    "DASH": {
        "WEIGHT": 1
    },
    "ETC": {
        "WEIGHT": 1
    },
    "EOS": {
        "WEIGHT": 1
    },
    "ZEC": {
        "WEIGHT": 1
    },
    "OMG": {
        "WEIGHT": 1
    }
}
