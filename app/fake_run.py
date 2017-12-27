import logging
from app import settings
from app.service import kline_handler
from app.service import mongodb

logger = logging.getLogger(__name__)

# 不通过websocket，直接通过读取到的数据库的值调用kline_handler
if __name__ == "__main__":
    index_dict = {}
    currency_dict = {}
    if mongodb:
        for currency in settings.COINS.keys():
            index_dict["market_%susdt_kline_1min" % currency.lower()] = 0

        for collection_name in index_dict.keys():
            collection = mongodb.get_collection(collection_name)
            currency_dict[collection_name] = collection.find_one({}, skip=index_dict[collection_name])

        while True:
            # 从currency_dict中找到ts最小的key，更新该key
            min_ts_document_key = min(currency_dict.items(), key=lambda x: x[1]['_id'])[0]
            collection = mongodb.get_collection(min_ts_document_key)
            index_dict[min_ts_document_key] += 1
            kline_handler.handle_raw_message(currency_dict[min_ts_document_key])
            currency_dict[min_ts_document_key] = collection.find_one(
                {'ts': {'$gt': 1000 * int(settings.SIMULATE_START.timestamp()),
                        '$lt': 1000 * int(settings.SIMULATE_END.timestamp())}}, skip=index_dict[min_ts_document_key])
            if currency_dict[min_ts_document_key] is None:
                break
    print("已完成处理")
