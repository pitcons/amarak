# encoding: utf8
from weakref import WeakValueDictionary


class IdentityMap(object):

    def __init__(self):
        self.clear()

    def get(self, obj_type, key):
        return self.objects[obj_type].get(key)

    def put(self, obj_type, key, obj):
        self.objects[obj_type][key] = obj

    def clear(self):
        self.objects = {
            'schemes': WeakValueDictionary(),
            'concepts': WeakValueDictionary(),
            'relations': WeakValueDictionary(),
            'links': WeakValueDictionary()
        }
