from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import argparse

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
COLUMN_PREFIX = "col"
TYPE_PREFIX = "udt"
FIELD_PREFIX = "fld"

# maps the original schema names to the replacement names
name_map = {
    KEYSPACE_PREFIX: {},
    TABLE_PREFIX: {},
    COLUMN_PREFIX: {},
    TYPE_PREFIX: {},
    FIELD_PREFIX: {}
}


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
    # tables
    [anonymize_table(table) for table in keyspace.tables.values()]
    # types
    [anonymize_udt(table) for table in keyspace.user_types.values()]


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


def anonymize_column(column):
    column.name = get_name(column.name, COLUMN_PREFIX)


def anonymize_table(table):
    table.keyspace_name = get_name(table.keyspace_name, KEYSPACE_PREFIX)
    table.name = get_name(table.name, TABLE_PREFIX)
    # columns
    [anonymize_column(column) for column in table.columns.values()]
    # partition keys
    [anonymize_column(partition_key) for partition_key in table.partition_key]
    # clustering keys
    [anonymize_column(clustering_key) for clustering_key in table.clustering_key]


def set_replication_factor(db_schema, factor):
    if factor:
        for ks in db_schema.keyspaces.values():
            strategy = ks.replication_strategy
            strategy.replication_factor_info = factor


def transform_if_not_exists(cql_string):
    cql_string = cql_string.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
    cql_string = cql_string.replace("CREATE KEYSPACE", "CREATE KEYSPACE IF NOT EXISTS")
    cql_string = cql_string.replace("CREATE TYPE", "CREATE TYPE IF NOT EXISTS")
    return cql_string


parser = argparse.ArgumentParser(description='Utility script that connects to a Cassandra cluster, ' +
                                             'extracts its schema as CQL statements and anonymizes the entity names.')
parser.add_argument('--hosts', metavar='127.0.0.1', default='127.0.0.1', help='Comma-separated list of contact points. '
                                                                              'Default: 127.0.0.1')
parser.add_argument('--port', metavar='9042', type=int, default=9042, help='Database RCP port. Default: 9042')
parser.add_argument('--output', metavar='/file/path', help='Output file. If not specified, it will write to stdout')
parser.add_argument('--username', metavar='user', help='Database username')
parser.add_argument('--password', metavar='pass', help='Database password')
parser.add_argument('--keyspaces', metavar='k1,k2', help='Comma-separated list of keyspaces to include. '
                                                         'If not specified, all keypaces will be included, '
                                                         'except system keypaces')
parser.add_argument('--replication-factor', metavar='3', type=int, help='Replication factor to override original '
                                                                        'setting. Optional.')

# extract command-line args
args = parser.parse_args()
hosts = args.hosts.split(',')
port = args.port
selected_keyspaces = args.keyspaces.split(',') if args.keyspaces is not None else None
username = args.username
password = args.password
replication_factor = args.replication_factor

# instantiate auth provider if credentials have been provided
auth_provider = None
if username is not None and password is not None:
    auth_provider = PlainTextAuthProvider(username=username, password=password)

cluster = Cluster(contact_points=hosts, port=port, auth_provider=auth_provider)
session = cluster.connect()
schema = cluster.metadata
cluster.shutdown()

# filter out system keyspaces
for sys_ks_name in system_keyspaces:
    schema.keyspaces.pop(sys_ks_name, None)

# filter out non-selected keyspaces
if selected_keyspaces is not None:
    to_remove = [ks for ks in schema.keyspaces.values() if ks.name not in selected_keyspaces]
    for ks in to_remove:
        schema.keyspaces.pop(ks.name, None)

# anonymize keyspace and its children
[anonymize_keyspace(ks) for ks in schema.keyspaces.values()]
# set replication factor
set_replication_factor(schema, replication_factor)
# build CQL statements string
generated_statements = "\n\n".join(ks.export_as_string() for ks in schema.keyspaces.values())
# transform CREATE statements to include `IF NOT EXISTS`
generated_statements = transform_if_not_exists(generated_statements)

print(generated_statements)
