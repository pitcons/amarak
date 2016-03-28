# encoding: utf8

def smart_encode(value):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value

def smart_decode(value):
    if isinstance(value, str):
        return value.decode('utf-8')
    else:
        return value
