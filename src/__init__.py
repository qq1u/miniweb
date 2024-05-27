# encoding: utf-8

__all__ = ["Application", "WebServer", "Request", "Response", "request"]

from .request import Request
from .server import WebServer
from .response import Response
from .proxy import request
from .application import Application


if __name__ == "__main__":
    app = Application()

    @app.route("/")
    def index():
        return "Hello World"

    WebServer().run(app)
