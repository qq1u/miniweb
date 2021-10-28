# encoding: utf-8

import json
import socket
import threading
from functools import wraps
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor

CONTENT_TYPE = 'Content-Type'
JSON_TYPE = 'application/json;charset=utf-8'
HTML_TYPE = 'text/html;charset=utf-8'


class Util:
    @staticmethod
    def dict2str(obj, ensure_ascii=False):
        return json.dumps(obj, ensure_ascii=ensure_ascii)


class Proxy:
    def __init__(self, local, attribute):
        self.local = local
        self.attribute = attribute

    def __getattribute__(self, item):
        local = super().__getattribute__('local')
        attribute = super().__getattribute__('attribute')
        obj = getattr(local, attribute)
        return object.__getattribute__(obj, item)


class Request:
    def __init__(self, method, path, version, headers, body, ip_port):
        self.method = method
        self.path = path
        self.version = version
        self.headers = headers
        self.body = body
        self.ip_port = ip_port


class Response:
    def __init__(self, body, headers=None, status_code=200):
        self.body = body
        self.headers = headers or {CONTENT_TYPE: HTML_TYPE}
        self.status_code = status_code

    def get_str(self):
        response_line = f'{http_local.request.version} {self.status_code} OK\r\n'
        if isinstance(self.body, dict):
            self.body = Util.dict2str(self.body)
            self.headers[CONTENT_TYPE] = JSON_TYPE
        response_headers = ''
        for k, v in self.headers.items():
            response_headers += f'{k}: {v}\r\n'
        return response_line + response_headers + '\r\n' + self.body


class ViewFunction:
    def __init__(self, methods, function):
        self.methods = methods
        self.function = function


class Method:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class Application:
    def __init__(self):
        self.url_func_map = {}  # {'/': ViewFunction('', '')}
        self.http_404 = Response('<html><body>Not Found 404</body></html>', status_code=404)
        self.http_405 = Response('<html><body>Method Not Allowed</body></html>', status_code=405)
        self.http_500 = Response('<html><body>Server Internal Error</body></html>', status_code=500)

    def route(self, path, methods=None):
        if methods is None:
            methods = [Method.GET]

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any):
                return func(*args, **kwargs)

            self.url_func_map[path] = ViewFunction(methods, func)
            return wrapper

        return decorator

    def dispatch(self):
        view_func = self.url_func_map.get(http_local.request.path)
        if not view_func:
            return self.http_404
        methods = view_func.methods
        if http_local.request.method not in methods:
            return self.http_405
        return view_func.function()

    def __call__(self):
        try:
            response = self.dispatch()
            if isinstance(response, str):
                response = Response(response)
            elif isinstance(response, dict):
                response = Response(Util.dict2str(response), {CONTENT_TYPE: JSON_TYPE})
            if not isinstance(response, Response):
                raise TypeError('Should return Response or dict or str')
        except Exception as e:
            print('Server Internal Error', e)
            response = self.http_500
        return response.get_str()


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

    def service_client(self, _socket, ip_port, application: Application):
        print(f'from {ip_port}')
        request_byte = _socket.recv(MAX_SIZE)
        try:
            http_local.request = self.parser_request(request_byte.decode('utf-8'), ip_port)
        except Exception as e:
            print('parse error:', e)
        else:
            response = application()
            _socket.send(response.encode('utf-8'))
        finally:
            _socket.close()

    @staticmethod
    def parser_request(request_str, ip_port):
        header, body = request_str.split('\r\n\r\n')
        request_line, *headers = header.split('\r\n')
        method, path, version = request_line.split(' ')
        headers_dict = {}
        for header in headers:
            k, v = header.split(':', maxsplit=1)
            headers_dict[k.strip()] = v.strip()
        return Request(method, path, version, headers_dict, body, ip_port)


MAX_SIZE = 1024 * 4

http_local = threading.local()
request = Proxy(http_local, 'request')

if __name__ == '__main__':
    app = Application()


    @app.route('/')
    def index():
        return 'Hello World'


    WebServer().run(app)
