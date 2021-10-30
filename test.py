"""
为什么async_requests()，调用requests的请求会出现请求丢失请求体的情况
    看服务端的example1.py里的parse error: 可以看出，都是丢失请求体。

sync_requests()，同步情况下是正常的
"""
import json
import socket
from concurrent.futures import ThreadPoolExecutor

import requests

hello_world = {"Hello": "World"}
sync_requests_responses = []
async_requests_responses = []
async_socket_request_responses = []


def socket_request():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 8000))
    content = f'POST / HTTP/1.1\r\nContent-Type: application/json;charset=utf-8\r\n\r\n{hello_world}'
    s.send(content.encode('utf-8'))
    resp = s.recv(1024)
    async_socket_request_responses.append(resp)
    return resp


def request():
    r = requests.post('http://127.0.0.1:8000', json=hello_world)
    return r


def append(collection, func):
    collection.append(func())


def async_socket_request(times=1000):
    with ThreadPoolExecutor() as pool:
        for _ in range(times):
            pool.submit(append, async_requests_responses, socket_request)
    print(f'total async socket_request times: {times}, responses: {len(async_requests_responses)}')


def async_requests(times=1000):
    with ThreadPoolExecutor() as pool:
        for _ in range(times):
            pool.submit(append, async_requests_responses, request)
    print(f'total async requests times: {times}, responses: {len(async_requests_responses)}')


def sync_requests(times=100):
    for _ in range(times):
        sync_requests_responses.append(request())
    print(f'total request times: {times}, responses: {len(sync_requests_responses)}')


if __name__ == '__main__':
    # async_requests()
    # sync_requests()
    async_requests(10)