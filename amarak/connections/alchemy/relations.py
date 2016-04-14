# encoding: utf8
import sqlalchemy
from amarak.connections.base import (ResultProxy,
                                     BaseRelations)
from amarak.connections.alchemy import tables as tbl
from .helpers import update_helper


class Relations(BaseRelations):

    def __init__(self, conn):
        self.conn = conn
        self.session = conn.session

    def update(self, obj):
        update_helper(tbl.concept_relation, self.session, obj,
            {'scheme_id': obj.scheme._alchemy_pk,
             'name': obj.name}
        )
