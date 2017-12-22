from app import settings
from collections import deque

###
# 本文件对传入的价格信息进行处理
###

transaction_queue_dict = {}
price_change_dict = {}


# 根据以下数据判断整体是否在涨跌
# 1. 时间段
# 2. 涨幅/跌幅
# 3. 交易数量
# 4. 交易金额
# 火币的交易量相关信息每60秒重置一次

def calculate_price_change():
    for key, value in transaction_queue_dict.items():
        if len(value) <= 1: continue
        close_price_difference = float((value[-1]['tick']['close'] - value[0]['tick']['close']) * 1000)
        time_difference = value[-1]['ts'] - value[0]['ts']
        price_change_dict[key] = round(close_price_difference / time_difference, 10)
        import pprint
        pprint.pprint(value[-1])


def handle_raw_message(msg_dict):
    channel = msg_dict['ch']
    if channel not in transaction_queue_dict:
        # 创建长度为N_TRANSACTION的queue
        transaction_queue_dict[channel] = deque("", settings.N_TRANSACTION)
    transaction_queue_dict[channel].append(msg_dict)
    calculate_price_change()
