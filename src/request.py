import json
from urllib.parse import urlsplit, parse_qs

from .constants import HeaderKey, ContentType, DEFAULT_ENCODE


class Request:
    def __init__(self, method, path, protocol_version, headers, body, ip_port):
        self.method = method
        self.protocol_version = protocol_version
        self.headers = headers
        self.body = body
        self.ip_port = ip_port
        self.json = self.str2dict()

        split = urlsplit(path)
        self.path = split.path
        self.args = parse_qs(split.query)

    def str2dict(self):
        if self.headers.get(HeaderKey.CONTENT_TYPE, '').startswith(ContentType.JSON):
            return json.loads(self.body.decode(DEFAULT_ENCODE))

    def __repr__(self):
        return '<Request: %s>' % self.__dict__
