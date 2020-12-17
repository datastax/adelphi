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


# Logic necessary to generate a string representation of a standard CQL schema

import hashlib
import logging
from base64 import urlsafe_b64encode
from datetime import datetime, tzinfo, timedelta

try:
    from itertools import ifilterfalse as filterfalse
except ImportError:
    from itertools import filterfalse

try:
    from datetime import timezone
    utc = timezone.utc
except ImportError:
    class UTC(tzinfo):
        def utcoffset(self, dt):
            return timedelta(0)
        def tzname(self, dt):
            return "UTC"
        def dst(self, dt):
            return timedelta(0)
    utc = UTC()


from adelphi.anonymize import anonymize_keyspace
from adelphi.store import build_keyspace_objects, set_replication_factor


log = logging.getLogger('adelphi')

class NoKeyspacesSelectedException(Exception):
    """Exception indicinating that no valid keyspaces were selected"""
    pass


class CqlExporter:

    def __init__(self, cluster, props):
        self.props = props

        self.keyspaces = self.__get_keyspaces(cluster, props)

        self.metadata = {k : props[k] for k in ["purpose", "maturity"] if k in props}
        self.metadata.update(self.__get_cluster_metadata(cluster))
        self.metadata["creation_timestamp"] = datetime.now(utc).isoformat()


    # unique_everseen from itertools recipes
    def __unique(self, iterable, key=None):
        "List unique elements, preserving order. Remember all elements ever seen."
        # unique_everseen('AAAABBBCCDAABBB') --> A B C D
        # unique_everseen('ABBCcAD', str.lower) --> A B C D
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in filterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element


    def __build_keyspace_id(self, ks):
        m = hashlib.sha256()
        m.update(ks.name.encode("utf-8"))
        # Leverage the urlsafe base64 encoding defined in RFC 4648, section 5 to provide an ID which can
        # safely be used for filenames as well
        return urlsafe_b64encode(m.digest()).decode('ascii')


    def __get_keyspaces(self, cluster, props):
        keyspace_names = props["keyspace-names"]
        metadata = cluster.metadata
        keyspaces = build_keyspace_objects(keyspace_names, metadata)

        if len(keyspaces) == 0:
            raise NoKeyspacesSelectedException

        log.info("Processing the following keyspaces: %s", ','.join((ks.name for ks in keyspaces)))

        # anonymize_keyspace mutates keyspace state so we must trap keyspace_id before we (possibly) call it
        base_map = { ks : self.__build_keyspace_id(ks) for ks in keyspaces}
        return base_map if not props['anonymize'] else {anonymize_keyspace(ks) : keyspace_id for (ks, keyspace_id) in base_map.items()}


    def __get_cluster_metadata(self, cluster):
        hosts = cluster.metadata.all_hosts()
        unique_dcs = self.__unique((host.datacenter for host in hosts))
        return {"host-count": len(hosts), "dc-count": sum(1 for i in unique_dcs)}


    def each_keyspace(self, ks_fn):
        for (ks, keyspace_id) in self.keyspaces.items():
            ks_fn(ks, keyspace_id)


    def export_metadata(self):
        return {k : self.metadata[k] for k in self.metadata.keys() if self.metadata[k]}


    def export_schema(self):

        set_replication_factor(self.keyspaces, self.props['rf'])

        # build CQL statements string
        cql_str = "\n\n".join(ks.export_as_string() for ks in self.keyspaces)

        # transform CREATE statements to include `IF NOT EXISTS`
        # TODO: shift this around to a regex so that we can do the whole thing in a single pass
        return cql_str.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS") \
                      .replace("CREATE KEYSPACE", "CREATE KEYSPACE IF NOT EXISTS") \
                      .replace("CREATE TYPE", "CREATE TYPE IF NOT EXISTS") \
                      .replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")
