import socket
import logging
from concurrent.futures import ThreadPoolExecutor

from .request import Request
from .proxy import http_local
from .utility import IgnoreCaseDict
from .constants import MAX_SIZE, DEFAULT_ENCODE, HeaderKey


class WebServer:
    def __init__(self, *, host='', port=8000, backlog=512):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.address = (host, port)

    def run(self, application):
        print('web server start...')
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        _socket.bind(self.address)
        print('web server bind address:', self.address)
        _socket.listen(self.backlog)
        with ThreadPoolExecutor() as pool:
            while True:
                new_socket, ip_port = _socket.accept()
                pool.submit(self.service_client, new_socket, ip_port, application)

    def service_client(self, _socket, ip_port, application):
        try:
            content = self.receive(_socket, ip_port)
            http_local.request = content
        except Exception as e:
            print(f'parse error', e)
        else:
            response = application()
            _socket.send(response.encode(DEFAULT_ENCODE))
        finally:
            _socket.close()

    @staticmethod
    def receive(_socket, ip_port):
        try:
            content = _socket.recv(MAX_SIZE)
            line_header, body = content.split(b'\r\n\r\n')
            line, *headers_raw = line_header.split(b'\r\n')
            headers = IgnoreCaseDict()
            for header in headers_raw:
                k, v = header.decode(DEFAULT_ENCODE).split(':', maxsplit=1)
                headers[k] = v.strip()
            method, path, protocol_version = line.decode(DEFAULT_ENCODE).split(' ')
            content_length = int(headers.get(HeaderKey.CONTENT_LENGTH, 0))
            while len(body) < content_length:
                # body += socket_.recv(content_length - len(body), socket.MSG_WAITALL)
                body += _socket.recv(MAX_SIZE)
            return Request(method, path, protocol_version, headers, body, ip_port)
        except Exception as e:
            logging.exception(e)
            raise e
