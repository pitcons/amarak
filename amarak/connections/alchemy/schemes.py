# encoding: utf8
import sqlalchemy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, update, delete, and_

from amarak.models.concept_scheme import ConceptScheme
from amarak.models.relation import Relation
from amarak.models.exception import DoesNotExist, MultipleReturned
from amarak.connections.base import (ResultProxy,
                                     BaseSchemes,
                                     BaseConcepts,
                                     BaseConnection)
from amarak.connections.alchemy import tables as tbl
from .helpers import update_helper

def mk_concept_scheme(pk, id, name, namespace, namespaces):
    scheme = ConceptScheme(
        id=id,
        name=name,
        namespace=namespace,
        namespaces=json.loads(namespaces) if namespaces else None
    )
    scheme._alchemy_pk = pk
    return scheme


class Schemes(BaseSchemes):

    def __init__(self, conn):
        self.conn = conn
        self.session = conn.session

    def _prepare_fill(self, schemes, from_cache_pks):
        pks = [scheme._alchemy_pk
               for scheme in schemes
               if scheme._alchemy_pk not in from_cache_pks]
        schemes_d = {
            scheme._alchemy_pk: scheme
            for scheme in schemes
            if scheme._alchemy_pk not in from_cache_pks
        }

        return pks, schemes_d

    def _fill_hierarhy(self, schemes_d, pks):
        if not schemes_d:
            return

        query = select([tbl.scheme_hierarchy]).where(
            tbl.scheme_hierarchy.c.scheme_id.in_(pks)
        )

        result = self.session.execute(query).fetchall()
        for pk, weight, scheme_id, parent_id in result:
            schemes_d[scheme_id].parents._parents.append(
                schemes_d[parent_id]
            )

    def _fill_relations(self, schemes_d, pks):
        if not pks:
            return

        query = select(
            [tbl.concept_relation.c.id,
             tbl.concept_relation.c.scheme_id,
             tbl.concept_relation.c.name]
        ).where(
            tbl.concept_relation.c.scheme_id.in_(pks)
        )

        result = self.session.execute(query).fetchall()
        for pk, scheme_id, name in result:
            relation = Relation(schemes_d[scheme_id], name)
            relation._alchemy_pk = pk
            schemes_d[scheme_id].relations._add_raw(relation)


    def get(self, name=None, id=None):
        # TODO optimize
        schemes = self.all()
        for scheme in schemes:
            if name and scheme.name == name:
                return scheme

            if id and scheme.id == id:
                return scheme

        raise DoesNotExist()

    def _fetch(self, params, offset, limit):
        query = select([tbl.scheme.c.id,
                        tbl.scheme.c.scheme_id,
                        tbl.scheme.c.name,
                        tbl.scheme.c.ns_prefix,
                        tbl.scheme.c.ns_url,
                        tbl.scheme.c.namespaces])

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        if 'pks' in params:
            if not params['pks']:
                return []
            query = query.where(tbl.scheme.c.id.in_(params['pks']))

        records = self.session.execute(query).fetchall()
        schemes = []
        from_cache_pks = set()
        for (pk, scheme_id, name, ns_prefix, ns_url, namespaces) in records:
            scheme_obj = self.conn.identity_map.get('schemes', pk)
            if scheme_obj:
                from_cache_pks.add(pk)
                schemes.append(scheme_obj)
            else:
                scheme_obj = mk_concept_scheme(pk, scheme_id, name, (ns_prefix, ns_url), namespaces)
                self.conn.identity_map.put('schemes', pk, scheme_obj)
                schemes.append(scheme_obj)

        query = select([tbl.scheme])
        records = self.session.execute(query).fetchall()

        pks, schemes_d = self._prepare_fill(schemes, from_cache_pks)
        self._fill_hierarhy(schemes_d, pks)
        self._fill_relations(schemes_d, pks)
        return schemes

    def delete(self, scheme):
        if hasattr(scheme, '_alchemy_pk') and scheme._alchemy_pk is not None:
            query = delete(tbl.scheme)\
                .where(tbl.scheme.c.id==scheme._alchemy_pk)
        else:
            query = delete(tbl.scheme)\
                .where(tbl.scheme.c.name==scheme.name)

        self.session.execute(query)

    def update(self, scheme):
        self.update_helper(
            'schemes', tbl.scheme, scheme,
            {'name': scheme.name,
             'scheme_id': scheme.id,
             'ns_prefix': scheme.ns_prefix,
             'ns_url': scheme.ns_url,
             'namespaces': json.dumps(scheme.namespaces)}
        )
        self.update_changes(
            tbl.scheme_hierarchy,
            scheme.parents._changes,
            insert_f=lambda obj: {'scheme_id': scheme._alchemy_pk,
                                  'parent_id': obj._alchemy_pk},
        )
        scheme.parents._changes = []

        self.update_changes(
            tbl.concept_relation,
            scheme.relations._changes,
            insert_f=None,
            delete_f=lambda obj: and_(
                tbl.concept_relation.c.scheme_id==scheme._alchemy_pk,
                tbl.concept_relation.c.name==obj.name
            )
        )
        scheme.relations._changes = []
