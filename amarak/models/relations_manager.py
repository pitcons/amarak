# encoding: utf8
from .relation import Relation


class RelationsManager(object):

    def __init__(self):
        self._relations = []
        self._changes = []

    def _add_raw(self, relation):
        self._relations.append(relation)

    def add(self, relation):
        self._add_raw(relation)
        self._changes.append(('new', relation))

    def to_python(self):
        return [relation.to_python() for relation in self._relations]

    def all(self):
        return self._relations

    def _remove_raw(self, relation):
        self._relations.remove(relation)

    def remove(self, relation):
        self._remove_raw(relation)
        self._changes.append(('remove', relation))

    def clear(self):
        for relation in self._relations:
            self.remove(relation)

    def get(self, name):
        for relation in self._relations:
            if relation.name == name:
                return relation
