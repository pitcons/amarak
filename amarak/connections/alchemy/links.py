from __future__ import absolute_import
from amarak.connections.base import BaseLinks
from amarak.connections.alchemy import tables as tbl
from .helpers import update_helper, fetch_helper


class Links(BaseLinks):

    def __init__(self, conn):
        self.conn = conn
        self.session = conn.session

    def update(self, obj):
        update_helper(
            tbl.concept_link, self.session, obj,
            {'concept1_id': obj.concept1._alchemy_pk,
             'concept2_id': obj.concept2._alchemy_pk,
             'concept_relation_id': obj.relation._alchemy_pk,
             'scheme_id': obj.scheme._alchemy_pk, }
        )

    def _fetch(self, params, offset, limit):
        fetch_helper(
            self.session,
            [tbl.concept_link.c.id,
             tbl.concept_link.c.concept1_id,
             tbl.concept_link.c.concept2_id,
             tbl.concept_link.c.concept_relation_id,
             tbl.concept_link.c.scheme_id, ],
            params, offset, limit)
