# encoding: utf8

class ParentsManager(object):

    def __init__(self, parents):
        self._parents = parents or []
        self._changes = []

    def _add_raw(self, scheme):
        self._parents.append(scheme)

    def _remove_raw(self, scheme):
        self._parents.append(scheme)

    def add(self, scheme):
        self._add_raw(scheme)
        self._changes.append(('new', scheme))

    def remove(self, scheme):
        self._remove_raw(scheme)
        self._changes.append(('remove', scheme))

    def all(self):
        return self._parents

    def clear(self):
        for parent in self._parents:
            self.remove(parent)
