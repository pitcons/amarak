# encoding: utf8
from amarak.connections.base import BaseRelations


class Relations(BaseRelations):

    def __init__(self, conn):
        self.conn = conn

    def update(self, obj):
        raise NotImplementedError
