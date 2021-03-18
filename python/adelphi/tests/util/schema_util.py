from cassandra.metadata import Metadata,\
	KeyspaceMetadata,\
	TableMetadata,\
	ColumnMetadata,\
	IndexMetadata,\
	SimpleStrategy, \
	UserType

# types compatible with C* 2.1+
data_types = ["ascii", "bigint", "blob", "boolean",
			"decimal", "double", "float", "inet", "int", "list<int>",
			"map<int,int>", "set<int>", "tuple<int, tuple<text, double>>",
			"text", "timestamp", "timeuuid",
			"uuid",  "varchar", "varint"]

def udt(keyspace, name, field_names, field_types):
	return UserType(keyspace.name, name, field_names, field_types)

def column(table_metadata, column_name, cql_type, is_static=False, is_reversed=False):
	return ColumnMetadata(table_metadata, column_name, cql_type)

def index(keyspace, table_name, index_name, kind, index_options):
	return IndexMetadata(keyspace.name, table_name, index_name, kind, index_options)

def get_table(keyspace, name, sasi=True):

	def data_type_column_name(idx):
		return "my_column_{}".format(idx)

	table = TableMetadata(keyspace.name, name)
	# build columns for each data type
	columns_dict = {}
	for i in range(len(data_types)):
		col = column(table, data_type_column_name(i), data_types[i])
		columns_dict[col.name] = col

	# create some udts
	address_udt = udt(keyspace, "address", ["street", "number"], ["text", "int"])
	user_udt = udt(keyspace, "user", ["name", "address"], ["tuple<text,text>", "frozen<address>"])
	collections_udt = udt(keyspace, "collections", ["field1", "field2", "field3", "field4"], ["frozen<user>",\
		"frozen<map<frozen<user>, frozen<user>>>",\
		"frozen<list<frozen<address>>>",\
		"frozen<tuple<frozen<user>, frozen<address>>>"])
	# add udts to keyspace
	keyspace.user_types = {address_udt.name: address_udt,\
		user_udt.name: user_udt,\
		collections_udt.name: collections_udt}
	# build column with udt types
	columns_dict["user"] = column(table, user_udt.name, "frozen<%s>" % user_udt.name)
	columns_dict["collections"] = column(table, collections_udt.name, "frozen<%s>" % collections_udt.name)

	# set some pk's and ck's
	def data_type_column(idx):
		return columns_dict[data_type_column_name(idx)]

	table.columns = columns_dict
	table.partition_key = [data_type_column(0), data_type_column(1)]
	table.clustering_key = [data_type_column(2), data_type_column(3)]

	# indexes
	indexes = {}
	# add a regular index
	regular_index = index(keyspace, name, "regular_index_" + name, None, {"target": "my_column_0"})
	indexes[regular_index.name] = regular_index
	# add a CUSTOM index (this must be removed by the anonymizer)
	if sasi:
		custom_index = index(keyspace, name, "custom_index_" + name, "CUSTOM", {"target": "my_column_5", "class_name": "org.apache.cassandra.index.sasi.SASIIndex"})
		indexes[custom_index.name] = custom_index
	table.indexes = indexes

	# table options compatible with C* 2.1+
	table.options = {
		# set a comment, which must be removed by the anonymizer
		"comment": "Lorem ipsum",
		"compaction_strategy_class": "org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy",
		"max_compaction_threshold": "32",
		"min_compaction_threshold": "4",
		"compression_parameters": '{"sstable_compression": ""}'
	}

	return table

def get_keyspace(name, durable_writes, strategy_class, strategy_options, sasi=True):
	keyspace = KeyspaceMetadata(name, durable_writes, strategy_class, strategy_options)
	# build some tables
	tables = {}
	for t in range(3):
		table = get_table(keyspace, "my_table_%s" % t, sasi=sasi)
		tables[table.name] = table

	keyspace.tables = tables
	return keyspace

def get_schema(sasi=True):
	# build a couple of keyspaces
	keyspaces = []
	for k in range(2):
		keyspace = get_keyspace("my_ks_%s" % k, True, "SimpleStrategy", {"replication_factor": 1}, sasi=sasi)
		keyspaces.append(keyspace)

	schema = Metadata()
	schema.keyspaces = keyspaces
	return schema

if __name__ == "__main__":
	"""
	Use this to print the test schema.
	The output can be used in the integration tests too.
	"""
        # As discussed elsewhere SASI support is disabled until https://github.com/datastax/adelphi/issues/105
        # is completed
	print("\n\n".join(ks.export_as_string() for ks in get_schema(sasi=False).keyspaces))
