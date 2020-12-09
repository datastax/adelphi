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


# Functions and constants related to the anonymization process
from adelphi.store import get_standard_columns_from_table_metadata
import re

# default prefixes for the anonymized names
KEYSPACE_PREFIX = "ks"
TABLE_PREFIX = "tbl"
COLUMN_PREFIX = "col"
TYPE_PREFIX = "udt"
FIELD_PREFIX = "fld"
INDEX_PREFIX = "idx"

# maps the original schema names to the replacement names
name_map = {
    KEYSPACE_PREFIX: {},
    TABLE_PREFIX: {},
    COLUMN_PREFIX: {},
    TYPE_PREFIX: {},
    FIELD_PREFIX: {},
    INDEX_PREFIX: {}
}

def get_name(original_name, prefix):
    """
    Looks up the anonymized name for the provided original name in the cache.
    If not present, one is created, inserted into the cache and returned.
    """
    count = len(name_map[prefix])
    anonymized_named_prefixed = "%s_%s" % (prefix, count)
    return name_map[prefix].setdefault(original_name, anonymized_named_prefixed)


def anonymize_keyspace(keyspace):
    keyspace.name = get_name(keyspace.name, KEYSPACE_PREFIX)

    # anonymize udts at once because they can reference
    # one another
    udts = sorted(keyspace.user_types.values(), key=lambda v: v.name)
    anonymize_udts(udts)

    for table in sorted(keyspace.tables.values(), key=lambda v: v.name):
        anonymize_table(table)

    # remove functions, aggregates and views for now
    keyspace.functions = {}
    keyspace.aggregates = {}
    keyspace.views = {}

    return keyspace

def anonymize_type(original_type):
    name = original_type
    for udt in name_map[TYPE_PREFIX]:
        name = name.replace(udt, name_map[TYPE_PREFIX][udt])
    return name


def anonymize_udts(udts):
    # anonymize all udt names first
    for udt in udts:
        udt.keyspace = get_name(udt.keyspace, KEYSPACE_PREFIX)
        udt.name = get_name(udt.name, TYPE_PREFIX)
    
    for udt in udts:
        # field names
        udt.field_names = [get_name(field_name, FIELD_PREFIX) for field_name in udt.field_names]
        # field types
        udt.field_types = [anonymize_type(field_type) for field_type in udt.field_types]

def anonymize_column(column):
    column.name = get_name(column.name, COLUMN_PREFIX)
    column.cql_type = anonymize_type(column.cql_type)


def anonymize_index(index):
    index.name = get_name(index.name, INDEX_PREFIX)
    index.index_options['target'] = get_name(index.index_options["target"], COLUMN_PREFIX)
    index.keyspace_name = get_name(index.keyspace_name, KEYSPACE_PREFIX)
    index.table_name = get_name(index.table_name, TABLE_PREFIX)

def anonymize_table(table):
    table.keyspace_name = get_name(table.keyspace_name, KEYSPACE_PREFIX)
    table.name = get_name(table.name, TABLE_PREFIX)

    for pk in table.partition_key:
        anonymize_column(pk)

    for ck in table.clustering_key:
        anonymize_column(ck)

    # remove comment since it may contain sensitive information
    table.options["comment"] = ""

    # The CQL python driver holds the same object references for clustering keys
    # and regular columns, so we have to separate them otherwise the names
    # will be re-anonymized.
    for column in get_standard_columns_from_table_metadata(table):
        anonymize_column(column)

    for index in sorted(list(table.indexes.values()), key=lambda v: v.name):
        if (index.kind == "CUSTOM"):
            del table.indexes[index.name]
            continue
        anonymize_index(index)
