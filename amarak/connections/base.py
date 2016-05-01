# encoding: utf8
import collections
from amarak.models.concept_scheme import ConceptScheme
from amarak.models.concept import Concept
from amarak.models.relation import Relation
from amarak.models.exception import DoesNotExist
from .common_manager import CommonManager, ResultProxy
from .identity_map import IdentityMap

class BaseSchemes(CommonManager):

    def get(self, id=None, name=None):
        raise NotImplementedError

    def update(self, scheme):
        raise NotImplementedError

    def get_or_create(self, id):
        try:
            return self.get(id=id)
        except DoesNotExist:
            # TODO default namespace from config
            return ConceptScheme(
                id=id,
                name=id,
                namespace=(id, 'http://example.com')
            )


class BaseConcepts(CommonManager):

    def update(self, concept):
        raise NotImplementedError

    def get_or_create(self, name, scheme):
        try:
            return self.get(name=name, scheme=scheme)
        except DoesNotExist:
            return Concept(name, scheme=scheme)


class BaseRelations(CommonManager):
    pass


class BaseLinks(CommonManager):
    pass


class BaseConnection(object):

    def __init__(self):
        self.identity_map = IdentityMap()

    def update(self, obj):
        if isinstance(obj, collections.Iterable):
            for item in obj:
                self.update(item)
        elif isinstance(obj, Concept):
            self.concepts.update(obj)
        elif isinstance(obj, ConceptScheme):
            self.schemes.update(obj)
        elif isinstance(obj, Relation):
            self.relations.update(obj)
        else:
            raise ValueError(
                "Expected Concept or ConceptScheme, but {} was passed"
                .format(type(obj))
            )
