from __future__ import absolute_import
from amarak.connections.base import BaseLinks
from amarak.connections.alchemy import tables as tbl
from amarak.models.link import Link
from .helpers import update_helper, fetch_helper


class Links(BaseLinks):

    def __init__(self, conn):
        self.conn = conn
        self.session = conn.session

    def update(self, obj):
        self.update_helper(
            'links',
            tbl.concept_link, obj,
            {'concept1_id': obj.concept1._alchemy_pk,
             'concept2_id': obj.concept2._alchemy_pk,
             'concept_relation_id': obj.relation._alchemy_pk,
             'scheme_id': obj.scheme._alchemy_pk, }
        )

    def _fetch(self, params, offset, limit):
        records = self._fetch_records(
            [tbl.concept_link.c.id,
             tbl.concept_link.c.concept1_id,
             tbl.concept_link.c.concept2_id,
             tbl.concept_link.c.concept_relation_id,
             tbl.concept_link.c.scheme_id, ],
            params, offset, limit
        )

        concept_pks = set()
        scheme_pks = set()
        relation_pks = set()
        result = []
        new_records = []
        for record in records:
            pk, concept1_id, concept2_id, relation_id, scheme_id = record
            link = self.conn.identity_map.get('links', pk)
            if link:
                result.append(result)
            else:
                new_records.append(record)
                concept_pks.add(concept1_id)
                concept_pks.add(concept2_id)
                relation_pks.add(relation_id)
                scheme_pks.add(scheme_id)

        schemes = self.conn.schemes._fetch(
            {'pks': scheme_pks}, None, None)
        concepts = self.conn.concepts._fetch(
            {'pks': concept_pks}, None, None)
        relations = self.conn.relations._fetch(
            {'pks': concept_pks}, None, None)

        for record in new_records:
            pk, concept1_id, concept2_id, relation_id, scheme_id = record

            link = Link(
                self.conn.identity_map.get('concepts', concept1_id),
                self.conn.identity_map.get('concepts', concept2_id),
                self.conn.identity_map.get('relations', relation_id),
                self.conn.identity_map.get('schemes', scheme_id),
            )
            self.conn.identity_map.put('links', pk, link)
            retsult.append(link)

        return result
