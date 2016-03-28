# encoding: utf8
from __future__ import unicode_literals
import hashlib
from itertools import chain

from pprint import pprint
from rdflib import Graph
from rdflib.term import URIRef, Literal

from amarak.connections.rest import RestConnection
from amarak.models.concept_scheme import ConceptScheme
from amarak.models.concept import Concept
from amarak.models import exception as exc


def hash_scheme_name(uri):
    return 'scheme-' + hashlib.md5(uri).hexdigest()[:8]

class ImportError(object):

    def __init__(self, message, tripplet):
        self.message = message
        self.tripplet = tripplet

    def serialize(self):
        return {'message': self.message, 'tripplet': self.tripplet}

def append_sharp(uri):
    uri = uri.strip()
    if not uri.endswith('#'):
        return uri + '#'

    return uri

class SkosImporter(object):
    CORE = 'http://www.w3.org/2004/02/skos/core#'
    TYPE_URI = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    SCHEME_URI = URIRef(CORE + 'ConceptScheme')
    CONCEPT_URI = URIRef(CORE + 'Concept')
    IN_SCHEME_URI = URIRef(CORE + 'inScheme')
    HAS_CONCEPT_URI = URIRef(CORE + 'hasConcept')
    LABELS = (
        CORE + 'prefLabel',
        CORE + 'altLabel',
        CORE + 'hiddenLabel',
    )

    def __init__(self, url_or_conn):
        if isinstance(url_or_conn, basestring):
            self.conn = RestConnection(url_or_conn)
        else:
            self.conn = url_or_conn
        self.errors = []

    def _to_python(self, iterator):
        for subj, pred, obj in iterator:
            yield subj.toPython(), pred.toPython(), obj.toPython()

    def _process_schemes(self, graph):
        # Создание всех схем
        schemes_d = {}
        qset = graph.triples((None, self.TYPE_URI, self.SCHEME_URI))
        for scheme_uri, pred, obj in self._to_python(qset):
            for ns_name, ns_url in graph.namespaces():
                if scheme_uri.startswith(ns_url):
                    break
                else:
                    ns_name, ns_url = None, None
            if not ns_url:
                raise ValueError('Namespace not found')

            ns_url = ns_url.toPython()
            scheme_name = scheme_uri[len(ns_url):]
            full_url = ns_url + ns_name
            # scheme_uri = append_sharp(scheme_uri)
            try:
                # пытаемся найти схему по URI
                scheme = self.conn.schemes.get(name=scheme_name)
                schemes_d[full_url] = scheme
            except exc.DoesNotExist:
                # если не нашли - создадим
                schemes_d[full_url] = ConceptScheme(
                    scheme_name, (ns_name, ns_url)
                )
                self.conn.schemes.update(schemes_d[full_url])

        return schemes_d

    def _process_concepts(self, graph, schemes_d):
        # создание всех концептов
        concepts_d = {}

        # сами концепты
        # TODO а нужны ли они тут? Только для отлова безсхемных?
        qset = graph.triples((None, self.TYPE_URI, self.CONCEPT_URI))
        for concept_uri, pred, obj in self._to_python(qset):
            concepts_d[concept_uri] = Concept(name=None, scheme=None)

        def process_concept(concept_uri, pred, scheme_uri):
            # scheme_uri = append_sharp(scheme_uri)
            concepts_d[concept_uri].scheme = schemes_d[scheme_uri]
            if concept_uri.startswith(scheme_uri):
                # имя концепта начинается со схемы
                concepts_d[concept_uri].name = concept_uri[len(scheme_uri):]
            else:
                # TODO hack
                # иначе у нас будут длинные имена
                concepts_d[concept_uri].name = concept_uri.split('/')[-1]

        #
        qset = graph.triples((None, self.IN_SCHEME_URI, None))
        for concept_uri, pred, scheme_uri in self._to_python(qset):
            process_concept(concept_uri, pred, scheme_uri)

        #
        qset = graph.triples((None, self.HAS_CONCEPT_URI, None))
        for scheme_uri, pred, concept_uri in self._to_python(qset):
            process_concept(concept_uri, pred, scheme_uri)

        return concepts_d

    def _process_other(self, graph, schemes_d, concepts_d):
        # После того, как создан каркас в виде схем и концептов,
        # мы можем обработать все остальные элементы

        for subj, pred, obj in graph:
            subj = subj.toPython()
            pred = pred.toPython()

            if pred in (self.IN_SCHEME_URI):
                # пропуск обработанных ранее
                pass
            elif pred in self.LABELS:
                label_type = pred.split('#')[-1]
                if subj in schemes_d:
                    schemes_d[subj].labels.add(
                        obj.language, label_type, obj.title()
                    )
                elif subj in concepts_d:
                    concepts_d[subj].labels.add(
                        obj.language, label_type, obj.title()
                    )
                else:
                    self.errors.append(ImportError('Not implemented', (subj, pred, obj)))
            else:
                # TODO enable
                pass
                # self.errors.append(ImportError('Not implemented', (subj, pred, obj)))

    def do_import(self, path, format):
        graph = Graph()
        graph.parse(path, format=format)

        self.errors = []
        schemes_d = self._process_schemes(graph)
        concepts_d = self._process_concepts(graph, schemes_d)
        self._process_other(graph, schemes_d, concepts_d)

        # Запишем концепты
        # TODO bulk_update
        for uri, concept in concepts_d.items():
            self.conn.concepts.update(concept)

        return self.errors


def import_skos(path):
    importer = SkosImporter('http://127.0.0.1:8000/')
    importer.do_import(path, "turtle")

if __name__ == '__main__':
    #import_skos('/home/petr/ownCloud/projects/ont/downloaded/unescothes_1000.ttl')
    import_skos('/home/petr/ownCloud/projects/ont/downloaded/Domain_Fields_Core.skos.turtle')
    #import_skos('/home/petr/ownCloud/projects/amarak/data/dg.rdf')
