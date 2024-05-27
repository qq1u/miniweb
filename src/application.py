from functools import wraps

from .proxy import http_local
from .utility import dict2str
from .response import Response
from .server import WebServer
from .constants import HeaderKey, ContentTypeCharset


class Method:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ViewFunction:
    def __init__(self, methods, function):
        self.methods = methods
        self.function = function


class Application:
    def __init__(self):
        self.url_func_map = {}
        self.http_404 = Response(
            "<html><body>Not Found 404</body></html>", status_code=404
        )
        self.http_405 = Response(
            "<html><body>Method Not Allowed</body></html>", status_code=405
        )
        self.http_500 = Response(
            "<html><body>Server Internal Error</body></html>", status_code=500
        )

    def route(self, path, methods=None):
        if methods is None:
            methods = [Method.GET]

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
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
                response = Response(
                    dict2str(response),
                    {HeaderKey.CONTENT_TYPE: ContentTypeCharset.JSON},
                )
            if not isinstance(response, Response):
                raise TypeError("Should return Response or dict or str")
        except Exception as e:
            print("Server Internal Error", e)
            response = self.http_500
        return response.get_str()

    def run(self, host="", port=8000):
        WebServer(host=host, port=port).run(self)
