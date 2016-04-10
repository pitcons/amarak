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
        if hasattr(concept, '_alchemy_pk') and concept._alchemy_pk is not None:
            query = update(tbl.concept)\
                .where(tbl.concept.c.id==concept._alchemy_pk)\
                .values(name=concept.name)
            result = self.session.execute(query)
            if result.rowcount == 0:
                concept._alchemy_pk = None
                return self.update(concept)

        else:
            query = select([tbl.concept])\
                .where(tbl.concept.c.name==concept.name)
            result = self.session.execute(query).fetchone()
            if result:
                concept._alchemy_pk = result[0]
            else:
                aquery = tbl.concept.insert().values(
                    name=concept.name,
                    scheme_id=concept.scheme._alchemy_pk
                )
                result = self.session.execute(aquery)
                concept._alchemy_pk = result.inserted_primary_key[0]

        for action, label in concept.labels._changes:
            if action == 'new':
                iquery = tbl.concept_label.insert().values(
                    concept_id=concept._alchemy_pk,
                    lang=label.lang,
                    type=label.type,
                    label=label.literal
                )
                result = self.session.execute(iquery)
            elif action == 'remove_by_id':
                query = delete(tbl.concept_label)\
                    .where(tbl.concept_label.c.id==label)
                self.session.execute(query)
            else:
                raise NotImplementedError(action)
        concept.labels._changes = []


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
                    ])

        if 'scheme' in params:
            scheme = params['scheme']
            query = query.where(tbl.concept.c.scheme_id==scheme._alchemy_pk)
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
        for pk, name, scheme_id in records:
            concept = Concept(name=name, scheme=scheme)
            concept._alchemy_pk = pk
            concepts_d[pk] = concept
            concepts_l.append(concept)

        query = select([
            tbl.concept_label.c.id,
                        tbl.concept_label.c.concept_id,
                        tbl.concept_label.c.type,
                        tbl.concept_label.c.lang,
                        tbl.concept_label.c.label,
                    ])\
            .select_from(
                join(tbl.concept, tbl.concept_label,
                     tbl.concept.c.id==tbl.concept_label.c.concept_id)
            )\
            .where(tbl.concept.c.scheme_id==scheme._alchemy_pk)\
            .order_by(tbl.concept_label.c.lang,
                      tbl.concept_label.c.type,
                      tbl.concept_label.c.label,)

        if 'name' in params:
            query = query.where(tbl.concept.c.name==params['name'])

        records = self.session.execute(query).fetchall()
        for pk, concept_id, label_type, lang, title in records:
            concepts_d[concept_id].labels._add_raw(lang, label_type, title, pk)

        return concepts_l

    def delete(self, concept):
        if hasattr(concept, '_alchemy_pk') and concept._alchemy_pk is not None:
            query = delete(tbl.concept)\
                .where(tbl.concept.c.id==concept._alchemy_pk)
        else:
            raise NotImplementedError

        self.session.execute(query)
