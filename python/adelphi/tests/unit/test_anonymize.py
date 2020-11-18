import pytest
from cassandra.metadata import Metadata,\
	KeyspaceMetadata,\
	TableMetadata,\
	ColumnMetadata,\
	IndexMetadata,\
	SimpleStrategy
from adelphi import anonymize
from adelphi.anonymize import COLUMN_PREFIX

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

data_types = ["ascii", "bigint", "bigint", "blob", "boolean", "date",
			"decimal", "double", "float", "inet", "int", "map", "set",
			"smallint", "text", "time", "timestamp", "timeuuid", "tinyint",
			"uuid",  "varchar", "varint"]

class TestCqlAnonymize(unittest.TestCase):

	def column(self, table_metadata, column_name, cql_type, is_static=False, is_reversed=False):
		return ColumnMetadata(table_metadata, column_name, cql_type)

	def index(self, keyspace, table_name, index_name, kind, index_options):
		return IndexMetadata(keyspace.name, table_name, index_name, kind, index_options)

	def table(self, keyspace, name):
		table = TableMetadata(keyspace.name, name)
		# build columns for each data type
		columns_dict = {}
		for i in range(len(data_types)):
			col = self.column(table, "my_column_%s" % i, data_types[i])
			columns_dict[col.name] = col

		columns = list(columns_dict.values())

		# set some pk's and ck's
		partition_keys = [columns[0], columns[1]]
		clustering_keys = [columns[2], columns[3]]

		table.columns = columns_dict
		table.partition_key = partition_keys
		table.clustering_key = clustering_keys

		indexes = {}
		# add a regular index
		regular_index = self.index(keyspace, name, "regular_index_" + name, None, {"target": "my_column_0"})
		indexes[regular_index.name] = regular_index
		# add a CUSTOM index (this must be removed by the anonymizer)
		custom_index = self.index(keyspace, name, "custom_index_" + name, "CUSTOM", {"target": "my_column_1", "class_name": "foo.MyClass"})
		indexes[custom_index.name] = custom_index

		table.indexes = indexes
		return table

	def keyspace(self, name, durable_writes, strategy_class, strategy_options):
		keyspace = KeyspaceMetadata(name, durable_writes, strategy_class, strategy_options)
		# build some tables
		tables = {}
		for t in range(3):
			table = self.table(keyspace, "my_table_%s" % t)
			tables[table.name] = table

		keyspace.tables = tables
		return keyspace

	def schema(self):
		# build a couple of keyspaces
		keyspaces = []
		for k in range(2):
			keyspace = self.keyspace("my_ks_%s" % k, True, "SimpleStrategy", {"replication_factor": 3})
			keyspaces.append(keyspace)

		schema = Metadata()
		schema.keyspaces = keyspaces
		return schema

	def test_anonymize_index(self):
		schema = self.schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		index = table.indexes["regular_index_my_table_0"]
		anonymize.anonymize_index(index)
		self.assertEqual(index.name, "idx_0")
		self.assertEqual(index.index_options["target"], "col_0")

	def test_anonymize_column(self):
		schema = self.schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		column = table.columns["my_column_0"]
		anonymize.anonymize_column(column)

		self.assertEqual(column.name, "col_0")
		self.assertEqual(column.cql_type, "ascii")

	def test_anonymize_table(self):
		schema = self.schema()
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
		schema = self.schema()
		keyspace = schema.keyspaces[0]
		anonymize.anonymize_keyspace(keyspace)
		self.assertEqual(keyspace.name, "ks_0")
		self.assertTrue(keyspace.durable_writes)
		self.assertEqual(keyspace.replication_strategy.replication_factor_info.all_replicas, 3)

		tables = list(keyspace.tables.values())
		self.assertEqual(tables[0].name, "tbl_0")
		self.assertEqual(tables[1].name, "tbl_1")
		self.assertEqual(tables[2].name, "tbl_2")

	def test_custom_indexes_are_removed(self):
		schema = self.schema()
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



