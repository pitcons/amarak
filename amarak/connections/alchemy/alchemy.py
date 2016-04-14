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
from .relations import Relations


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
        self.relations = Relations(self)
