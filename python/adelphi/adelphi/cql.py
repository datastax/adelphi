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

from adelphi.store import get_standard_columns_from_table_metadata, set_replication_factor

def export_cql_schema(keyspaces_metadata, options):

    # set replication factor
    set_replication_factor(keyspaces_metadata, options['rf'])
    # build CQL statements string
    generated_statements = "\n\n".join(ks.export_as_string() for ks in keyspaces_metadata)
    # transform CREATE statements to include `IF NOT EXISTS`

    # TODO: shift this around to a regex so that we can do the whole thing in a single pass
    return generated_statements.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS") \
        .replace("CREATE KEYSPACE", "CREATE KEYSPACE IF NOT EXISTS") \
        .replace("CREATE TYPE", "CREATE TYPE IF NOT EXISTS") \
        .replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")
