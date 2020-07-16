from cassandra.cluster import Cluster
from cassandra import metadata

# holds a reference to the original `protect_name` implementation
protect_name = metadata.protect_name

# maps the original schema names to the replacement names
name_map = {}

# list of system keyspaces to filter out
system_keyspaces = ["system",
                    "system_schema",
                    "system_traces",
                    "system_auth",
                    "system_distributed",
                    "system_virtual_schema",
                    "system_views"]


def anonymize_name(name):
    anonymized_name = name_map.setdefault(name, "name_" + str(len(name_map)))
    return protect_name(anonymized_name)

# override `protect_name` by the anonymizing version
metadata.protect_name = anonymize_name

# TODO: accept connection config params in the command line
cluster = Cluster()
session = cluster.connect()

print("\n\n".join(ks.export_as_string() for ks in cluster.metadata.keyspaces.values() if ks.name not in system_keyspaces))
