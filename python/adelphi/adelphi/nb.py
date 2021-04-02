import logging
import yaml

from itertools import chain

from adelphi.exceptions import KeyspaceSelectionException, TableSelectionException, ExportException
from adelphi.export import BaseExporter

SEQS={}
SEQS["text"] = "Mod(1000000000); ToString() -> String"
DISTS={}
DISTS["text"] = "Hash(); Mod(1000000000); ToString() -> String"

log = logging.getLogger('adelphi')

# A collection of functionally static functions
def dist_binding_name(col):
    return "{}_dist".format(col.name)


def seq_binding_name(col):
    return "{}_seq".format(col.name)


def quote_str(s):
    return "\"{}\"".format(s)

def build_bindings(table):
    rv = {}
    for (col_name, col) in table.columns.items():
        if col.cql_type not in DISTS.keys():
            raise ColumnTypeException("No nosqlbench distribution configured for type {}".format(col.cql_type))
        rv[dist_binding_name(col)] = DISTS[col.cql_type]

        # If we have a primary key we'll also need a seq for insert statements
        if col_name in [c.name for c in table.primary_key]:
            if col.cql_type not in SEQS.keys():
                raise ColumnTypeException("No nosqlbench sequence configured for type {}".format(col.cql_type))
            rv[seq_binding_name(col)] = SEQS[col.cql_type]

    return rv


def build_select_statements(keyspace, table):
    key_bindings = " and ".join(["{} = {}".format(quote_str(key.name), "{" + dist_binding_name(key) + "}") for key in table.primary_key])
    return "select * from  {}.{} where {}".format(quote_str(keyspace.name), quote_str(table.name), key_bindings)


def build_insert_statements(keyspace, table):
    # Note that both the sequence of column names and column bindings are built off of
    # the same base sequence (cols below) in order to make sure column names and binding
    # names line up in the generated CQL.  Order is pretty important here.
    cols = table.columns.values()
    primary_keys = set([c.name for c in table.primary_key])
    col_names = ",".join([quote_str(col.name) for col in cols])
    def binding_name(col):
        return seq_binding_name(col) if col.name in primary_keys else dist_binding_name(col)
    col_bindings = ",".join(["{" + binding_name(c) + "}" for c in cols])
    return "insert into {}.{} ({}) values ({})".format(quote_str(keyspace.name), quote_str(table.name), col_names, col_bindings)


class ColumnTypeException(Exception):
    """Exception indicinating an error in the handling of a specific column type"""
    pass


class NbExporter(BaseExporter):

    def __init__(self, cluster, props):

        # Always disable anonymization when generating nosqlbench configs
        self.props = props.copy()
        self.props["anonymize"] = False

        self.metadata = self.get_common_metadata(cluster, self.props)

        all_keyspaces = self.get_keyspaces(cluster, self.props)
        if len(all_keyspaces) > 1:
            raise KeyspaceSelectionException("nosqlbench export doesn't support multiple keyspaces")
        self.keyspace = next(iter(all_keyspaces.values())).ks_obj

        if len(self.keyspace.tables) == 0:
            raise TableSelectionException("Keyspace {} contains no tables".format(self.keyspace.name))
        self.table = next(iter(self.keyspace.tables.values()))

        log.info("Creating nosqlbench config for {}.{}".format(self.keyspace.name, self.table.name))



    def export_schema(self, keyspace=None):
        if keyspace and keyspace != self.keyspace.name:
            raise ExportException("Exporter doesn't know about keyspace {} requested for export".format(keyspace))
        return self.__build_schema()


    # Requires custom impl because we don't want to support the notion of an arbitrary keyspace_id.
    # We don't anonymize nosqlbench configs at all so just explicitly use keyspace name here.
    def each_keyspace(self, ks_fn):
        ks_fn(self.keyspace, self.keyspace.name)


    def __build_rampup_statement(self):
        return {"tags":{"name":"rampup-insert"}, "rampup-insert": build_insert_statements(self.keyspace, self.table)}


    def __build_main_read_statement(self):
        return {"tags":{"name":"main-select"}, "main-select": build_select_statements(self.keyspace, self.table)}


    def __build_main_write_statement(self):
        return {"tags":{"name":"main-insert"}, "main-insert": build_insert_statements(self.keyspace, self.table)}


    def __build_schema(self):
        """Really more of a config than a schema, but we'll allow it"""
        root = {}

        rampup_scenario = "run driver=cql tags==phase:rampup cycles===TEMPLATE(rampup-cycles,1000) threads=auto"
        main_scenario = "run driver=cql tags==phase:main cycles===TEMPLATE(main-cycles,1000) threads=auto"
        root["scenarios"] = {"default":[rampup_scenario, main_scenario]}
        
        root["bindings"] = build_bindings(self.table)

        cl_map = {"cl":"LOCAL_QUORUM"}
        cl_ratio_map = {"ratio":5}
        cl_ratio_map.update(cl_map)

        rampup_block = {"name":"rampup", "tags":{"phase":"rampup"}, "params":cl_map, "statements": [self.__build_rampup_statement()]}
        main_read_block = {"name":"main-read", "tags":{"phase":"main", "type":"read"}, "params":cl_ratio_map, "statements": [self.__build_main_read_statement()]}
        main_write_block = {"name":"main-write", "tags":{"phase":"main", "type":"write"}, "params":cl_ratio_map, "statements": [self.__build_main_write_statement()]}
        root["blocks"] = [rampup_block, main_read_block, main_write_block]

        return yaml.dump(root, default_flow_style=False)
