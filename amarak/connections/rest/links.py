# encoding: utf8
from amarak.connections.base import BaseLinks


class Links(BaseLinks):

    def __init__(self, conn):
        self.conn = conn

    def update(self, obj):
        raise NotImplementedError
        # url = 'schemes/{}/relations/{}'.format(obj.scheme.id, obj.orig_name)
        # self.conn._put(url, data={'name': obj.name})
