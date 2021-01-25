import yaml

from itertools import chain

from adelphi.exceptions import TooManyKeyspacesException, TooManyTablesException
from adelphi.export import BaseExporter


class NbExporter(BaseExporter):

    def __init__(self, cluster, props):

        self.props = props
        self.metadata = self.get_common_metadata(cluster, props)

        all_keyspaces = self.get_keyspaces(cluster, props)
        if len(all_keyspaces) > 1:
            raise TooManyKeyspacesException
        (ks, keyspace_id) = next(iter(all_keyspaces.items()))
        if (len(ks.tables)) > 1:
            raise TooManyTablesException
        self.keyspace = ks
        self.keyspace_id = keyspace_id


    def export_all(self):
        return self.export_schema()


    def export_metadata(self):
        return {k : self.metadata[k] for k in self.metadata.keys() if self.metadata[k]}


    def export_schema(self):
        return self.__build_schema()


    def each_keyspace(self, ks_fn):
        ks_fn(self.keyspace, self.keyspace_id)


    def __build_schema(self):
        """Really more of a config than a schema, but we'll allow it"""
        root={}

        rampup_scenario = "run driver=cql tags==phase:rampup cycles===TEMPLATE(rampup-cycles,1000) threads=auto"
        main_scenario = "run driver=cql tags==phase:main cycles===TEMPLATE(main-cycles,1000) threads=auto"
        root["scenarios"] = {"default":[rampup_scenario, main_scenario]}
        
        #root["bindings"] = bindings

        cl_map = {"cl":"LOCAL_QUORUM"}
        cl_ratio_map = {"ratio":5}
        cl_ratio_map.update(cl_map)

        rampup_block = {"name":"rampup", "tags":{"phase":"rampup"}, "params":cl_map}
        verify_block = {"name":"verify", "tags":{"phase":"verify", "type":"read"}, "params":cl_map}
        main_read_block = {"name":"main-read", "tags":{"phase":"main", "type":"read"}, "params":cl_ratio_map}
        main_write_block = {"name":"main-write", "tags":{"phase":"main", "type":"write"}, "params":cl_ratio_map}
        root["blocks"] = [rampup_block, verify_block, main_read_block, main_write_block]

        return yaml.dump(root, default_flow_style=False)
