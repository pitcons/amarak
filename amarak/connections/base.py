# encoding: utf8
import collections
from amarak.models.concept_scheme import ConceptScheme
from amarak.models.concept import Concept
from amarak.models.relation import Relation
from amarak.models.exception import DoesNotExist


class ResultProxy(object):

    def __init__(self, manager, params=None, offset=None, limit=None):
        self._manager = manager
        self._params = params
        self._offset = offset
        self._limit = limit

    def all(self):
        self._params = None
        self._offset = None
        self._limit = None
        return self

    def filter(self, *args, **kwargs):
        self._params.update(kwargs)
        return self

    def limit(self, value):
        self._limit = value
        return self

    def offset(self, value):
        self._offset = value
        return self

    def __getitem__(self, value):
        if isinstance(value, (int, long)):
            for item in self.offset(value).limit(1):
                return item

        if value.step is not None:
            raise ValueError('Slice step is not supported')

        if value.start is not None:
            if not isinstance(value.start, (int, long)) or value.start < 0:
                raise ValueError('Slice should be an non-negaive integer')

            self.offset(value.start)

        if value.stop is not None:
            if not isinstance(value.stop, (int, long)) or value.stop < 0:
                raise ValueError('Slice should be an non-negaive integer')

            if value.start is not None:
                if value.start > value.stop:
                    raise ValueError('Slice start should be less than stop')

                self.limit(value.stop - value.start)
            else:
                self.limit(value.stop)

        return self

    def __iter__(self):
        items = self._manager._fetch(self._params, self._offset, self._limit)
        for item in items:
            yield item


class CommonManager(object):

    def all(self):
        return ResultProxy(self, {}, None, None)

    def filter(self, **kwargs):
        return ResultProxy(self, kwargs, None, None)


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


class BaseConnection(object):

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
