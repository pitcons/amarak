# encoding: utf8
from .label import Label


class LabelsManager(object):

    def __init__(self):
        self._labels = []
        self._changes = []

    def _add_raw(self, lang, label_type, literal, id=None):
        label = Label(lang, label_type, literal, id=id)
        self._labels.append(label)
        return label

    def add(self, lang, label_type, literal, id=None):
        label = self._add_raw(lang, label_type, literal, id)
        self._changes.append(('new', label))

    def _remove_raw(self, label):
        self._labels.append(label)

    def remove(self, label):
        self._remove_raw(label)
        self._changes.append(('remove', label))

    def remove_by_id(self, label_id):
        self._changes.append(('remove_by_id', label_id))

    def all(self):
        return self._labels

    def clear(self):
        for label in self._labels:
            self.remove(label)

    def to_python(self):
        return [
            {'id': label.id,
             'lang': label.lang,
             'type': label.type,
             'literal': label.literal}
            for label in self.all()
        ]
