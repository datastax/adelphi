import logging
import yaml

from itertools import chain

from adelphi.exceptions import KeyspaceSelectionException, TableSelectionException, ExportException
from adelphi.export import BaseExporter

MAX_NUMERIC_VAL = 1000 ** 3
RAMPUP_SCENARIO = "run driver=cql tags=phase:rampup cycles={} threads=auto"
MAIN_SCENARIO = "run driver=cql tags=phase:main cycles={} threads=auto"

CQL_TYPES={}
CQL_TYPES["text"] = "Mod({}); ToString() -> String"
CQL_TYPES["ascii"] = "Mod({}); ToString() -> String"
CQL_TYPES["int"] = "Mod({}); ToInt() -> int"
CQL_TYPES["tinyint"] = "Mod({}); ToByte() -> java.lang.Byte"
CQL_TYPES["smallint"] = "Mod({}); ToShort() -> java.lang.Short"
CQL_TYPES["bigint"] = "Mod({}); ToLong() -> long"
CQL_TYPES["float"] = "Mod({}); ToFloat() -> java.lang.Float"
CQL_TYPES["double"] = "Mod({}); ToDouble() -> double"
CQL_TYPES["decimal"] = "ModuloToBigDecimal({}) -> java.math.BigDecimal"
CQL_TYPES["boolean"] = "Mod({}); ToBoolean() -> java.lang.Boolean"
CQL_TYPES["varchar"] = "Mod({}); ToString() -> String"
CQL_TYPES["varint"] = "ModuloToBigInt({}) -> java.math.BigInteger"
CQL_TYPES["blob"] = "Mod({}); ToByteBuffer() -> java.nio.ByteBuffer"
CQL_TYPES["timestamp"] = "Mod({}); ToDate() -> java.util.Date"
CQL_TYPES["date"] = "Mod({}); LongToLocalDateDays() -> com.datastax.driver.core.LocalDate"
CQL_TYPES["time"] = "Mod({}); ToLong() -> long"
CQL_TYPES["uuid"] = "Mod({}); ToHashedUUID() -> java.util.UUID"
CQL_TYPES["timeuuid"] = "Mod({}); ToTimeUUIDMax() -> java.util.UUID"
CQL_TYPES["inet"] = "Mod({}); ToInetAddress() -> java.net.InetAddress"

log = logging.getLogger('adelphi')

# A collection of functionally static functions
def dist_binding_name(col):
    return "{}_dist".format(col.name)


def seq_binding_name(col):
    return "{}_seq".format(col.name)


def quote_str(s):
    return "\"{}\"".format(s)


def is_supported_type(col):
    """Returns true if we have the ability to create a distribution or sequence for this column type, false otherwise"""
    return col.cql_type in CQL_TYPES


def partition_cols(table):
    pk_set = set([c.name for c in table.primary_key])
    plain_cols = [c for c in table.columns.values() if c.name not in pk_set]
    return (table.primary_key, plain_cols)


def build_select_statements(keyspace, table):
    # Note that we don't need to worry about supported types here.  We're only selecting based on
    # primary keys cols and elsewhere we've already validated that these cols are all of a supported
    # type.
    key_bindings = " and ".join(["{} = {}".format(quote_str(key.name), "{" + dist_binding_name(key) + "}") for key in table.primary_key])
    return "select * from  {}.{} where {}".format(quote_str(keyspace.name), quote_str(table.name), key_bindings)


def build_insert_statements(keyspace, table):
    # Note that both the sequence of column names and column bindings are built off of
    # the same base sequence (cols below) in order to make sure column names and binding
    # names line up in the generated CQL.  Order is pretty important here.
    cols = [c for c in table.columns.values() if is_supported_type(c)]
    primary_keys = set([c.name for c in table.primary_key])
    col_names = ",".join([quote_str(col.name) for col in cols])
    def binding_name(col):
        return seq_binding_name(col) if col.name in primary_keys else dist_binding_name(col)
    col_bindings = ",".join(["{" + binding_name(c) + "}" for c in cols])
    return "insert into {}.{} ({}) values ({})".format(quote_str(keyspace.name), quote_str(table.name), col_names, col_bindings)


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
        self.keyspace = next(iter(all_keyspaces.values())).ks_obj

        if len(self.keyspace.tables) == 0:
            raise TableSelectionException("Keyspace {} contains no tables".format(self.keyspace.name))
        self.table = next(iter(self.keyspace.tables.values()))

        log.info("Creating nosqlbench config for {}.{}".format(self.keyspace.name, self.table.name))
        log.info("Number of cycles for rampup phase = {}".format(self.rampup_cycles))
        log.info("Number of cycles for main phase = {}".format(self.main_cycles))
        log.info("Max numeric value = {}".format(self.numeric_max))


    def export_schema(self, keyspace=None):
        if keyspace and keyspace != self.keyspace.name:
            raise ExportException("Exporter doesn't know about keyspace {} requested for export".format(keyspace))
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
        base = CQL_TYPES[typename].format(self.numeric_max)
        return "Hash(); {}".format(base)


    def __get_seq(self, typename):
        return CQL_TYPES[typename].format(self.numeric_max)


    def __build_rampup_statement(self):
        return {"tags":{"name":"rampup-insert"}, "rampup-insert": build_insert_statements(self.keyspace, self.table)}


    def __build_main_read_statement(self):
        return {"tags":{"name":"main-select"}, "main-select": build_select_statements(self.keyspace, self.table)}


    def __build_main_write_statement(self):
        return {"tags":{"name":"main-insert"}, "main-insert": build_insert_statements(self.keyspace, self.table)}


    def __build_bindings(self, table):
        (pk_cols, plain_cols) = partition_cols(table)
        rv = {dist_binding_name(plain_col): self.__get_dist(plain_col.cql_type) for plain_col in plain_cols if is_supported_type(plain_col)}

        def pk_generator():
            for pk_col in pk_cols:
                if not is_supported_type(pk_col):
                    raise UnsupportedPrimaryKeyTypeException("No sequence definition for primary key column {} of type {}".format(pk_col.name, pk_col.cql_type))
                yield((seq_binding_name(pk_col), self.__get_seq(pk_col.cql_type)))
                # Each pk col also gets a DIST def because we may want to execute selects against it
                yield((dist_binding_name(pk_col), self.__get_dist(pk_col.cql_type)))
        rv.update(dict(pk_generator()))
        return rv


    def __build_schema(self):
        """Really more of a config than a schema, but we'll allow it"""
        root = {}

        root["scenarios"] = {"TEMPLATE(scenarioname,default)":[self.__get_rampup_scenario(), self.__get_main_scenario()]}
        
        root["bindings"] = self.__build_bindings(self.table)

        cl_map = {"cl":"LOCAL_QUORUM"}
        cl_ratio_map = {"ratio":5}
        cl_ratio_map.update(cl_map)

        rampup_block = {"name":"rampup", "tags":{"phase":"rampup"}, "params":cl_map, "statements": [self.__build_rampup_statement()]}
        main_read_block = {"name":"main-read", "tags":{"phase":"main", "type":"read"}, "params":cl_ratio_map, "statements": [self.__build_main_read_statement()]}
        main_write_block = {"name":"main-write", "tags":{"phase":"main", "type":"write"}, "params":cl_ratio_map, "statements": [self.__build_main_write_statement()]}
        root["blocks"] = [rampup_block, main_read_block, main_write_block]

        return yaml.dump(root, default_flow_style=False)
