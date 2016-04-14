# encoding: utf8
import json
import requests
from urllib import quote, quote_plus, urlencode
from os.path import join


from amarak.models.concept_scheme import ConceptScheme
from amarak.models.concept import Concept
from amarak.models.relation import Relation
from amarak.models.exception import DoesNotExist, MultipleReturned
from amarak.connections.base import (BaseSchemes,
                                     BaseConcepts,
                                     BaseConnection,
                                     BaseRelations)
from .relations import Relations

def orig_name(item):
    try:
        return item._orig_name
    except AttributeError:
        return item.name


class Schemes(BaseSchemes):

    def __init__(self, conn):
        self.conn = conn

    def get(self, id=None, name=None):
        if id:
            params = {'id': id}
        elif name:
            params = {'name': name}
        else:
            raise ValueError('The parameter name or id is expected')
        schemes = self._fetch(params, None, None)

        if len(schemes) > 1:
            raise MultipleReturned
        elif not schemes:
            raise DoesNotExist
        else:
            return schemes[0]

    def _fetch(self, params, offset, limit):
        req_data = {}
        if offset is not None:
            req_data['offset'] = offset

        if limit is not None:
            req_data['limit'] = limit

        if 'name' in params:
            req_data['name'] = params['name']

        if 'id' in params:
            req_data['id'] = params['id']

        response = self.conn._get('schemes/', req_data)
        result = []
        for scheme_d in response['schemes']:
            scheme = ConceptScheme(
                name=scheme_d['name'],
                namespace=(scheme_d['ns_prefix'], scheme_d['ns_url']),
            )
            for parent_id in scheme_d['parents']:
                # TODO optimize
                scheme.parents._add_raw(self.get(parent_id))

            for relation in scheme_d['relations']:
                # TODO Incorret
                scheme.relations._add_raw(Relation(scheme, relation['name']))

            scheme._rest_id = scheme.id
            result.append(scheme)

        return result


    def update(self, scheme):
        data = {
            key: getattr(scheme, key)
            for key in ('name', 'ns_prefix', 'ns_url')
        }

        # TODO update namespaces support
        data['parents'] = [parent.name for parent in scheme.parents.all()]

        # TODO update namespaces support
        data['relations'] = [
            relation.to_python() for relation in scheme.relations.all()
        ]

        self.conn._put('schemes/' + orig_name(scheme), data)
        scheme._orig_name = scheme.name


class Concepts(BaseConcepts):

    def __init__(self, conn):
        self.conn = conn

    def _fetch(self, params, offset, limit):
        scheme = params['scheme']

        result = self.conn._get('schemes/' + quote(scheme.name) + '/concepts/')
        concepts = []
        for concept_d in result['concepts']:
            concept = Concept.from_python(scheme, concept_d)
            concepts.append(concept)

        return concepts

    def update(self, concept):
        if not concept or not concept.name:
            # TODO maybe exeption?
            return

        self.conn._put(
            'schemes/' + quote(concept.scheme.name.encode('utf-8')) +
            '/concepts/' + quote(orig_name(concept).encode('utf-8')),
            {
                'name': concept.name,
                'labels': concept.labels.to_python()
            },
            as_json=True
        )
        concept._orig_name = concept.name


class RestConnection(BaseConnection):

    def __init__(self, url):
        self.url = url
        self.schemes = Schemes(self)
        self.concepts = Concepts(self)
        self.relations = Relations(self)

    def _get(self, url, data=None):
        url = join(self.url, url)
        response = requests.get(url, data)
        response.raise_for_status()

        return json.loads(response.content)

    def _put(self, url, data=None, as_json=False):
        url = join(self.url, url)
        if json:
            response = requests.put(url, json=data)
        else:
            response = requests.put(url, data)
        response.raise_for_status()

        return json.loads(response.content)
