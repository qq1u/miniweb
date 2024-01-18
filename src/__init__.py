# encoding: utf-8

__all__ = ['Application', 'AsyncServer', 'Request', 'Response']

from .request import Request
from .async_server import AsyncServer
from .response import Response
from .application import Application


if __name__ == '__main__':
    app = Application()


    @app.route('/')
    def index():
        return 'Hello World'


    AsyncServer().run(app)
