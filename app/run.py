import gzip
import json
import pprint
import threading

import time
import websocket


def send_message(ws, message_dict, log=False):
    data = json.dumps(message_dict).encode()
    if log:
        print("Sending Message:")
        pprint.pprint(message_dict)
    ws.send(data)


def on_message(ws, message):
    unzipped_data = gzip.decompress(message).decode()
    msg_dict = json.loads(unzipped_data)
    if 'ping' in msg_dict:
        data = {
            "pong": msg_dict['ping']
        }
        send_message(ws, data)
    else:
        print("Recieved Message: ")
        pprint.pprint(msg_dict)


def on_error(ws, error):
    print("Error: " + str(error))
    error = gzip.decompress(error).decode()
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    data = {
        "sub": "market.btcusdt.kline.1min",
        "id": "id1"
    }
    # 订阅K线图
    send_message(ws, data)
    print("thread terminating...")


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "wss://api.huobi.pro/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
    print("done")
