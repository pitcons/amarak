# encoding: utf8
import sqlalchemy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, update, delete

from amarak.models.concept_scheme import ConceptScheme
from amarak.models.exception import DoesNotExist, MultipleReturned
from amarak.connections.base import (ResultProxy,
                                     BaseSchemes,
                                     BaseConcepts,
                                     BaseConnection)
from amarak.connections.alchemy import tables as tbl


def mk_concept_scheme(pk, name, namespace, namespaces):
    scheme = ConceptScheme(
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

    def _fill_hierarhy(self, schemes):
        if not schemes:
            return

        query = select([tbl.scheme_hierarchy]).where(
            tbl.scheme_hierarchy.c.scheme_id.in_([
                scheme._alchemy_pk for scheme in schemes
            ])
        )
        schemes_d = {
            scheme._alchemy_pk: scheme
            for scheme in schemes
        }

        result = self.session.execute(query).fetchall()
        for pk, weight, scheme_id, parent_id in result:
            schemes_d[scheme_id].parents._parents.append(
                schemes_d[parent_id]
            )

    def get(self, name=None):
        # TODO optimize
        schemes = self.all()
        for scheme in schemes:
            if name and scheme.name == name:
                return scheme

        raise DoesNotExist()

    def _fetch(self, params, offset, limit):
        query = select([tbl.scheme.c.id,
                        tbl.scheme.c.name,
                        tbl.scheme.c.ns_prefix,
                        tbl.scheme.c.ns_url,
                        tbl.scheme.c.namespaces])

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        records = self.session.execute(query).fetchall()
        schemes = []
        for (pk, name, ns_prefix, ns_url, namespaces) in records:
            schemes.append(mk_concept_scheme(pk, name, (ns_prefix, ns_url), namespaces))

        query = select([tbl.scheme])
        records = self.session.execute(query).fetchall()

        self._fill_hierarhy(schemes)
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
        if hasattr(scheme, '_alchemy_pk') and scheme._alchemy_pk is not None:
            query = update(tbl.scheme)\
                .where(tbl.scheme.c.id==scheme._alchemy_pk)\
                .values(name=scheme.name,
                        ns_prefix=scheme.ns_prefix,
                        ns_url=scheme.ns_url,
                        namespaces=json.dumps(scheme.namespaces))
            result = self.session.execute(query)
            if result.rowcount == 0:
                scheme._alchemy_pk = None
                return self.update(scheme)
        else:
            query = select([tbl.scheme]).where(tbl.scheme.c.name==scheme.name)
            result = self.session.execute(query).fetchone()
            if result:
                scheme._alchemy_pk = result[0]
                return self.update(scheme)
            else:
                aquery = tbl.scheme.insert().values(
                    name=scheme.name,
                    ns_prefix=scheme.ns_prefix,
                    ns_url=scheme.ns_url
                )
                result = self.session.execute(aquery)
                scheme._alchemy_pk = result.inserted_primary_key[0]

        for action, parent in scheme.parents._changes:
            if action == 'new':
                if not hasattr(parent, '_alchemy_pk') or not parent._alchemy_pk:
                    self.update(parent)
                iquery = tbl.scheme_hierarchy.insert().values(
                    scheme_id=scheme._alchemy_pk,
                    parent_id=parent._alchemy_pk,
                )
                self.session.execute(iquery)
            elif action == 'remove':
                if not hasattr(parent, '_alchemy_pk') or not parent._alchemy_pk:
                    self.update(parent)
                dquery = tbl.scheme_hierarchy.insert().delete(
                    scheme_id=scheme._alchemy_pk,
                    parent_id=parent._alchemy_pk,
                )
                self.session.execute(dquery)
            else:
                raise NotImplementedError(action)
