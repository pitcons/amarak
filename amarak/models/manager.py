# encoding: utf8

class Manager(object):

    def __init__(self, klass):
        self._objects = []
        self._changes = []
        self._klass = klass

    def _add_raw(self, *args, **kwargs):
        obj = self._klass(*args, **kwargs)
        self._objects.append(obj)
        return obj

    def add(self, *args, **kwargs):
        obj = self._add_raw(*args, **kwargs)
        self._changes.append(('new', obj))

    def _remove_raw(self, obj):
        self._objects.remove(obj)

    def remove(self, obj):
        self._remove_raw(obj)
        self._changes.append(('remove', obj))

    def remove_by_id(self, obj_id):
        self._changes.append(('remove_by_id', obj_id))

    def all(self):
        return self._objects

    def clear(self):
        for label in self._objects:
            self.remove(label)

    # def to_python(self):
    #     return [
    #         {'id': label.id,
    #          'lang': label.lang,
    #          'type': label.type,
    #          'literal': label.literal}
    #         for label in self.all()
    #     ]
