# encoding: utf8
from amarak.utils import smart_encode, smart_decode
from rdflib.namespace import SKOS

class NoteTypeError(Exception):
    pass


class Note(object):

    def __init__(self, lang, type, literal, id=None):
        self.id = id
        self.lang = smart_decode(lang)
        self.type = smart_decode(type)
        self.literal = smart_decode(literal)

    def as_skos(self):
        return SKOS.definition
