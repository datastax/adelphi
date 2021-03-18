from adelphi import anonymize
from adelphi.anonymize import KEYSPACE_PREFIX,\
	COLUMN_PREFIX,\
	TABLE_PREFIX,\
	TYPE_PREFIX,\
	FIELD_PREFIX,\
	INDEX_PREFIX,\
	get_name
from tests.util.schema_util import get_schema

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

class TestCqlAnonymize(unittest.TestCase):

	def setUp(self):
		# clear state between tests
		anonymize.name_map = {
		    KEYSPACE_PREFIX: {},
		    TABLE_PREFIX: {},
		    COLUMN_PREFIX: {},
		    TYPE_PREFIX: {},
		    FIELD_PREFIX: {},
		    INDEX_PREFIX: {}
		}

	def assertPrefixes(self, name_list, prefix):
		for name in name_list:
			self.assertTrue(name.startswith(prefix))

	def test_anonymize_simple_udt(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		udt = keyspace.user_types["address"]
		anonymize.anonymize_udts([udt])
		self.assertTrue(udt.name.startswith("udt"))
		self.assertPrefixes(udt.field_names, "fld")
		self.assertEqual(udt.field_types, ["text", "int"])

	def test_anonymize_nested_udt(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		address = keyspace.user_types["address"]
		user = keyspace.user_types["user"]
		anonymize.anonymize_udts([address, user])
		self.assertTrue(user.name.startswith("udt"))
		self.assertPrefixes(user.field_names, "fld")
		self.assertEqual(user.field_types, ["tuple<text,text>", "frozen<udt_0>"])

	def test_anonymize_complex_udt(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		address = keyspace.user_types["address"]
		user = keyspace.user_types["user"]
		collections = keyspace.user_types["collections"]
		anonymize.anonymize_udts([address, user, collections])
		self.assertTrue(collections.name.startswith("udt"))
		self.assertPrefixes(collections.field_names, "fld")
		self.assertEqual(collections.field_types, ["frozen<udt_1>",\
			"frozen<map<frozen<udt_1>, frozen<udt_1>>>",\
			"frozen<list<frozen<udt_0>>>",\
			"frozen<tuple<frozen<udt_1>, frozen<udt_0>>>"])

	def test_anonymize_index(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		index = table.indexes["regular_index_my_table_0"]
		anonymize.anonymize_index(index)
		# check the index name has been anonymized
		self.assertTrue(index.name.startswith("idx"))
		# check the index'es target column has been anonymized
		self.assertTrue(index.index_options["target"].startswith("col"))

	def test_anonymize_column(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		column = table.columns["my_column_0"]
		anonymize.anonymize_column(column)

		self.assertTrue(column.name.startswith("col"))
		self.assertEqual(column.cql_type, "ascii")

	def test_anonymize_table(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		table = keyspace.tables["my_table_0"]
		origin_pk = table.partition_key
		origin_ck = table.clustering_key
		origin_col_cnt = len(table.columns)

		anonymize.anonymize_table(table)
		self.assertTrue(table.keyspace_name.startswith("ks"))
		self.assertTrue(table.name.startswith("tbl"))

		self.assertEqual(origin_col_cnt, len(table.columns))

		# check all columns at once
		self.assertPrefixes([column.name for column in table.columns.values()], "col")

		# Check standard columns match their pk and ck definitions.
		#
		# Note that table.columns imposes no guaranteed ordering (particularly on Python2) and
		# that we have no mapping between original and anonymized column names.  As such all
		# we can do here is compare the types of the partition and clustering keys for both
		# tables and validate that they match.
		self.assertEqual(origin_pk[0].cql_type, table.partition_key[0].cql_type)
		self.assertEqual(origin_pk[1].cql_type, table.partition_key[1].cql_type)
		self.assertEqual(origin_ck[0].cql_type, table.clustering_key[0].cql_type)
		self.assertEqual(origin_ck[1].cql_type, table.clustering_key[1].cql_type)

	def test_anonymize_keyspace(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		anonymize.anonymize_keyspace(keyspace)
		self.assertEqual(keyspace.name, "ks_0")
		self.assertTrue(keyspace.durable_writes)
		self.assertEqual(keyspace.replication_strategy.replication_factor_info.all_replicas, 1)

		tables = [table.name for table in keyspace.tables.values()]
		self.assertPrefixes(tables, "tbl")

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

	def test_table_comment_is_removed(self):
		schema = get_schema()
		keyspace = schema.keyspaces[0]
		tables = list(keyspace.tables.values())
		table = tables[0]

		self.assertTrue(table.options["comment"] == "Lorem ipsum")
		anonymize.anonymize_table(table)
		self.assertTrue(table.options["comment"] == "")

	def test_anonymous_name_is_consistent(self):
		name1 = get_name("test_column", COLUMN_PREFIX)
		name2 = get_name("test_column", COLUMN_PREFIX)
		name3 = get_name("another_column", COLUMN_PREFIX)
		self.assertEqual(name1, name2)
		self.assertNotEqual(name1, name3)

if __name__ == "__main__":
    unittest.main()
