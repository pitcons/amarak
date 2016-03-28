# encoding: utf8

__all__ = ['DoesNotExist', 'MultipleReturned']


class DoesNotExist(Exception):
    pass


class MultipleReturned(Exception):
    pass
