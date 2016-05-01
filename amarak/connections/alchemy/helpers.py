# encoding: utf8
from sqlalchemy.sql import select, update, delete

def update_helper(ikey, table, session, obj, mapping):
    raise ValueError
    if hasattr(obj, '_alchemy_pk') and obj._alchemy_pk is not None:
        query = update(table)\
            .where(table.c.id==obj._alchemy_pk)\
            .values(**mapping)
        result = session.execute(query)

        if result.rowcount == 0:
            raise RuntimeError("Can't update object")
            # obj._alchemy_pk = None
            # return update_helper(session, obj, mapping)
    else:
        # TODO search for an object
        # query = select([table]).where(table.c.uri==obj.uri)
        # result = session.execute(query).fetchone()
        # if result:
        #     obj._alchemy_pk = result[0]
        #     return update_helper(session, obj, mapping)
        # else:

        # print "INSERT", obj, session.execute(select([table])).fetchall()
        aquery = table.insert().values(**mapping)
        result = session.execute(aquery)
        obj._alchemy_pk = result.inserted_primary_key[0]

def fetch_helper(session, fields, params, offset, limit):
    raise ValueError
    query = select(fields)

    if offset is not None:
        query = query.offset(offset)

    if limit is not None:
        query = query.limit(limit)

    records = session.execute(query).fetchall()

    records = session.execute(query).fetchall()
    for props in records:
        print props

    return concepts_l
