# encoding: utf8
from __future__ import absolute_import
import sqlalchemy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, update, delete

from amarak.models.concept_scheme import ConceptScheme
from amarak.models.exception import DoesNotExist, MultipleReturned
from amarak.connections.base import (BaseSchemes,
                                     BaseConcepts,
                                     BaseConnection)
from amarak.connections.alchemy import tables as tbl
from .schemes import Schemes
from .concepts import Concepts

# def update_helper(session, obj, mapping):
#     if hasattr(obj, '_alchemy_pk') and obj._alchemy_pk is not None:
#         query = update(tbl.scheme)\
#             .where(tbl.scheme.c.id==obj._alchemy_pk)\
#             .values(prefix=obj.name,
#                     uri=obj.uri,
#                     namespaces=json.dumps(obj.namespaces))
#         result = session.execute(query)
#         if result.rowcount == 0:
#             obj._alchemy_pk = None
#             return update_helper(session, obj, mapping))
#     else:
#         query = select([tbl.scheme]).where(tbl.scheme.c.uri==obj.uri)
#         result = session.execute(query).fetchone()
#         if result:
#             obj._alchemy_pk = result[0]
#             return update_helper(session, obj, mapping)
#         else:
#             aquery = tbl.scheme.insert().values(prefix=obj.name,
#                                                 uri=obj.uri)
#         result = session.execute(aquery)
#         obj._alchemy_pk = result.inserted_primary_key[0]





class AlchemyConnection(BaseConnection):

    def __init__(self, url):
        self.engine = sqlalchemy.create_engine(
            url,
            isolation_level="AUTOCOMMIT"
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.schemes = Schemes(self)
        self.concepts = Concepts(self)
