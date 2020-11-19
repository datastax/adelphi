from cassandra.metadata import Metadata,\
	KeyspaceMetadata,\
	TableMetadata,\
	ColumnMetadata,\
	IndexMetadata,\
	SimpleStrategy

# types compatible with C* 2.1
data_types = ["ascii", "bigint", "blob", "boolean",
			"decimal", "double", "float", "inet", "int", "list<int>",
			"map<int,int>", "set<int>",
			"text", "timestamp", "timeuuid",
			"uuid",  "varchar", "varint"]

# types compatible with C* 2.1+
#data_types = ["date", "smallint", "time", "tinyint"]

def column(table_metadata, column_name, cql_type, is_static=False, is_reversed=False):
	return ColumnMetadata(table_metadata, column_name, cql_type)

def index(keyspace, table_name, index_name, kind, index_options):
	return IndexMetadata(keyspace.name, table_name, index_name, kind, index_options)

def get_table(keyspace, name):
	table = TableMetadata(keyspace.name, name)
	# build columns for each data type
	columns_dict = {}
	for i in range(len(data_types)):
		col = column(table, "my_column_%s" % i, data_types[i])
		columns_dict[col.name] = col

	columns = list(columns_dict.values())

	# set some pk's and ck's
	partition_keys = [columns[0], columns[1]]
	clustering_keys = [columns[2], columns[3]]

	table.columns = columns_dict
	table.partition_key = partition_keys
	table.clustering_key = clustering_keys

	# indexes
	indexes = {}
	# add a regular index
	regular_index = index(keyspace, name, "regular_index_" + name, None, {"target": "my_column_0"})
	indexes[regular_index.name] = regular_index
	# add a CUSTOM index (this must be removed by the anonymizer)
	custom_index = index(keyspace, name, "custom_index_" + name, "CUSTOM", {"target": "my_column_5", "class_name": "org.apache.cassandra.index.sasi.SASIIndex"})
	indexes[custom_index.name] = custom_index
	table.indexes = indexes

	# table options
	table.options = {
		"compaction_strategy_class": "org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy",
		"max_compaction_threshold": "32",
		"min_compaction_threshold": "4",
		"compression_parameters": '{"sstable_compression": ""}'
	}

	return table

def get_keyspace(name, durable_writes, strategy_class, strategy_options):
	keyspace = KeyspaceMetadata(name, durable_writes, strategy_class, strategy_options)
	# build some tables
	tables = {}
	for t in range(3):
		table = get_table(keyspace, "my_table_%s" % t)
		tables[table.name] = table

	keyspace.tables = tables
	return keyspace

def get_schema():
	# build a couple of keyspaces
	keyspaces = []
	for k in range(2):
		keyspace = get_keyspace("my_ks_%s" % k, True, "SimpleStrategy", {"replication_factor": 1})
		keyspaces.append(keyspace)

	schema = Metadata()
	schema.keyspaces = keyspaces
	return schema

if __name__ == "__main__":
	"""
	Use this to print the generated schema.
	The output can be used in the integration tests too.
	"""
	print("\n\n".join(ks.export_as_string() for ks in get_schema().keyspaces))