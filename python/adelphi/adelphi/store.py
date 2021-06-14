# Copyright DataStax, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Functions to facilitate interactions with the underlying data store

import logging
from itertools import tee

# Account for name change in itertools as of py3k
try:
    from itertools import ifilterfalse as filterfalse
except ImportError:
    from itertools import filterfalse

from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, default_lbp_factory
from cassandra.auth import PlainTextAuthProvider

from tenacity import retry

log = logging.getLogger('adelphi')

system_keyspaces = set(["system",
                    "system_schema",
                    "system_traces",
                    "system_auth",
                    "system_distributed",
                    "system_virtual_schema",
                    "system_views"])

def build_auth_provider(username = None,password = None):
    """Instantiate auth provider if credentials have been provided"""
    if username is None or password is None:
        return None
    return PlainTextAuthProvider(username=username, password=password)


@retry
def with_cluster(cluster_fn, hosts, port, username = None, password = None):
    ep = ExecutionProfile(load_balancing_policy=default_lbp_factory())
    cluster = Cluster(hosts, port=port, auth_provider=build_auth_provider(username,password), execution_profiles={EXEC_PROFILE_DEFAULT: ep})
    try:
        cluster.connect()
        return cluster_fn(cluster)
    finally:
        cluster.shutdown()


@retry
def with_local_cluster(cluster_fn):
    return with_cluster(cluster_fn, ["127.0.0.1"], port=9042)


def build_keyspace_objects(keyspaces, metadata):
    """Build a list of cassandra.metadata.KeyspaceMetadata objects from a list of strings and a c.m.Metadata instance.  System keyspaces will be excluded."""
    all_keyspace_objs = [metadata.keyspaces[ks] for ks in keyspaces] if keyspaces is not None else metadata.keyspaces.values()

    # Borrowed from itertools
    def partition(pred, iterable):
        t1, t2 = tee(iterable)
        return list(filterfalse(pred, t1)), list(filter(pred, t2))

    (failed,passed) = partition(lambda ks: ks.name not in system_keyspaces,all_keyspace_objs)
    if failed:
        log.info("Excluding system keyspaces " + ",".join((ks.name for ks in failed)))
    return passed


def get_standard_columns_from_table_metadata(table_metadata):
    """Return the standard columns and ensure to exclude pk and ck ones"""
    partition_column_names = [c.name for c in table_metadata.partition_key]
    clustering_column_names = [c.name for c in table_metadata.clustering_key]
    standard_columns = []
    for c in list(table_metadata.columns.values()):
        if (c.name not in clustering_column_names
                and c.name not in partition_column_names):
            standard_columns.append(c)

    return standard_columns


def set_replication_factor(selected_keyspaces, factor):
    if not factor:
        log.debug("No replication factor provided")
    else:
        for ks in selected_keyspaces:
            if ks.virtual:
                log.debug("Keyspace " + ks.name + " is a virtual keyspace")
                continue
            log.debug("Replication for keyspace " + ks.name+ ": " + str(ks.replication_strategy))
            strategy = ks.replication_strategy
            strategy.replication_factor_info = factor


def create_schema(session, schemaPath):
    """Read schema CQL document and apply CQL commands to cluster"""
    log.info("Creating schema on Cassandra cluster from file {}".format(schemaPath))
    with open(schemaPath) as schema:
        buff = ""
        for line in schema:
            realLine = line.strip()
            if len(realLine) == 0:
                log.debug("Skipping empty statement")
                continue
            if realLine.startswith("//") or realLine.startswith("--"):
                log.debug("Skipping commented statement")
                continue
            buff += (" " if len(buff) > 0 else "")
            buff += realLine
            if buff.endswith(';'):
                log.debug("Executing statement {}".format(buff))
                try:
                    session.execute(buff)
                except Exception as exc:
                    log.error("Exception executing statement: {}".format(buff), exc_info=exc)
                finally:
                    buff = ""
