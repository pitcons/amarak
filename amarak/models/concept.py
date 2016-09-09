# encoding: utf8
from .labels_manager import LabelsManager
from .manager import Manager
from .link import Link
from .note import Note
from .notes_manager import NotesManager
from amarak.utils import smart_encode, smart_decode


class LinkManager(Manager):

    def __init__(self):
        super(LinkManager, self).__init__(Link)


class Concept(object):
    name = None
    scheme = None
    labels = None

    def __init__(self, name, scheme):
        self.name = name
        self.scheme = scheme
        self.labels = LabelsManager()
        self.links = LinkManager()
        self.notes = NotesManager()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = smart_decode(value)

    def skos_name(self):
        return self.name.replace(' ', '_').replace('"', '')

    def __repr__(self):
        return 'Concept("%s")' % (smart_encode(self.name))

    @classmethod
    def from_python(cls, scheme, data):
        concept = cls(name=data['name'], scheme=scheme)

        for label_d in data['labels']:
            concept.labels._add_raw(
                label_d['lang'],
                label_d['type'],
                label_d['literal'],
                label_d.get('id'))

        return concept

    def to_python(self):
        return {
            'scheme': self.scheme.id,
            'name': self.name,
            'labels': self.labels.to_python()
        }
