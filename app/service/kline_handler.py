import logging

from app import settings
from collections import deque
import numpy

###
# 本文件对传入的价格信息进行处理
###

# 记录每种虚拟货币的每笔交易
transaction_dict = {}
# 记录每种虚拟货币在1分钟内的分析数据，队列长度设置为10，即10分钟内的数据
analyzed_queue_dict = {}

# 思路：价格在一定位置保留一段时间则认为在涨/跌
# 根据以下数据判断整体是否在涨跌
# 1. 时间段
# 2. 涨幅/跌幅
# 3. 交易数量
# 4. 交易金额
# 火币的交易量相关信息每60秒重置一次

def perform_calculation(channel):
    # 从transaction_dict[channel]中获取
    # 1. 1分钟内的涨跌幅
    # 2. 价格变化幅度（标准差）
    # 3. 1分别内的交易额
    if channel not in analyzed_queue_dict:
        analyzed_queue_dict[channel] = deque("", settings.N_MINUTES_STATE)
    # todo: 目前analyzed_queue_dict[channel]中保存的是dict，以后将保存的是简单的数值，数值由以下参数计算出来
    data = {
        'change': transaction_dict[channel][-1]['tick']['close'] - transaction_dict[channel][0]['tick']['close'],
        'vol': transaction_dict[channel][-1]['tick']['vol'],
        'mean': numpy.std(list(map(lambda x: x['tick']['close'], transaction_dict[channel])))
    }
    logger = logging.getLogger(channel)
    logger.info(str(data))
    analyzed_queue_dict[channel].append(data)


def handle_raw_message(msg_dict):
    channel = msg_dict['ch']
    if channel not in transaction_dict:
        # 创建长度为N_TRANSACTION的queue
        transaction_dict[channel] = [msg_dict]
    else:
        if transaction_dict[channel][-1]['tick']['count'] > msg_dict['tick']['count']:
            # 每60秒计算一次已有数据，然后重置该channel
            perform_calculation(channel)
            transaction_dict[channel] = [msg_dict]
        else:
            transaction_dict[channel].append(msg_dict)
