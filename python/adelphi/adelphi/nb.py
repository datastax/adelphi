import yaml

from itertools import chain

from adelphi.exceptions import TooManyKeyspacesException, TooManyTablesException
from adelphi.export import BaseExporter

SEQS={}
SEQS["text"] = "Mod(1000000000); ToString() -> String"
DISTS={}
DISTS["text"] = "Hash(); Mod(1000000000); ToString() -> String"

# A collection of functionally static functions
def dist_binding_name(col):
    return "{}_dist".format(col.name)


def seq_binding_name(col):
    return "{}_seq".format(col.name)


def build_bindings(table):
    rv = {}
    for (col_name, col) in table.columns.items():
        if col.cql_type not in DISTS.keys():
            raise UnsupportedColumnTypeException("No nosqlbench distribution configured for type {}".format(col.cql_type))
        rv[dist_binding_name(col)] = DISTS[col.cql_type]

        # If we have a primary key we'll also need a seq for insert statements
        if col_name in [c.name for c in table.primary_key]:
            if col.cql_type not in SEQS.keys():
                raise UnsupportedColumnTypeException("No nosqlbench sequence configured for type {}".format(col.cql_type))
            rv[seq_binding_name(col)] = SEQS[col.cql_type]

    return rv


def build_select_statements(keyspace, table):
    key_bindings = " and ".join(["{} = {}".format(key.name, "{" + dist_binding_name(key) + "}") for key in table.primary_key])
    return "select * from  {}.{} where {}".format(keyspace.name, table.name, key_bindings)


def build_insert_statements(keyspace, table):
    cols = table.columns.values()
    primary_keys = set(table.primary_key)
    col_names = ",".join([col.name for col in cols])
    def binding_name(col):
        return seq_binding_name(c) if col in primary_keys else dist_binding_name(c)
    col_bindings = ",".join(["{" + binding_name(c) + "}" for c in cols])
    return "insert into {}.{} ({}) values ({})".format(keyspace.name, table.name, col_names, col_bindings)


class UnsupportedColumnTypeException(Exception):
    """Exception indicinating that we can't create nosqlbench structures for a column type"""
    def __init__(self, msg):
        self.message = msg


class NbExporter(BaseExporter):

    def __init__(self, cluster, props):

        # Always disable anonymization when generating nosqlbench configs
        self.props = props.copy()
        self.props["anonymize"] = False

        self.metadata = self.get_common_metadata(cluster, self.props)

        all_keyspaces = self.get_keyspaces(cluster, self.props)
        if len(all_keyspaces) > 1:
            raise TooManyKeyspacesException
        (ks, keyspace_id) = next(iter(all_keyspaces.items()))
        if (len(ks.tables)) > 1:
            raise TooManyTablesException
        self.keyspace = ks
        self.keyspace_id = keyspace_id
        self.table = next(iter(ks.tables.values()))


    def export_all(self):
        return self.export_schema()


    def export_metadata(self):
        return {k : self.metadata[k] for k in self.metadata.keys() if self.metadata[k]}


    def export_schema(self):
        return self.__build_schema()


    def each_keyspace(self, ks_fn):
        ks_fn(self.keyspace, self.keyspace_id)


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
