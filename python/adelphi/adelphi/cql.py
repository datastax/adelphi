# Logic necessary to generate a string representation of a standard CQL schema

from adelphi.anonymize import anonymize_keyspace
from adelphi.store import set_replication_factor

def export_cql_schema(keyspaces_metadata, schema, options):
    if options['anonymize']:
        # anonymize keyspace and its children
        for ks in keyspaces_metadata:
            anonymize_keyspace(ks)

    # set replication factor
    set_replication_factor(schema, options['rf'])
    # build CQL statements string
    generated_statements = "\n\n".join(ks.export_as_string() for ks in keyspaces_metadata)
    # transform CREATE statements to include `IF NOT EXISTS`

    # TODO: shift this around to a regex so that we can do the whole thing in a single pass
    return generated_statements.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS") \
        .replace("CREATE KEYSPACE", "CREATE KEYSPACE IF NOT EXISTS") \
        .replace("CREATE TYPE", "CREATE TYPE IF NOT EXISTS") \
        .replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")
