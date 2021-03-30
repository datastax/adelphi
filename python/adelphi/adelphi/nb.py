import logging
import yaml

from itertools import chain

from adelphi.exceptions import KeyspaceSelectionException, TableSelectionException
from adelphi.export import BaseExporter

MAX_NUMERIC_VAL = 1000 ** 3
RAMPUP_SCENARIO = "run driver=cql tags=phase:rampup cycles={} threads=auto"
MAIN_SCENARIO = "run driver=cql tags=phase:main cycles={} threads=auto"

SEQS={}
SEQS["text"] = "Mod({}); ToString() -> String"
SEQS["ascii"] = "Mod({}); ToString() -> String"
SEQS["int"] = "Mod({}); ToInt() -> int"
SEQS["smallint"] = "Mod({}); ToShort() -> java.lang.Short"
SEQS["bigint"] = "Mod({}); ToLong() -> long"
SEQS["float"] = "Mod({}); ToFloat() -> java.lang.Float"
SEQS["double"] = "Mod({}); ToDouble() -> double"
SEQS["decimal"] = "ModuloToBigDecimal({}) -> java.math.BigDecimal"
SEQS["boolean"] = "Mod({}); ToBoolean() -> java.lang.Boolean"
SEQS["varint"] = "ModuloToBigInt({}) -> java.math.BigInteger"
SEQS["blob"] = "Mod({}); ToByteBuffer() -> java.nio.ByteBuffer"
DISTS={}
DISTS["text"] = "Hash(); Mod({}); ToString() -> String"
DISTS["ascii"] = "Hash(); Mod({}); ToString() -> String"
DISTS["int"] = "Hash(); Mod({}); ToInt() -> int"
DISTS["smallint"] = "Hash(); Mod({}); ToShort() -> java.lang.Short"
DISTS["bigint"] = "Hash(); Mod({}); ToLong() -> long"
DISTS["float"] = "Hash(); Mod({}); ToFloat() -> java.lang.Float"
DISTS["double"] = "Hash(); Mod({}); ToDouble() -> double"
DISTS["decimal"] = "Hash(); ModuloToBigDecimal({}) -> java.math.BigDecimal"
DISTS["boolean"] = "Hash(); Mod({}); ToBoolean() -> java.lang.Boolean"
DISTS["varint"] = "Hash(); ModuloToBigInt({}) -> java.math.BigInteger"
DISTS["blob"] = "Hash(); Mod({}); ToByteBuffer() -> java.nio.ByteBuffer"

log = logging.getLogger('adelphi')

# A collection of functionally static functions
def dist_binding_name(col):
    return "{}_dist".format(col.name)


def seq_binding_name(col):
    return "{}_seq".format(col.name)


def quote_str(s):
    return "\"{}\"".format(s)


def is_supported_plain_type(col):
    """Returns true if we have the ability to create a distribution for this column type, false otherwise"""
    return col.cql_type in DISTS


def is_supported_pk_type(col):
    """Returns true if we have the ability to create a sequence for this column type, false otherwise"""
    return col.cql_type in SEQS


def is_supported_type(col):
    """Returns true if we have the ability to create a distribution or sequence for this column type, false otherwise"""
    return is_supported_plain_type(col) or is_supported_pk_type(col)


def partition_cols(table):
    pk_set = set(table.primary_key)
    plain_cols = [c for c in table.columns.values() if c not in pk_set]
    return (table.primary_key, plain_cols)


def build_select_statements(keyspace, table):
    key_bindings = " and ".join(["{} = {}".format(quote_str(key.name), "{" + dist_binding_name(key) + "}") for key in table.primary_key])
    return "select * from  {}.{} where {}".format(quote_str(keyspace.name), quote_str(table.name), key_bindings)


def build_insert_statements(keyspace, table):
    (pk_cols, plain_cols) = partition_cols(table)
    col_names = [c.name for c in (table.primary_key + plain_cols) if is_supported_type(c)]

    pk_bindings = ["{" + seq_binding_name(c) + "}" for c in table.primary_key if is_supported_pk_type(c)]
    plain_bindings = ["{" + dist_binding_name(c) + "}" for c in plain_cols if is_supported_plain_type(c)]
    col_bindings = ",".join(pk_bindings + plain_bindings)

    return "insert into {}.{} ({}) values ({})".format(quote_str(keyspace.name), quote_str(table.name), ",".join(col_names), col_bindings)


class UnsupportedPrimaryKeyTypeException(Exception):
    """Exception indicating a primary key column for which there is no sequence support"""
    pass


