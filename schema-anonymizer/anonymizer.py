import argparse
import logging
import json

from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, default_lbp_factory
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqltypes import cql_types_from_string, cqltype_to_python

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('anonymizer')

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


def export_cql_schema(keyspaces_metadata, options):
    # anonymize keyspace and its children
    for ks in keyspaces_metadata:
        anonymize_keyspace(ks)

    # set replication factor
    set_replication_factor(schema, options['rf'])
    # build CQL statements string
    generated_statements = "\n\n".join(ks.export_as_string() for ks in keyspaces_metadata)
    # transform CREATE statements to include `IF NOT EXISTS`
    generated_statements = transform_if_not_exists(generated_statements)

    print(generated_statements)


def export_gemini_schema(keyspaces_metadata, options):
    for ks in keyspaces_metadata:
        anonymize_keyspace(ks)

    # set replication factor
    set_replication_factor(schema, options['rf'])

    keyspace = keyspaces_metadata[0]
    replication = json.loads(
        ks.replication_strategy.export_for_schema().replace("'", "\""))
    data = {
        "keyspace": {
            "name": keyspace.name,
            "replication": replication,
            "oracle_replication": replication
        },
        "tables": []
    }

    for t in keyspace.tables.values():
        table_data = {
            "name": t.name,
            "partition_keys": [],
            "clustering_keys": [],
            "columns": [],
            "indexes": []
        }

        for pk in t.partition_key:
            table_data["partition_keys"].append({
                "name": pk.name,
                "type": pk.cql_type
            })

        for ck in t.clustering_key:
            table_data["clustering_keys"].append({
                "name": ck.name,
                "type": ck.cql_type
            })

        columns = get_standard_columns_from_table_metadata(t)
        for c in columns:
            table_data["columns"].append({
                "name": c.name,
                "type": cql_type_to_gemini(cqltype_to_python(c.cql_type))
            })

        for index in t.indexes.values():
            table_data["indexes"].append({
                "name": index.name,
                "column": index.index_options["target"]
            })

        data["tables"].append(table_data)

    print(json.dumps(data, indent=4))


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


def cql_type_to_gemini(cql_type, is_frozen=False):
    """
    Convert a cql type representation to the gemini json one.

    Limitations:
      * no support for udt
      * limited nested complex types support
    """
    if isinstance(cql_type, str):
        return cql_type
    elif len(cql_type) == 1:
        return cql_type[0]
    else:
        is_frozen_type = is_frozen
        gemini_type = {}
        token = cql_type.pop(0)

        if isinstance(token, (list, tuple)):
            return cql_type_to_gemini(token, is_frozen_type)
        elif token == 'frozen':
            return cql_type_to_gemini(cql_type.pop(0), True)
        elif token == 'map':
            subtypes = cql_type.pop(0)
            gemini_type['key_type'] = cql_type_to_gemini(subtypes[0], is_frozen_type)
            gemini_type['value_type'] = cql_type_to_gemini(subtypes[1], is_frozen_type)
        elif token == 'list':
            gemini_type['kind'] = 'list'
            gemini_type['type'] = cql_type_to_gemini(cql_type.pop(0)[0], is_frozen_type)
        elif token == 'set':
            gemini_type['kind'] = 'set'
            gemini_type['type'] = cql_type_to_gemini(cql_type.pop(0)[0], is_frozen_type)
        elif token == 'tuple':
            gemini_type['types'] = cql_type.pop(0)

        gemini_type['frozen'] = is_frozen_type
        return gemini_type


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


def set_replication_factor(db_schema, factor):
    if factor:
        for ks in db_schema.keyspaces.values():
            strategy = ks.replication_strategy
            strategy.replication_factor_info = factor


def transform_if_not_exists(cql_string):
    return cql_string.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS") \
        .replace("CREATE KEYSPACE", "CREATE KEYSPACE IF NOT EXISTS") \
        .replace("CREATE TYPE", "CREATE TYPE IF NOT EXISTS") \
        .replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")


parser = argparse.ArgumentParser(description='Utility script that connects to a Cassandra cluster,'
                                             'extracts its schema as CQL statements and anonymizes the entity names.')
parser.add_argument('--hosts', metavar='127.0.0.1', default='127.0.0.1',
                    help='Comma-separated list of contact points. Default: 127.0.0.1')
parser.add_argument('--port', metavar='9042', type=int, default=9042, help='Database RCP port. Default: 9042')
# not implemented yet
#parser.add_argument('--output', metavar='/file/path', help='Output file. If not specified, it will write to stdout')
parser.add_argument('--username', metavar='user', help='Database username')
parser.add_argument('--password', metavar='pass', help='Database password')
parser.add_argument('--keyspaces', metavar='k1,k2',
                    help='Comma-separated list of keyspaces to include. If not specified, all keypaces will '
                         'be included, except system keypaces')
parser.add_argument('--replication-factor', metavar='3', type=int,
                    help='Replication factor to override original setting. Optional.')
parser.add_argument('--format', metavar='cql', default='cql', choices=['cql', 'gemini'],
                    help='Output format for the schema. cql or gemini (json). Default is cql.')

# extract command-line args
args = parser.parse_args()
hosts = args.hosts.split(',')
port = args.port
selected_keyspaces = args.keyspaces.split(',') if args.keyspaces is not None else None
output_format = args.format
username = args.username
password = args.password

options = dict()
options['rf'] = args.replication_factor

# instantiate auth provider if credentials have been provided
auth_provider = None
if username is not None and password is not None:
    auth_provider = PlainTextAuthProvider(username=username, password=password)

ep = ExecutionProfile(load_balancing_policy=default_lbp_factory())
cluster = Cluster(hosts, port=port, auth_provider=auth_provider, execution_profiles={EXEC_PROFILE_DEFAULT: ep})
log.info("Connecting to the cluster to get metadata...")
session = cluster.connect()
schema = cluster.metadata
cluster.shutdown()

keyspaces_metadata = []
if selected_keyspaces is not None:
    try:
        for k in selected_keyspaces:
            keyspaces_metadata.append(schema.keyspaces[k])
    except KeyError:
        log.error("Keyspace '%s' not found in schema.", k)
else:
    # filter out system keyspaces
    keyspaces_metadata = [k for k in schema.keyspaces.values() if k.name not in system_keyspaces]

if len(keyspaces_metadata) == 0:
    log.info("No keyspace selected.")
    exit(1)

log.info("Exporting schema for the following keyspaces: %s",
         ','.join([k.name for k in keyspaces_metadata]))

if output_format == 'gemini':
    # multiple keyspaces is not supported with gemini
    if len(keyspaces_metadata) > 1:
        log.error("Gemini schema doesn't support multiple keyspaces.")
        exit(1)
    export_gemini_schema(keyspaces_metadata, options)
else:
    export_cql_schema(keyspaces_metadata, options)
