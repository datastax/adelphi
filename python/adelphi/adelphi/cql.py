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


import json

from adelphi.export import BaseExporter
from adelphi.store import set_replication_factor


class CqlExporter(BaseExporter):

    def __init__(self, cluster, props):
        self.props = props
        self.keyspaces = self.get_keyspaces(cluster, props)
        self.metadata = self.get_common_metadata(cluster, props)


    def export_all(self):
        metadata_str = json.dumps(self.export_metadata_dict(), indent=4)
        metadata_comments = "\n".join("//{}".format(line).strip() for line in metadata_str.splitlines())

        return metadata_comments + "\n\n" + self.export_schema()


    def export_schema(self, keyspace=None):

        ks_objs = [self.keyspaces[keyspace].ks_obj] if keyspace else [t.ks_obj for t in self.keyspaces.values()]

        set_replication_factor(ks_objs, self.props['rf'])

        # TODO: shift this around to a regex so that we can do the whole thing in a single pass
        cql_str = "\n\n".join(ks_obj.export_as_string() for ks_obj in ks_objs)
        return cql_str.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS") \
                      .replace("CREATE KEYSPACE", "CREATE KEYSPACE IF NOT EXISTS") \
                      .replace("CREATE TYPE", "CREATE TYPE IF NOT EXISTS") \
                      .replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")


    def each_keyspace(self, ks_fn):
        for (ks_name, ks_tuple) in self.keyspaces.items():
            ks_fn(ks_tuple.ks_obj, ks_tuple.ks_id)
