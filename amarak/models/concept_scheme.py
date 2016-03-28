# encoding: utf8
from amarak.utils import smart_decode, smart_encode
from .labels_manager import LabelsManager
from .parents_manager import ParentsManager


DEFAULT_NAMESPACES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
}



class ConceptScheme(object):
    uri = None

    def __init__(self, name, namespace, namespaces=None, parents=None):
        self.parents = ParentsManager(parents)
        self.name = name
        self.ns_prefix = namespace[0]
        self.ns_url = namespace[1]
        self.labels = LabelsManager()
        self.namespaces = namespaces or DEFAULT_NAMESPACES.copy()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = smart_decode(value)

    def __repr__(self):
        return 'ConceptScheme("%s", ("%s", "%s"))' % (
            smart_encode(self.name),
            smart_encode(self.ns_prefix),
            smart_encode(self.ns_url)
        )
