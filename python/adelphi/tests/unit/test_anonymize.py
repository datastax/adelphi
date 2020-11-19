import pytest
from adelphi import anonymize
from adelphi.anonymize import COLUMN_PREFIX, get_name
from schema_util import get_schema

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

class TestCqlAnonymize(unittest.TestCase):

	def test_anonymize_index(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		index = table.indexes["regular_index_my_table_0"]
		anonymize.anonymize_index(index)
		self.assertEqual(index.name, "idx_0")
		self.assertEqual(index.index_options["target"], "col_0")

	def test_anonymize_column(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		column = table.columns["my_column_0"]
		anonymize.anonymize_column(column)

		self.assertEqual(column.name, "col_0")
		self.assertEqual(column.cql_type, "ascii")

	def test_anonymize_table(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		anonymize.anonymize_table(table)
		self.assertEqual(table.keyspace_name, "ks_0")
		self.assertEqual(table.name, "tbl_0")
		self.assertEqual(table.partition_key[0].name, "col_0")
		self.assertEqual(table.partition_key[1].name, "col_1")
		self.assertEqual(table.clustering_key[0].name, "col_2")
		self.assertEqual(table.clustering_key[1].name, "col_3")

	def test_anonymize_keyspace(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		anonymize.anonymize_keyspace(keyspace)
		self.assertEqual(keyspace.name, "ks_0")
		self.assertTrue(keyspace.durable_writes)
		self.assertEqual(keyspace.replication_strategy.replication_factor_info.all_replicas, 1)

		tables = list(keyspace.tables.values())
		self.assertEqual(tables[0].name, "tbl_0")
		self.assertEqual(tables[1].name, "tbl_1")
		self.assertEqual(tables[2].name, "tbl_2")

	def test_custom_indexes_are_removed(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		tables = list(keyspace.tables.values())
		table = tables[0]
		
		# ensure we have some custom indexes in the schema before anonymizing
		custom_indexes = [index for index in table.indexes.values() if index.kind == "CUSTOM"]
		self.assertTrue(len(custom_indexes) > 0)

		anonymize.anonymize_keyspace(keyspace)
		
		# custom indexes should have been removed
		custom_indexes = [index for index in table.indexes.values() if index.kind == "CUSTOM"]
		self.assertTrue(len(custom_indexes) == 0)

	def test_anonymous_name_is_consistent(self):
		name1 = get_name("test_column", COLUMN_PREFIX)
		name2 = get_name("test_column", COLUMN_PREFIX)
		name3 = get_name("another_column", COLUMN_PREFIX)
		self.assertEqual(name1, name2)
		self.assertNotEqual(name1, name3)
