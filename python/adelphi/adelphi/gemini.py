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

from cassandra.cqltypes import cqltype_to_python

from adelphi.exceptions import KeyspaceSelectionException, ExportException
from adelphi.export import BaseExporter
from adelphi.store import get_standard_columns_from_table_metadata, set_replication_factor


class GeminiExporter(BaseExporter):

    def __init__(self, cluster, props):

        self.props = props
        self.metadata = self.get_common_metadata(cluster, props)

        all_keyspaces = self.get_keyspaces(cluster, props)
        if len(all_keyspaces) > 1:
            raise KeyspaceSelectionException("Gemini schema doesn't support multiple keyspaces")
        (ks_name, ks_tuple) = next(iter(all_keyspaces.items()))
        self.keyspace = ks_tuple.ks_obj
        self.keyspace_id = ks_tuple.ks_id


    def export_schema(self, keyspace=None):
        if keyspace and keyspace != self.keyspace.name:
            raise ExportException("Exporter doesn't know about keyspace {} requested for export".format(keyspace))
        return self.__build_schema()


    def __build_schema(self):

        set_replication_factor(self.keyspace, self.props['rf'])

        replication = json.loads(
            self.keyspace.replication_strategy.export_for_schema().replace("'", "\""))
        data = {
            "keyspace": {
                "name": self.keyspace.name,
                "replication": replication,
                "oracle_replication": replication
            },
            "tables": []
        }

        for t in self.keyspace.tables.values():
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
                    "type": self.__cql_type_to_gemini(cqltype_to_python(c.cql_type))
                })

            for index in t.indexes.values():
                table_data["indexes"].append({
                    "name": index.name,
                    "column": index.index_props["target"]
                })

            data["tables"].append(table_data)

        return json.dumps(data, indent=4)


    def __cql_type_to_gemini(self, cql_type, is_frozen=False):
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
                return self.__cql_type_to_gemini(token, is_frozen_type)
            elif token == 'frozen':
                return self.__cql_type_to_gemini(cql_type.pop(0), True)
            elif token == 'map':
                subtypes = cql_type.pop(0)
                gemini_type['key_type'] = self.__cql_type_to_gemini(subtypes[0], is_frozen_type)
                gemini_type['value_type'] = self.__cql_type_to_gemini(subtypes[1], is_frozen_type)
            elif token == 'list':
                gemini_type['kind'] = 'list'
                gemini_type['type'] = self.__cql_type_to_gemini(cql_type.pop(0)[0], is_frozen_type)
            elif token == 'set':
                gemini_type['kind'] = 'set'
                gemini_type['type'] = self.__cql_type_to_gemini(cql_type.pop(0)[0], is_frozen_type)
            elif token == 'tuple':
                gemini_type['types'] = cql_type.pop(0)

            gemini_type['frozen'] = is_frozen_type
            return gemini_type
