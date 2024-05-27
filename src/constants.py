MAX_SIZE = 1024 * 4
DEFAULT_ENCODE = "utf-8"


class HeaderKey:
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"


class ContentType:
    JSON = "application/json"
    HTML = "text/html"


class ContentTypeCharset:
    UTF8_CHARSET = f";charset={DEFAULT_ENCODE}"
    JSON = ContentType.JSON + UTF8_CHARSET
    HTML = ContentType.HTML + UTF8_CHARSET
