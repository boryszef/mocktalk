import re


class Script:
    """Maintain a (question, response) list"""

    def __init__(self, *data):
        self.data = [(re.compile(key), value) for key, value in data]

    def match(self, item):
        item = item.decode('UTF-8')
        for k, v in self.data:
            if k.match(item):
                return v.encode('UTF-8')
        return None
