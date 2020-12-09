//Schema metadata:
//@host_count = 1
//@dc_count = 1

CREATE KEYSPACE IF NOT EXISTS ks_0 WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}  AND durable_writes = true;

CREATE TYPE IF NOT EXISTS ks_0.udt_0 (
    fld_0 text,
    fld_1 int
);

CREATE TYPE IF NOT EXISTS ks_0.udt_1 (
    fld_2 frozen<udt_2>,
    fld_3 frozen<map<frozen<udt_2>, frozen<udt_2>>>,
    fld_4 frozen<list<frozen<udt_0>>>,
    fld_5 frozen<tuple<frozen<udt_2>, frozen<udt_0>>>
);

CREATE TYPE IF NOT EXISTS ks_0.udt_2 (
    fld_6 frozen<tuple<text, text>>,
    fld_7 frozen<udt_0>
);

CREATE TABLE IF NOT EXISTS ks_0.tbl_0 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 frozen<udt_1>,
    col_5 map<int, int>,
    col_6 set<int>,
    col_7 frozen<tuple<int, frozen<tuple<text, double>>>>,
    col_8 text,
    col_9 timestamp,
    col_10 timeuuid,
    col_11 uuid,
    col_12 text,
    col_13 varint,
    col_14 decimal,
    col_15 double,
    col_16 float,
    col_17 inet,
    col_18 int,
    col_19 list<int>,
    col_20 frozen<udt_2>,
    PRIMARY KEY ((col_0, col_1), col_2, col_3)
) WITH CLUSTERING ORDER BY (col_2 ASC, col_3 ASC)
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'enabled': 'false'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
CREATE INDEX IF NOT EXISTS idx_0 ON ks_0.tbl_0 (col_0);

CREATE TABLE IF NOT EXISTS ks_0.tbl_1 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 frozen<udt_1>,
    col_5 map<int, int>,
    col_6 set<int>,
    col_7 frozen<tuple<int, frozen<tuple<text, double>>>>,
    col_8 text,
    col_9 timestamp,
    col_10 timeuuid,
    col_11 uuid,
    col_12 text,
    col_13 varint,
    col_14 decimal,
    col_15 double,
    col_16 float,
    col_17 inet,
    col_18 int,
    col_19 list<int>,
    col_20 frozen<udt_2>,
    PRIMARY KEY ((col_0, col_1), col_2, col_3)
) WITH CLUSTERING ORDER BY (col_2 ASC, col_3 ASC)
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'enabled': 'false'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
CREATE INDEX IF NOT EXISTS idx_1 ON ks_0.tbl_1 (col_0);

CREATE TABLE IF NOT EXISTS ks_0.tbl_2 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 frozen<udt_1>,
    col_5 map<int, int>,
    col_6 set<int>,
    col_7 frozen<tuple<int, frozen<tuple<text, double>>>>,
    col_8 text,
    col_9 timestamp,
    col_10 timeuuid,
    col_11 uuid,
    col_12 text,
    col_13 varint,
    col_14 decimal,
    col_15 double,
    col_16 float,
    col_17 inet,
    col_18 int,
    col_19 list<int>,
    col_20 frozen<udt_2>,
    PRIMARY KEY ((col_0, col_1), col_2, col_3)
) WITH CLUSTERING ORDER BY (col_2 ASC, col_3 ASC)
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'enabled': 'false'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
CREATE INDEX IF NOT EXISTS idx_2 ON ks_0.tbl_2 (col_0);

CREATE KEYSPACE IF NOT EXISTS ks_1 WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}  AND durable_writes = true;

CREATE TYPE IF NOT EXISTS ks_1.udt_0 (
    fld_0 text,
    fld_1 int
);

CREATE TYPE IF NOT EXISTS ks_1.udt_1 (
    fld_2 frozen<udt_2>,
    fld_3 frozen<map<frozen<udt_2>, frozen<udt_2>>>,
    fld_4 frozen<list<frozen<udt_0>>>,
    fld_5 frozen<tuple<frozen<udt_2>, frozen<udt_0>>>
);

CREATE TYPE IF NOT EXISTS ks_1.udt_2 (
    fld_6 frozen<tuple<text, text>>,
    fld_7 frozen<udt_0>
);

CREATE TABLE IF NOT EXISTS ks_1.tbl_0 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 frozen<udt_1>,
    col_5 map<int, int>,
    col_6 set<int>,
    col_7 frozen<tuple<int, frozen<tuple<text, double>>>>,
    col_8 text,
    col_9 timestamp,
    col_10 timeuuid,
    col_11 uuid,
    col_12 text,
    col_13 varint,
    col_14 decimal,
    col_15 double,
    col_16 float,
    col_17 inet,
    col_18 int,
    col_19 list<int>,
    col_20 frozen<udt_2>,
    PRIMARY KEY ((col_0, col_1), col_2, col_3)
) WITH CLUSTERING ORDER BY (col_2 ASC, col_3 ASC)
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'enabled': 'false'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
CREATE INDEX IF NOT EXISTS idx_0 ON ks_1.tbl_0 (col_0);

CREATE TABLE IF NOT EXISTS ks_1.tbl_1 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 frozen<udt_1>,
    col_5 map<int, int>,
    col_6 set<int>,
    col_7 frozen<tuple<int, frozen<tuple<text, double>>>>,
    col_8 text,
    col_9 timestamp,
    col_10 timeuuid,
    col_11 uuid,
    col_12 text,
    col_13 varint,
    col_14 decimal,
    col_15 double,
    col_16 float,
    col_17 inet,
    col_18 int,
    col_19 list<int>,
    col_20 frozen<udt_2>,
    PRIMARY KEY ((col_0, col_1), col_2, col_3)
) WITH CLUSTERING ORDER BY (col_2 ASC, col_3 ASC)
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'enabled': 'false'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
CREATE INDEX IF NOT EXISTS idx_1 ON ks_1.tbl_1 (col_0);

CREATE TABLE IF NOT EXISTS ks_1.tbl_2 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 frozen<udt_1>,
    col_5 map<int, int>,
    col_6 set<int>,
    col_7 frozen<tuple<int, frozen<tuple<text, double>>>>,
    col_8 text,
    col_9 timestamp,
    col_10 timeuuid,
    col_11 uuid,
    col_12 text,
    col_13 varint,
    col_14 decimal,
    col_15 double,
    col_16 float,
    col_17 inet,
    col_18 int,
    col_19 list<int>,
    col_20 frozen<udt_2>,
    PRIMARY KEY ((col_0, col_1), col_2, col_3)
) WITH CLUSTERING ORDER BY (col_2 ASC, col_3 ASC)
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'enabled': 'false'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
CREATE INDEX IF NOT EXISTS idx_2 ON ks_1.tbl_2 (col_0);
