import cv2
import time
import numpy as np
import os
from timeit import time
import sys
import queue
from threading import Thread
import subprocess as sp
from socket import *
import json

IP_list = ["192.168.1.101", "192.168.1.102", "192.168.1.37", '192.168.1.43']


def sub_process(cameraIP, threshold):
    command = [
        '/home/yy/anaconda3/envs/CenterNet/bin/python',
        os.getcwd() + '/' + 'src/vidoe_demo.py', '--cameraIP', cameraIP,
        "--threshold",
        str(threshold)
    ]
    framechild = sp.Popen(command)
    # time.sleep(5)
    # framechild.kill()
    return framechild


def doConnect(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((host, port))
    except:
        pass
    return sock


def tcp_receive():
    # 本机socket
    local_socket = socket(AF_INET, SOCK_STREAM)
    local_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    address = ('192.168.1.233', 7788)
    local_socket.bind(address)
    #listen里的数字表征同一时刻能连接客户端的程度.
    local_socket.listen(128)

    # 对方socket
    des_socket = socket(AF_INET, SOCK_STREAM)
    # 链接服务器
    des_ip, des_port = '192.168.1.112', 10002
    des_socket.connect((des_ip, des_port))
    #des_socket.connect(('192.168.1.233', 10002))

    all_cams = {}
    for ip in IP_list:
        all_cams[ip] = {'sp': '', 'funcControStatus': 0}

    while True:
        client_socket, clientAddr = local_socket.accept()
        print('accept-------------------')
        while True:
            data = client_socket.recv(1024).decode("utf-8")
            if len(data):
                print(data)
                print('------------------------------------------------')
                if data == 'ping':
                    continue

                data = json.loads(data)
                messageId = data['messageId']
                cameraIP = data['cameraIP']
                function = data['function']
                threshold = data['params']['threshold']
                messageName = data['messageName']
                if messageName == 'FuncControlRequest':
                    funcControStatus = data['funcControStatus']
                    if funcControStatus == 0 and all_cams[cameraIP][
                            'funcControStatus'] == 1:
                        all_cams[cameraIP]['sp'].kill()
                        all_cams[cameraIP]['funcControStatus'] = 0
                        print('kill-------------------')
                        des_socket = response(des_socket, data, 1, des_ip,
                                              des_port)

                    elif funcControStatus == 1 and all_cams[cameraIP][
                            'funcControStatus'] == 0:
                        cameraIP_sp = sub_process(cameraIP, threshold)
                        all_cams[cameraIP]['sp'] = cameraIP_sp
                        all_cams[cameraIP]['funcControStatus'] = 1
                        des_socket = response(des_socket, data, 1, des_ip,
                                              des_port)
                    else:
                        # 已经开启或者关闭
                        des_socket = response(des_socket, data, 1, des_ip,
                                              des_port)

                else:
                    responseStatus = data['responseStatus']
            else:
                break


def response(des_socket, data, responseStatus, des_ip, des_port):
    response_data = {
        "messageName": "FuncControlRequest",
        "messageId": data['messageId'],
        "cameraIP": data['cameraIP'],
        "function": data['function'],
        'responseStatus': responseStatus
    }
    response_data = json.dumps(response_data)
    try:
        des_socket.send(response_data.encode("utf-8"))
    except error:
        print(
            "\r\nsocket error,do reconnect--ObjDetection--------------------- "
        )

        des_socket = doConnect(des_ip, des_port)
        #des_socket.send(response_data.encode("utf-8"))

    return des_socket


if __name__ == "__main__":
    tcp_receive()
