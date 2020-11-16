# Functions to facilitate interactions with the underlying data store

import logging

from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, default_lbp_factory
from cassandra.auth import PlainTextAuthProvider

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('adelphi')

system_keyspaces = ["system",
                    "system_schema",
                    "system_traces",
                    "system_auth",
                    "system_distributed",
                    "system_virtual_schema",
                    "system_views"]

def build_auth_provider(username = None,password = None):
    # instantiate auth provider if credentials have been provided
    auth_provider = None
    if username is not None and password is not None:
        auth_provider = PlainTextAuthProvider(username=username, password=password)
    return auth_provider


def with_cluster(cluster_fn, hosts, port, username = None, password = None):
    ep = ExecutionProfile(load_balancing_policy=default_lbp_factory())
    cluster = Cluster(hosts, port=port, auth_provider=build_auth_provider(username,password), execution_profiles={EXEC_PROFILE_DEFAULT: ep})
    log.info("Connecting to the cluster to get metadata...")
    cluster.connect()
    cluster_fn(cluster)
    cluster.shutdown()


def filter_keyspaces_for_export(keyspaces, metadata):
    if keyspaces is not None:
        return [metadata.keyspaces[k] for k in keyspaces]
    else:
        # filter out system keyspaces
        return [k for k in metadata.keyspaces.values() if k.name not in system_keyspaces]


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


def set_replication_factor(metadata, selected_keyspaces, factor):
    if factor:
        for ks in selected_keyspaces:
            print("Replication: " + str(ks.replication_strategy) + " for keyspace " + ks.name)
            strategy = ks.replication_strategy
            strategy.replication_factor_info = factor
