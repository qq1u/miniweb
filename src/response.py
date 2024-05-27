from .proxy import http_local
from .utility import dict2str
from .constants import HeaderKey, ContentType, ContentTypeCharset


class Response:
    def __init__(self, body, headers=None, status_code=200):
        self.body = body
        self.headers = headers or {HeaderKey.CONTENT_TYPE: ContentType.HTML}
        self.status_code = status_code

    def get_str(self):
        response_line = (
            f"{http_local.request.protocol_version} {self.status_code} OK\r\n"
        )
        if isinstance(self.body, dict):
            self.body = dict2str(self.body)
            self.headers[HeaderKey.CONTENT_TYPE] = ContentTypeCharset.JSON
        response_headers = ""
        for k, v in self.headers.items():
            response_headers += f"{k}: {v}\r\n"
        return response_line + response_headers + "\r\n" + self.body
