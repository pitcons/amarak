# encoding: utf8
from store import Store
from store.backends.sqlalchemy_store import *

def importer_rutez_to_skos():
    store = Store()
    scheme = store.scheme_get('rutez')
    print scheme.id
    for term in session.query(Term).all():
        print term
