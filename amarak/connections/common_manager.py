# encoding: utf8
# TODO REMOVE
from sqlalchemy.sql import select, update, delete

class ResultProxy(object):

    def __init__(self, manager, params=None, offset=None, limit=None):
        self._manager = manager
        self._params = params
        self._offset = offset
        self._limit = limit

    def all(self):
        self._params = None
        self._offset = None
        self._limit = None
        return self

    def filter(self, *args, **kwargs):
        self._params.update(kwargs)
        return self

    def limit(self, value):
        self._limit = value
        return self

    def offset(self, value):
        self._offset = value
        return self

    def __getitem__(self, value):
        if isinstance(value, (int, long)):
            for item in self.offset(value).limit(1):
                return item

        if value.step is not None:
            raise ValueError('Slice step is not supported')

        if value.start is not None:
            if not isinstance(value.start, (int, long)) or value.start < 0:
                raise ValueError('Slice should be an non-negaive integer')

            self.offset(value.start)

        if value.stop is not None:
            if not isinstance(value.stop, (int, long)) or value.stop < 0:
                raise ValueError('Slice should be an non-negaive integer')

            if value.start is not None:
                if value.start > value.stop:
                    raise ValueError('Slice start should be less than stop')

                self.limit(value.stop - value.start)
            else:
                self.limit(value.stop)

        return self

    def __iter__(self):
        items = self._manager._fetch(self._params, self._offset, self._limit)
        for item in items:
            yield item


class CommonManager(object):

    def all(self):
        return ResultProxy(self, {}, None, None)

    def filter(self, **kwargs):
        return ResultProxy(self, kwargs, None, None)

    def update_changes(self, table, changes,
                       insert_f=None, where_f=None, delete_f=None):

        for action, obj in changes:
            if action == 'new':
                if insert_f is not None:
                    iquery = table.insert().values(
                        **insert_f(obj)
                    )
                    self.session.execute(iquery)
                else:
                    self.conn.update(obj)
            elif action == 'remove_by_id':
                dquery = delete(table)\
                    .where(table.c.id==obj)
                self.session.execute(dquery)
            elif action == 'remove':
                if delete_f is not None:
                    dquery = delete(table).where(
                        delete_f(obj)
                    )
                    self.session.execute(dquery)
                elif not hasattr(obj, '_alchemy_pk') or not obj._alchemy_pk:
                    raise NotImplementedError
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError(action)


    def update_helper(self, ikey, table, obj, mapping):

        if hasattr(obj, '_alchemy_pk') and obj._alchemy_pk is not None:
            query = update(table)\
                .where(table.c.id==obj._alchemy_pk)\
                .values(**mapping)
            result = self.session.execute(query)

            if result.rowcount == 0:
                raise RuntimeError("Can't update object")
                # obj._alchemy_pk = None
                # return update_helper(self.session, obj, mapping)
        else:
            # TODO search for an object
            # query = select([table]).where(table.c.uri==obj.uri)
            # result = self.session.execute(query).fetchone()
            # if result:
            #     obj._alchemy_pk = result[0]
            #     return update_helper(self.session, obj, mapping)
            # else:

            # print "INSERT", obj, self.session.execute(select([table])).fetchall()
            aquery = table.insert().values(**mapping)
            result = self.session.execute(aquery)
            obj._alchemy_pk = result.inserted_primary_key[0]
            self.conn.identity_map.put(ikey, obj._alchemy_pk, obj)

    def _fetch_records(self, fields, params, offset, limit):
        query = select(fields)

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return self.session.execute(query).fetchall()
