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

import hashlib
import logging
from base64 import urlsafe_b64encode
from collections import namedtuple
from datetime import datetime, tzinfo, timedelta

try:
    from itertools import ifilterfalse as filterfalse
except ImportError:
    from itertools import filterfalse

from adelphi.anonymize import anonymize_keyspace
from adelphi.exceptions import KeyspaceSelectionException
from adelphi.store import build_keyspace_objects


log = logging.getLogger('adelphi')

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

KsTuple = namedtuple('KsTuple',['ks_id', 'ks_obj'])

class BaseExporter:
    
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


    def build_keyspace_id(self, ks):
        m = hashlib.sha256()
        m.update(ks.name.encode("utf-8"))
        # Leverage the urlsafe base64 encoding defined in RFC 4648, section 5 to provide an ID which can
        # safely be used for filenames as well
        return urlsafe_b64encode(m.digest()).decode('ascii')


    def get_keyspaces(self, cluster, props):
        keyspace_names = props["keyspace-names"]
        metadata = cluster.metadata
        keyspaces = build_keyspace_objects(keyspace_names, metadata)

        if len(keyspaces) == 0:
            raise KeyspaceSelectionException("Unable to select a keyspace from specified keyspace names")

        log.info("Processing the following keyspaces: %s", ','.join((ks.name for ks in keyspaces)))

        # anonymize_keyspace mutates keyspace state so we must trap keyspace_id before we (possibly) call it
        ids = {ks.name : self.build_keyspace_id(ks) for ks in keyspaces}

        # Create a tuple to represent this keyspace.  Note that we must perform anonymization as part of this
        # operation because we need the keyspace name before anonymization to access the correct ID from the
        # dict above.
        def make_tuple(ks):
            orig_name = ks.name
            if props['anonymize']:
                anonymize_keyspace(ks)
            return KsTuple(ids[orig_name], ks)
        return {t.ks_obj.name : t for t in [make_tuple(ks) for ks in keyspaces]}


    def get_cluster_metadata(self, cluster):
        hosts = cluster.metadata.all_hosts()
        unique_dcs = self.__unique((host.datacenter for host in hosts))
        unique_cass_vers = self.__unique((host.release_version for host in hosts))
        return {"host_count": len(hosts), "dc_count": sum(1 for _ in unique_dcs), "cassandra_versions": ",".join(unique_cass_vers)}


    def get_common_metadata(self, cluster, props):
        metadata = {k : props[k] for k in ["purpose", "maturity"] if k in props}
        metadata.update(self.get_cluster_metadata(cluster))
        metadata["creation_timestamp"] = datetime.now(utc).isoformat()
        return metadata


    # Remaining methods in this class represent default impls of methods for subclasses
    def export_all(self):
        return self.export_schema()


    # Note assumption of keyspace and keyspace_id as attrs
    def each_keyspace(self, ks_fn):
        ks_fn(self.keyspace, self.keyspace_id)


    # Functions below assume self.metadata as a dict
    def export_metadata_dict(self):
        return {k : self.metadata[k] for k in self.metadata.keys() if self.metadata[k]}


    def add_metadata(self, k, v):
        """Note that this function sets a metadata value for the entire exporter.  If you
        need something keyspace-specific you're probably better off just adding it to the
        exported metadata directory."""
        self.metadata[k] = v
