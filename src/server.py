import socket
import logging
from concurrent.futures import ThreadPoolExecutor

from .request import Request
from .proxy import http_local
from .utility import IgnoreCaseDict
from .constants import MAX_SIZE, DEFAULT_ENCODE


class WebServer:
    def __init__(self, *, host="", port=8000, backlog=512):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.address = (host, port)

    def run(self, application):
        print("web server start...")
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        _socket.bind(self.address)
        print("web server bind address:", self.address)
        _socket.listen(self.backlog)
        with ThreadPoolExecutor() as pool:
            while True:
                new_socket, ip_port = _socket.accept()
                pool.submit(self.service_client, new_socket, ip_port, application)

    def service_client(self, _socket, ip_port, application):
        try:
            content = self.receive(_socket, ip_port)
        except Exception as e:
            print(f"parse error", e)
        else:
            if content:
                http_local.request = content
                response = application()
                _socket.send(response.encode(DEFAULT_ENCODE))
        finally:
            _socket.close()

    @classmethod
    def receive(cls, _socket, ip_port):
        _socket.settimeout(0)
        content = b""

        while True:
            try:
                chunk = _socket.recv(MAX_SIZE)
            except BlockingIOError:
                break
            else:
                content += chunk
                if len(chunk) < MAX_SIZE:
                    break
        if not content:
            return

        try:
            method, path, protocol_version, headers, body = cls.parse(content)
        except Exception as e:
            logging.exception(e)
            logging.error(content)
            raise e
        else:
            return Request(method, path, protocol_version, headers, body, ip_port)

    @staticmethod
    def parse(content):
        line_header, body = content.split(b"\r\n\r\n")
        line, *headers_raw = line_header.split(b"\r\n")
        headers = IgnoreCaseDict()
        for header in headers_raw:
            k, v = header.decode(DEFAULT_ENCODE).split(":", maxsplit=1)
            headers[k] = v.strip()
        method, path, protocol_version = line.decode(DEFAULT_ENCODE).split(" ")
        return method, path, protocol_version, headers, body
