# Logic necessary to generate a string representation of a Gemini schema

import json

from cassandra.cqltypes import cqltype_to_python

from adelphi.anonymize import anonymize_keyspace
from adelphi.store import get_standard_columns_from_table_metadata, set_replication_factor

def export_gemini_schema(keyspaces_metadata, options):
    if options['anonymize']:
        for ks in keyspaces_metadata:
            anonymize_keyspace(ks)

    # set replication factor
    set_replication_factor(keyspaces_metadata, options['rf'])

    keyspace = keyspaces_metadata[0]
    replication = json.loads(
        keyspace.replication_strategy.export_for_schema().replace("'", "\""))
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

    return data


def to_string(data):
    return json.dumps(data, indent=4)

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
