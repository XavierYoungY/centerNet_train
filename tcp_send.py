from socket import *

import json
import time
data = {
    "messageName": "FuncControlRequest",
    "funcControStatus":0,
    "function": "objectDetection",
    "messageId": 1,
    "cameraIP": "192.168.1.37",
    "params": {
        'threshold': 0.1
    }
}


tcp_socket = socket(AF_INET, SOCK_STREAM)

# 目的信息
server_ip = '192.168.1.233'
server_port = 7789
# 链接服务器
tcp_socket.connect((server_ip, server_port))

while True:
    data_ = json.dumps(data)
    tcp_socket.send(data_.encode("utf-8"))
    # if data["funcControStatus"]==1:
    #     data["funcControStatus"]=0
    # else:
    #     data["funcControStatus"]=1
    time.sleep(20)
    if data['cameraIP']=="192.168.1.37":
        data['cameraIP'] = "192.168.1.43"
    else:
        data['cameraIP'] = "192.168.1.37"
    data_ = json.dumps(data)
    tcp_socket.send(data_.encode("utf-8"))
    time.sleep(20)

