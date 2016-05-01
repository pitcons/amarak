# encoding: utf8
from amarak.connections.base import BaseRelations


class Relations(BaseRelations):

    def __init__(self, conn):
        self.conn = conn

    def update(self, obj):
        url = 'schemes/{}/relations/{}'.format(obj.scheme.id, obj.orig_name)
        self.conn._put(url, data={'name': obj.name})
