import threading


class Proxy:
    def __init__(self, local, attribute):
        self.local = local
        self.attribute = attribute

    def __getattribute__(self, item):
        local = super().__getattribute__("local")
        attribute = super().__getattribute__("attribute")
        obj = getattr(local, attribute)
        return getattr(obj, item)


http_local = threading.local()
request = Proxy(http_local, "request")
