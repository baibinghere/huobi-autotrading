import json
import numpy
import logging
import http.client
import statistics

from app import settings
from app.service import ma
from collections import deque

###
# 本文件对传入的价格信息进行处理
###

# 记录每种虚拟货币的每笔交易
transaction_dict = {}
# 记录每种虚拟货币在1分钟内的分析数据，队列长度设置为10，即10分钟内的数据
analyzed_queue_dict = {}
# 记录10分钟内的"价格"变化，这里的"价格"目前直接用close的差计算，以后考虑通过交易量，标准差等计算
price_change_dict = {}

logger = logging.getLogger(__name__)


def get_usdt_sell_price():
    conn = http.client.HTTPSConnection("api-otc.huobi.pro")
    conn.request("GET", "/v1/otc/trade/list/public?coinId=2&tradeType=0&currentPage=1&payWay=&country=")
    res = conn.getresponse()
    try:
        data = json.loads(res.read().decode("utf-8"))['data']
        return statistics.mean(list(map(lambda x: x['price'], data)))
    except Exception as exp:
        logger.error("无法获得USDT交易卖出价：" + str(exp))
    return "失败"


def send_mail(title, content):
    if not ma:
        return
    with ma.SMTP() as s:
        s.send(settings.MAIL_RECEIPIENTS, content, title)


def trigger_price_increase_action(total_price_change):
    content = "价格上升：%.2f", total_price_change
    logger.warning(content)
    send_mail(content, "火币网价格上升")


def trigger_price_decrease_action(total_price_change):
    content = "价格下降：%.2f", total_price_change
    logger.warning(content)
    send_mail(content, "火币网价格下降")


def predict_and_notify(total_price_change):
    usdt_sell_price = get_usdt_sell_price()
    context = "价格变动：%.4f；USDT当前售价：%.2f" % (total_price_change, usdt_sell_price)
    if total_price_change >= settings.PRICE_ALERT_INCREASE_POINT:
        trigger_price_increase_action(total_price_change)
    if total_price_change <= settings.PRICE_ALERT_DECREASE_POINT:
        trigger_price_decrease_action(total_price_change)
    logger.info(context)


def perform_calculation():
    total_price_change = 0
    # 当收集满所有货币的10分钟内交易额后，计算才有意义
    if not len(price_change_dict) == len(settings.CURRENCIES):
        return
    # 取出price_change_dict中的所有数据，并根据settings中设置的WEIGHT决定是否购买
    for channel, price in price_change_dict.items():
        currency = channel.split(".")[1].replace(settings.SYMBOL.lower(), "").upper()
        weight = settings.CURRENCIES[currency]["WEIGHT"]
        total_price_change += price * weight
    total_price_change /= sum(list(map(lambda x: x["WEIGHT"], settings.CURRENCIES.values())))
    predict_and_notify(total_price_change)


# 火币的交易量相关信息每60秒重置一次
def update_data(channel):
    # 从transaction_dict[channel]中获取
    # 1. 1分钟内的涨跌幅
    # 2. 价格变化幅度（标准差）
    # 3. 1分钟内的交易额
    # 4. 1分钟最后一笔交易的价格
    if channel not in analyzed_queue_dict:
        analyzed_queue_dict[channel] = deque("", settings.N_MINUTES_STATE)
    data = {
        'change': transaction_dict[channel][-1]['tick']['close'] - transaction_dict[channel][0]['tick']['close'],
        'vol': transaction_dict[channel][-1]['tick']['vol'],
        'mean': numpy.std(list(map(lambda x: x['tick']['close'], transaction_dict[channel]))),
        'close': transaction_dict[channel][-1]['tick']['close'],
    }
    analyzed_queue_dict[channel].append(data)
    logger.debug("updated: " + channel)
    if len(analyzed_queue_dict[channel]) == settings.N_MINUTES_STATE:
        # 10分钟以内的"价格"变化
        price_change_dict[channel] = (analyzed_queue_dict[channel][-1]['close'] - analyzed_queue_dict[channel][0][
            'close']) * 100 / analyzed_queue_dict[channel][0]['close']
    perform_calculation()


def handle_raw_message(msg_dict):
    channel = msg_dict['ch']
    if channel not in transaction_dict:
        # 创建长度为N_TRANSACTION的queue
        transaction_dict[channel] = [msg_dict]
    else:
        if transaction_dict[channel][-1]['tick']['count'] > msg_dict['tick']['count']:
            # 每60秒计算一次已有数据，然后重置该channel
            update_data(channel)
            transaction_dict[channel] = [msg_dict]
        else:
            transaction_dict[channel].append(msg_dict)
