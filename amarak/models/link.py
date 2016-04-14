# encoding: utf8


class Link(object):

    def __init__(self, concept1, concept2, relation, scheme):
        self.concept1 = concept1
        self.concept2 = concept2
        self.relation = relation
        self.scheme = scheme
