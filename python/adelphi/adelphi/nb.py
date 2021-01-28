import yaml

from itertools import chain

from adelphi.exceptions import TooManyKeyspacesException, TooManyTablesException
from adelphi.export import BaseExporter

TEXT_SEQ="Mod(1000000000); ToString() -> String"
TEXT_DIST="Hash(); Mod(1000000000); ToString() -> String"

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


    def __build_bindings(self):
        rv = {}
        for (col_name, col) in self.table.columns.items():
            if col.cql_type == 'text':
                rv["{}_seq".format(col.name)] = TEXT_SEQ
                # If we have a primary key we'll also need a general distribution for select statements
                if col_name in [c.name for c in self.table.primary_key]:
                    rv["{}_dist".format(col.name)] = TEXT_DIST
        return rv


    def __build_rampup_insert_block(self):
        base_block = {"tags":{"name":"rampup-insert"}}
        # TODO: gen CQL string + add here
        #base_block["rampup-insert"] = 


    def __build_schema(self):
        """Really more of a config than a schema, but we'll allow it"""
        root = {}

        rampup_scenario = "run driver=cql tags==phase:rampup cycles===TEMPLATE(rampup-cycles,1000) threads=auto"
        main_scenario = "run driver=cql tags==phase:main cycles===TEMPLATE(main-cycles,1000) threads=auto"
        root["scenarios"] = {"default":[rampup_scenario, main_scenario]}
        
        root["bindings"] = self.__build_bindings()

        cl_map = {"cl":"LOCAL_QUORUM"}
        cl_ratio_map = {"ratio":5}
        cl_ratio_map.update(cl_map)

        rampup_block = {"name":"rampup", "tags":{"phase":"rampup"}, "params":cl_map, "statements": self.__build_rampup_insert_block()}
        main_read_block = {"name":"main-read", "tags":{"phase":"main", "type":"read"}, "params":cl_ratio_map}
        main_write_block = {"name":"main-write", "tags":{"phase":"main", "type":"write"}, "params":cl_ratio_map}
        root["blocks"] = [rampup_block, main_read_block, main_write_block]

        return yaml.dump(root, default_flow_style=False)
