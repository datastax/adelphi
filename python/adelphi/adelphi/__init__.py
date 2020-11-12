from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, default_lbp_factory
from cassandra.auth import PlainTextAuthProvider

# list of system keyspaces to filter out
system_keyspaces = ["system",
                    "system_schema",
                    "system_traces",
                    "system_auth",
                    "system_distributed",
                    "system_virtual_schema",
                    "system_views"]


# default prefixes for the anonymized names
KEYSPACE_PREFIX = "ks"
TABLE_PREFIX = "tbl"
PARTITION_KEY_PREFIX = "pk"
CLUSTERING_KEY_PREFIX = "ck"
COLUMN_PREFIX = "col"
TYPE_PREFIX = "udt"
FIELD_PREFIX = "fld"
INDEX_PREFIX = "idx"

# maps the original schema names to the replacement names
name_map = {
    KEYSPACE_PREFIX: {},
    TABLE_PREFIX: {},
    PARTITION_KEY_PREFIX: {},
    CLUSTERING_KEY_PREFIX: {},
    COLUMN_PREFIX: {},
    TYPE_PREFIX: {},
    FIELD_PREFIX: {},
    INDEX_PREFIX: {}
}

def set_replication_factor(db_schema, factor):
    if factor:
        for ks in db_schema.keyspaces.values():
            strategy = ks.replication_strategy
            strategy.replication_factor_info = factor


def get_standard_columns_from_table_metadata(table_metadata):
    """
    Return the standard columns and ensure to exclude pk and ck ones.
    """
    partition_column_names = [c.name for c in table_metadata.partition_key]
    clustering_column_names = [c.name for c in table_metadata.clustering_key]
    standard_columns = []
    for c in list(table_metadata.columns.values()):
        if 'udt' in c.cql_type:
            log.warning("Ignoring column %s since udt are not supported." % c.name)
            del table_metadata.columns[c.name]
            continue
        if (c.name not in clustering_column_names
                and c.name not in partition_column_names):
            standard_columns.append(c)

    return standard_columns


def get_name(original_name, prefix):
    """
    Looks up the anonymized name for the provided original name in the cache.
    If not present, one is created, inserted into the cache and returned.
    """
    count = len(name_map[prefix])
    anonymized_named_prefixed = "%s_%s" % (prefix, count)
    return name_map[prefix].setdefault(original_name, anonymized_named_prefixed)


def anonymize_keyspace(keyspace):
    keyspace.name = get_name(keyspace.name, KEYSPACE_PREFIX)

    for table in keyspace.tables.values():
        anonymize_table(table)

    for table in keyspace.user_types.values():
        anonymize_udt(table)


def anonymize_udt(udt):
    udt.keyspace = get_name(udt.keyspace, KEYSPACE_PREFIX)
    udt.name = get_name(udt.name, TYPE_PREFIX)
    # field names
    udt.field_names = [get_name(field_name, FIELD_PREFIX) for field_name in udt.field_names]
    # field types
    udt.field_types = [get_name(field_type, TYPE_PREFIX)
                       if field_type in name_map[TYPE_PREFIX]
                       else field_type
                       for field_type in udt.field_types]


def anonymize_column(column, prefix):
    column.name = get_name(column.name, prefix)


def anonymize_index(index):
    index.name = get_name(index.name, INDEX_PREFIX)
    prefix = COLUMN_PREFIX if index.index_options['target'] in name_map[COLUMN_PREFIX] \
        else CLUSTERING_KEY_PREFIX
    index.index_options['target'] = name_map[prefix][index.index_options["target"]]
    index.keyspace_name = name_map[KEYSPACE_PREFIX][index.keyspace_name]
    index.table_name = name_map[TABLE_PREFIX][index.table_name]


def anonymize_table(table):
    table.keyspace_name = get_name(table.keyspace_name, KEYSPACE_PREFIX)
    table.name = get_name(table.name, TABLE_PREFIX)

    for partition_key in table.partition_key:
        anonymize_column(partition_key, PARTITION_KEY_PREFIX)

    for clustering_key in table.clustering_key:
        anonymize_column(clustering_key, CLUSTERING_KEY_PREFIX)

    # CK are also in the standard columns, but different objects
    # if we don't anonymize them there too, the generated cql is wrong
    for clustering_key in [t for t in table.columns.values() if t.name in name_map[CLUSTERING_KEY_PREFIX]]:
        clustering_key.name = name_map[CLUSTERING_KEY_PREFIX][clustering_key.name]

    for column in get_standard_columns_from_table_metadata(table):
        anonymize_column(column, COLUMN_PREFIX)

    for index in list(table.indexes.values()):
        if (index.index_options["target"] not in name_map[COLUMN_PREFIX].keys() and
                index.index_options["target"] not in name_map[CLUSTERING_KEY_PREFIX].keys()):
            del table.indexes[index.name]
            continue
        anonymize_index(index)
