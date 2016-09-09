from __future__ import absolute_import
import sqlalchemy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, update, delete, join

from amarak.models.concept_scheme import ConceptScheme
from amarak.models.concept import Concept
from amarak.models.exception import DoesNotExist, MultipleReturned
from amarak.connections.base import (BaseSchemes,
                                     BaseConcepts,
                                     BaseConnection)
from amarak.connections.alchemy import tables as tbl


class Concepts(BaseConcepts):

    def __init__(self, conn):
        self.conn = conn
        self.session = conn.session

    def update(self, concept):
        self.update_helper(
            'concepts', tbl.concept, concept,
            {'name': concept.name,
             'scheme_id': concept.scheme._alchemy_pk}
        )
        # labels
        self.update_changes(
            tbl.concept_label,
            concept.labels._changes,
            insert_f=lambda obj: {
                'concept_id': concept._alchemy_pk,
                'lang': obj.lang,
                'type': obj.type,
                'label': obj.literal
            },
            delete_f=None
        )
        concept.labels._changes = []

        # notes
        self.update_changes(
            tbl.concept_note,
            concept.notes._changes,
            insert_f=lambda obj: {
                'concept_id': concept._alchemy_pk,
                'lang': obj.lang,
                'type': obj.type,
                'text': obj.literal
            },
            delete_f=None
        )
        concept.notes._changes = []


    def get(self, name, scheme):
        concepts = self._fetch({'scheme': scheme, 'name': name}, None, None)
        if len(concepts) > 1:
            raise MultipleReturned
        elif not concepts:
            raise DoesNotExist
        else:
            return concepts[0]

    def _fetch(self, params, offset, limit):
        query = select([tbl.concept.c.id,
                        tbl.concept.c.name,
                        tbl.concept.c.scheme_id,
                    ])\
            .select_from(tbl.concept)\
            .order_by(tbl.concept.c.name)

        if 'scheme' in params:
            scheme = params['scheme']
            query = query.where(tbl.concept.c.scheme_id==scheme._alchemy_pk)
        elif 'pks' in params:
            if not params['pks']:
                return []
            query = query.where(tbl.scheme.c.id.in_(params['pks']))
        else:
            raise NotImplementedError

        if 'name' in params:
            query = query.where(tbl.concept.c.name==params['name'])

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        records = self.session.execute(query).fetchall()
        concepts_d = {}
        concepts_l = []
        pks = []
        for pk, name, scheme_id in records:
            pks.append(pk)
            scheme = self.conn.identity_map.get('schemes', scheme_id)
            if not scheme:
                raise RuntimeError
            concept = Concept(name=name, scheme=scheme)
            concept._alchemy_pk = pk
            concepts_d[pk] = concept
            concepts_l.append(concept)

        # Labels
        query = select([tbl.concept_label.c.id,
                        tbl.concept_label.c.concept_id,
                        tbl.concept_label.c.type,
                        tbl.concept_label.c.lang,
                        tbl.concept_label.c.label, ])\
            .select_from(
                join(tbl.concept, tbl.concept_label,
                     tbl.concept.c.id==tbl.concept_label.c.concept_id)
            )\
            .where(tbl.concept.c.id.in_(pks))\
            .order_by(tbl.concept_label.c.lang,
                      tbl.concept_label.c.type,
                      tbl.concept_label.c.label,)

        if 'name' in params:
            query = query.where(tbl.concept.c.name==params['name'])

        records = self.session.execute(query).fetchall()
        for pk, concept_id, label_type, lang, title in records:
            concepts_d[concept_id].labels._add_raw(lang, label_type, title, pk)

        # Notes
        query = select([tbl.concept_note.c.id,
                        tbl.concept_note.c.concept_id,
                        tbl.concept_note.c.type,
                        tbl.concept_note.c.lang,
                        tbl.concept_note.c.text, ])\
            .select_from(
                join(tbl.concept, tbl.concept_note,
                     tbl.concept.c.id==tbl.concept_note.c.concept_id)
            )\
            .where(tbl.concept.c.id.in_(pks))\
            .order_by(tbl.concept_note.c.lang,
                      tbl.concept_note.c.type,
                      tbl.concept_note.c.text,)

        if 'name' in params:
            query = query.where(tbl.concept.c.name==params['name'])

        records = self.session.execute(query).fetchall()
        for pk, concept_id, note_type, lang, title in records:
            concepts_d[concept_id].notes._add_raw(lang, note_type, title, pk)

        return concepts_l

    def delete(self, concept):
        if hasattr(concept, '_alchemy_pk') and concept._alchemy_pk is not None:
            query = delete(tbl.concept)\
                .where(tbl.concept.c.id==concept._alchemy_pk)
        else:
            raise NotImplementedError

        self.session.execute(query)
