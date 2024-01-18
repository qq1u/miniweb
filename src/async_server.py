import asyncio
import socket

from .request import Request
from .utility import IgnoreCaseDict
from .constants import MAX_SIZE, DEFAULT_ENCODE


class AsyncServer:

    def __init__(self, *, host="", port=8000):
        self.host = host
        self.port = port
        self.address = (host, port)

    def run(self, application):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        server.setblocking(False)  # async server must set blocking False
        server.bind(self.address)
        server.listen()

        asyncio.run(self.accept(server, application))

    @classmethod
    async def accept(cls, server: socket.socket, application):
        loop = asyncio.get_running_loop()
        while True:
            connect, addr = await loop.sock_accept(server)
            loop.create_task(cls.handler(connect, addr, application))

    @classmethod
    async def handler(cls, connect: socket.socket, addr: tuple[str, str], application):
        content = b""
        loop = asyncio.get_running_loop()
        while chunk := await loop.sock_recv(connect, MAX_SIZE):
            content += chunk
            if len(chunk) < MAX_SIZE:
                break

        # parse data
        try:
            method, path, protocol_version, headers, body = cls.parse(content)
        except Exception as e:
            print("invalid request", e)
        else:
            request = Request(method, path, protocol_version, headers, body, addr)
            response = await application(request)
            await loop.sock_sendall(connect, response.encode(DEFAULT_ENCODE))
        finally:
            connect.close()

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
