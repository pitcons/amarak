# encoding: utf8
import unittest
import os
import sqlalchemy
from sqlalchemy_utils import (database_exists,
                              create_database,
                              drop_database)
from amarak.models import *
from amarak.connections.alchemy import AlchemyConnection
from amarak.connections.alchemy.tables import Base


URL = 'postgresql://amarak_test:123123@localhost:5432/amarak_test'
class TestDB(unittest.TestCase):

    def setUp(self):
        # url = os.getenv("DB_TEST_URL")
        # if not url:
        #     self.skipTest("No database URL set")

        self.engine = sqlalchemy.create_engine(URL, isolation_level="AUTOCOMMIT")
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        self.connection = self.engine.connect()
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.conn = AlchemyConnection(self.engine.url)

    def tearDown(self):
        drop_database(self.engine.url)


class SchemesTest(TestDB):

    def test_create_scheme(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.schemes.update(scheme)
        schemes = list(self.conn.schemes.all())
        self.assertEquals(len(schemes), 1)
        self.assertEquals(schemes[0].name, scheme.name)
        self.assertEquals(schemes[0].namespaces, scheme.namespaces)

    def test_update_scheme_total(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.schemes.update(scheme)
        scheme.name = 'example2'
        scheme.ns_prefix = 'example2'
        scheme.ns_url = 'http://example2.com'
        self.conn.schemes.update(scheme)
        schemes = list(self.conn.schemes.all())
        self.assertEquals(len(schemes), 1)
        self.assertEquals(schemes[0].name, scheme.name)
        self.assertEquals(schemes[0].ns_prefix, scheme.ns_prefix)
        self.assertEquals(schemes[0].ns_url, scheme.ns_url)
        self.assertEquals(schemes[0].namespaces, scheme.namespaces)

    def test_get(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.schemes.update(scheme)

        scheme = self.conn.schemes.get(id='example')
        self.assertEquals(scheme.name, 'example')
        self.assertEquals(scheme.ns_prefix, 'example')
        self.assertEquals(scheme.ns_url, 'http://example.com')

    def test_slice(self):
        scheme1 = ConceptScheme('example1', ('example1', 'http://example1.com'))
        scheme2 = ConceptScheme('example2', ('example2', 'http://example2.com'))
        scheme3 = ConceptScheme('example3', ('example3', 'http://example3.com'))
        scheme4 = ConceptScheme('example4', ('example4', 'http://example4.com'))

        self.conn.update([scheme1, scheme2, scheme3, scheme4])

        result1 = list(self.conn.schemes.all().limit(1))
        self.assertEquals(len(result1), 1)
        self.assertEquals(result1[0].name, scheme1.name)

        result2 = list(self.conn.schemes.all().limit(1).offset(1))
        self.assertEquals(len(result2), 1)
        self.assertEquals(result2[0].name, scheme2.name)

        result3 = list(self.conn.schemes.all().limit(2).offset(2))
        self.assertEquals(len(result3), 2)
        self.assertEquals(result3[0].name, scheme3.name)
        self.assertEquals(result3[1].name, scheme4.name)

        result4 = list(self.conn.schemes.all()[1:])
        self.assertEquals(len(result4), 3)
        self.assertEquals(result4[0].name, scheme2.name)
        self.assertEquals(result4[1].name, scheme3.name)
        self.assertEquals(result4[2].name, scheme4.name)

        result5 = list(self.conn.schemes.all()[:2])
        self.assertEquals(len(result5), 2)
        self.assertEquals(result5[0].name, scheme1.name)
        self.assertEquals(result5[1].name, scheme2.name)

        result6 = list(self.conn.schemes.all()[2:3])
        self.assertEquals(len(result6), 1)
        self.assertEquals(result6[0].name, scheme3.name)

        result7 = self.conn.schemes.all()[2]
        self.assertEquals(result7.name, scheme3.name)


    def test_slice_errors(self):
        with self.assertRaisesRegexp(
                ValueError, 'Slice step is not supported'):
            self.conn.schemes.all()[0:10:1]

        for start, stop in [(-1, 0), (0, -1)]:
            with self.assertRaisesRegexp(
                    ValueError,'Slice should be an non-negaive integer'):
                self.conn.schemes.all()[start:stop]

        with self.assertRaisesRegexp(
                ValueError, 'Slice start should be less than stop'):
            self.conn.schemes.all()[10:5]


    def test_hierarhy(self):
        scheme1 = ConceptScheme('example1', ('example1', 'http://example1.com'))
        scheme2 = ConceptScheme('example2', ('example2', 'http://example2.com'))
        scheme1.parents.add(scheme2)
        self.conn.schemes.update(scheme2)
        self.conn.schemes.update(scheme1)


        scheme = self.conn.schemes.get(id='example1')
        parents = scheme.parents.all()
        self.assertEquals(len(parents), 1)
        self.assertEquals(parents[0].id, 'example2')

    def test_relations(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        scheme.relations.add(Relation(scheme, 'test-relation'))
        self.conn.schemes.update(scheme)

        schemes = list(self.conn.schemes.all())
        self.assertEquals(len(schemes), 1)

        self.assertEquals(schemes[0].relations.all()[0].name, 'test-relation')
        self.assertEquals(schemes[0].relations.all()[0].scheme, scheme)


class ConceptsTest(TestDB):

    def test_concepts(self):
        scheme = ConceptScheme('example1', ('example1', 'http://example1.com'))
        self.conn.schemes.update(scheme)
        concept1 = Concept('Some concept', scheme=scheme)
        self.conn.concepts.update(concept1)

        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 1)
        self.assertEquals(concepts[0].name, 'Some concept')

        concept1.name = 'Changed'
        self.conn.concepts.update(concept1)

        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 1)
        self.assertEquals(concepts[0].name, 'Changed')


    def test_labels(self):
        scheme = ConceptScheme('example1', ('example1', 'http://example1.com'))
        self.conn.schemes.update(scheme)
        concept1 = Concept('Some concept', scheme=scheme)
        concept1.labels.add('en', 'prefLabel', 'Some label')
        concept1.labels.add('ru', 'prefLabel', 'Некоторое название')
        self.conn.concepts.update(concept1)

        concepts = self.conn.concepts.filter(scheme=scheme)
        self.assertEquals(
            concepts[0].labels.all(),
            [Label("en", "prefLabel", "Some label"),
             Label("ru", "prefLabel", "Некоторое название")]
        )
