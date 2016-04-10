# encoding: utf8
from amarak.utils import smart_encode, smart_decode
from rdflib.namespace import SKOS

class LabelTypeError(Exception):
    pass


class Label(object):

    def __init__(self, lang, type, literal, id=None):
        self.id = id
        self.lang = smart_decode(lang)
        self.type = smart_decode(type)
        self.literal = smart_decode(literal)

    def as_skos(self):
        if self.type == 'prefLabel':
            return SKOS.prefLabel
        elif self.type == 'altLabel':
            return SKOS.altLabel
        elif self.type == 'hiddenLabel':
            return SKOS.hiddenLabel
        else:
            raise LabelTypeError

    def __repr__(self):
        return 'Label("{0}", "{1}", "{2}", id={3})'.format(
            smart_encode(self.lang),
            smart_encode(self.type),
            smart_encode(self.literal),
            smart_encode(self.id)
        )

    def __eq__(self, other):
        return (self.lang == other.lang and
                self.type == other.type and
                self.literal == other.literal)
