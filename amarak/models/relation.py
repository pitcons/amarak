# encoding: utf8
from amarak.utils import smart_decode, smart_encode


class Relation(object):

    def __init__(self, scheme, name):
        self.scheme = scheme
        self.name = smart_decode(name)

    def __repr__(self):
        return "Relation('{0}', '{1}')".format(
            smart_encode(self.scheme.id),
            smart_encode(self.name)
        )

    def __eq__(self, other):
        return (
            isinstance(other, Relation) and
            (self.scheme == other.scheme and self.name == other.name)
        )

    def to_python(self):
        return {
            'scheme': self.scheme.id,
            'name': self.name
        }