class NbExporter(BaseExporter):

    def __init__(self, cluster, props):

        self.rampup_cycles = props["rampup-cycles"]
        self.main_cycles = props["main-cycles"]
        self.numeric_max = min((self.rampup_cycles + self.main_cycles) * 1000, MAX_NUMERIC_VAL)

        # Always disable anonymization when generating nosqlbench configs
        real_props = props.copy()
        real_props["anonymize"] = False

        self.metadata = self.get_common_metadata(cluster, real_props)

        all_keyspaces = self.get_keyspaces(cluster, real_props)
        if len(all_keyspaces) > 1:
            raise KeyspaceSelectionException("nosqlbench export doesn't support multiple keyspaces")
        self.keyspace = next(iter(all_keyspaces.keys()))

        if len(self.keyspace.tables) == 0:
            raise TableSelectionException("Keyspace {} contains no tables".format(self.keyspace.name))
        self.table = next(iter(self.keyspace.tables.values()))

        log.info("Creating nosqlbench config for {}.{}".format(self.keyspace.name, self.table.name))
        log.info("Number of cycles for rampup phase = {}".format(self.rampup_cycles))
        log.info("Number of cycles for main phase = {}".format(self.main_cycles))
        log.info("Max numeric value = {}".format(self.numeric_max))

    def export_all(self):
        return self.export_schema()


    def export_metadata(self):
        return {k : self.metadata[k] for k in self.metadata.keys() if self.metadata[k]}


    def export_schema(self):
        return self.__build_schema()


    # Requires custom impl because we don't want to support the notion of an arbitrary keyspace_id.
    # We don't anonymize nosqlbench configs at all so just explicitly use keyspace name here.
    def each_keyspace(self, ks_fn):
        ks_fn(self.keyspace, self.keyspace.name)


    def __get_rampup_scenario(self):
        return RAMPUP_SCENARIO.format(self.rampup_cycles)


    def __get_main_scenario(self):
        return MAIN_SCENARIO.format(self.main_cycles)


    def __get_dist(self, typename):
        return DISTS[typename].format(self.numeric_max)


    def __get_seq(self, typename):
        return SEQS[typename].format(self.numeric_max)


    def __build_rampup_statement(self):
        return {"tags":{"name":"rampup-insert"}, "rampup-insert": build_insert_statements(self.keyspace, self.table)}


    def __build_main_read_statement(self):
        return {"tags":{"name":"main-select"}, "main-select": build_select_statements(self.keyspace, self.table)}


    def __build_main_write_statement(self):
        return {"tags":{"name":"main-insert"}, "main-insert": build_insert_statements(self.keyspace, self.table)}


    def __build_bindings(self, table):
        (pk_cols, plain_cols) = partition_cols(table)
        rv = {dist_binding_name(plain_col): self.__get_dist(plain_col.cql_type) for plain_col in plain_cols if is_supported_plain_type(plain_col)}

        def pk_generator():
            for pk_col in pk_cols:
                if not is_supported_pk_type(pk_col):
                    raise UnsupportedPrimaryKeyTypeException("No sequence definition for primary key column {} of type {}".format(pk_col.name, pk_col.cql_type))
                yield((seq_binding_name(pk_col), self.__get_seq(pk_col.cql_type)))
                # Each pk col also gets a DIST def because we may want to execute selects against it
                yield((dist_binding_name(pk_col), self.__get_dist(pk_col.cql_type)))
        rv.update(dict(pk_generator()))
        return rv


    def __build_schema(self):
        """Really more of a config than a schema, but we'll allow it"""
        root = {}

        root["scenarios"] = {"default":[self.__get_rampup_scenario(), self.__get_main_scenario()]}
        
        root["bindings"] = self.__build_bindings(self.table)

        cl_map = {"cl":"LOCAL_QUORUM"}
        cl_ratio_map = {"ratio":5}
        cl_ratio_map.update(cl_map)

        rampup_block = {"name":"rampup", "tags":{"phase":"rampup"}, "params":cl_map, "statements": [self.__build_rampup_statement()]}
        main_read_block = {"name":"main-read", "tags":{"phase":"main", "type":"read"}, "params":cl_ratio_map, "statements": [self.__build_main_read_statement()]}
        main_write_block = {"name":"main-write", "tags":{"phase":"main", "type":"write"}, "params":cl_ratio_map, "statements": [self.__build_main_write_statement()]}
        root["blocks"] = [rampup_block, main_read_block, main_write_block]

        return yaml.dump(root, default_flow_style=False)
