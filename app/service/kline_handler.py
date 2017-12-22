import queue

###
# 本文件对传入的价格信息进行处理
###

queue_dict = {}

def handle_raw_message(msg_dict):
    # if msg_dict['ch'] not in queue_dict:
    #     # 创建queue
    import pprint
    pprint.pprint(msg_dict)
    pass