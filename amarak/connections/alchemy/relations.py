# encoding: utf8
import sqlalchemy
from amarak.connections.base import (ResultProxy,
                                     BaseRelations)
from amarak.connections.alchemy import tables as tbl
from amarak.models.relation import Relation
from .helpers import update_helper


class Relations(BaseRelations):

    def __init__(self, conn):
        self.conn = conn
        self.session = conn.session

    def update(self, obj):
        self.update_helper(
            'relations', tbl.concept_relation, obj,
            {'scheme_id': obj.scheme._alchemy_pk,
             'name': obj.name}
        )

    def _fetch(self, params, offset, limit):
        records = self._fetch_records(
            [tbl.concept_relation.c.id,
             tbl.concept_relation.c.name,
             tbl.concept_relation.c.scheme_id, ],
            params, offset, limit
        )
        result = []
        for pk, name, scheme_id in records:
            relation = self.conn.identity_map.get('relations', pk)
            if relation:
                result.append(relation)
            else:
                scheme = self.conn.identity_map.get('schemes', scheme_id)
                if not scheme:
                    raise NotImplementedError
                relation = Relation(scheme, name)
                relation._alchemy_pk = pk
                self.conn.identity_map.put('relations', pk, relation)
                result.append(relation)

        return result
