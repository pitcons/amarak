# encoding: utf8
from __future__ import unicode_literals

from urllib import urlencode, quote
from rdflib import Namespace
from rdflib import Graph, BNode, Literal
from rdflib.namespace import RDF, SKOS

from amarak.connections.rest import RestConnection
from amarak.models.concept_scheme import ConceptScheme
from amarak.models.concept import Concept
from amarak.models import exception as exc


class ExportError(object):

    def __init__(self, message):
        pass


class ExportResult(object):

    def __init__(self, errors):
        self.errors = errors


class RdfExporter(object):

    def __init__(self, url):
        if isinstance(url, basestring):
            self.conn = RestConnection(url)
        else:
            self.conn = url

    def do_export(self, scheme_name, stream):
        graph = Graph()
        graph.bind('skos', 'http://www.w3.org/2004/02/skos/core#')

        errors = []
        scheme = self.conn.schemes.get(name=scheme_name)
        graph.bind(scheme.name, scheme.ns_url)
        ns = Namespace(scheme.ns_url)

        graph.add((ns[scheme.name], RDF.type, SKOS.ConceptScheme))
        for concept in self.conn.concepts.filter(scheme=scheme):
            graph.add((ns[concept.skos_name()], RDF.type, SKOS.Concept))
            graph.add((ns[scheme.name], SKOS.hasConcept, ns[concept.skos_name()]))
            # graph.add((ns[scheme.name], SKOS.hasTopConcept, ns[concept.skos_name()]))

            for label in concept.labels.all():
                graph.add((ns[concept.skos_name()],
                           label.as_skos(),
                           Literal(label.literal, lang=label.lang)))


        stream.write(graph.serialize(format='turtle'))

        return ExportResult(errors)
