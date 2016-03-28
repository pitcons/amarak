# encoding: utf8
import time
from sqlalchemy import Integer, Text, String, Column, create_engine, Table
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ReprNameMixin(object):

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class ReprUriMixin(object):

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.uri


language = Table(
    'language', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('lang', String(64), primary_key=True),
    Column('name', String(255), nullable=False),
)


class Language(Base, ReprNameMixin):
    __table__ = language


scheme = Table(
    'scheme', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), nullable=False),
    Column('ns_prefix', String(512), nullable=False),
    Column('ns_url', String(512), nullable=False),
    Column('namespaces', Text(), nullable=False, server_default=''),
)


class Scheme(Base, ReprUriMixin):
    __table__ = scheme
    labels = relationship("SchemeLabel")


scheme_label = Table(
    'scheme_label', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('scheme_id',
           Integer,
           ForeignKey("scheme.id", ondelete='cascade'),
           nullable=False),
    Column('lang', String(64), nullable=False),
    Column('label', String(512), nullable=False),
)


class SchemeLabel(Base):
    __table__ = scheme_label


scheme_hierarchy = Table(
    'scheme_hierarchy', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('weight', Integer, default=0),
    Column('scheme_id',
           Integer,
           ForeignKey("scheme.id", ondelete='cascade'),
           nullable=False),
    Column('parent_id',
           Integer,
           ForeignKey("scheme.id", ondelete='cascade'),
           nullable=False),
    UniqueConstraint('scheme_id', 'parent_id')
)


class SchemeHierarchy(Base):
    __table__ = scheme_hierarchy


concept = Table(
    'concept', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(512), nullable=False),
    Column('scheme_id',
           Integer,
           ForeignKey("scheme.id", ondelete='cascade'),
           nullable=False),
)


class Concept(Base, ReprUriMixin):
    __table__ = concept
    labels = relationship("ConceptLabel")
    links = relationship("ConceptLink",
                         foreign_keys='ConceptLink.concept1_id')
    def skos_name(self):
        return self.uri.replace(' ', '_').replace('"', '')


concept_label = Table(
    'concept_label', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('concept_id',
           Integer,
           ForeignKey("concept.id", ondelete='cascade'),
           nullable=False),
    Column('type', String(64), nullable=False),
    Column('lang', String(64), nullable=False),
    Column('label', String(512), nullable=False, index=True),
)


class ConceptLabel(Base):
    __table__ = concept_label


# class ConceptInScheme(Base):
#     __table__ = Table(
#         'concept_in_scheme', Base.metadata,
#         Column('id', Integer, primary_key=True),
#         Column('concept_id',
#                Integer,
#                ForeignKey("concept.id", ondelete='cascade'),
#                nullable=False,
#                index=True),
#         Column('scheme_id',
#                Integer,
#                ForeignKey("scheme.id", ondelete='cascade'),
#                nullable=False,
#                index=True),
#     )


concept_relation = Table(
    'concept_relation', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('scheme_id',
           Integer,
           ForeignKey("scheme.id", ondelete='cascade'),
           nullable=False),
    Column('name', String(64)),
    UniqueConstraint('scheme_id', 'name'),
)


class ConceptRelation(Base):
    __table__ = concept_relation


concept_link = Table(
    'concept_link', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('concept1_id',
           Integer,
           ForeignKey("concept.id", ondelete='cascade'),
           nullable=False),
    Column('concept2_id',
           Integer,
           ForeignKey("concept.id", ondelete='cascade'),
           nullable=False),
    Column('concept_relation_id',
           Integer,
           ForeignKey("concept_relation.id", ondelete='cascade'),
           nullable=False),
    Column('scheme_id',
           Integer,
           ForeignKey("scheme.id", ondelete='cascade'),
           nullable=False),
    UniqueConstraint('concept_relation_id',
                     'concept1_id',
                     'concept2_id')
)


class ConceptLink(Base):
    __table__ = concept_link
    relation = relationship("ConceptRelation")
    concept1 = relationship("Concept",
                             foreign_keys="ConceptLink.concept1_id")
    concept2 = relationship("Concept",
                             foreign_keys="ConceptLink.concept2_id")
