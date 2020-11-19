CREATE KEYSPACE IF NOT EXISTS ks_0 WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}  AND durable_writes = true;

CREATE TABLE IF NOT EXISTS ks_0.tbl_0 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 map<int, int>,
    col_5 set<int>,
    col_6 text,
    col_7 timestamp,
    col_8 timeuuid,
    col_9 uuid,
    col_10 text,
    col_11 varint,
    col_12 decimal,
    col_13 double,
    col_14 float,
    col_15 inet,
    col_16 int,
    col_17 list<int>,
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
    col_4 map<int, int>,
    col_5 set<int>,
    col_6 text,
    col_7 timestamp,
    col_8 timeuuid,
    col_9 uuid,
    col_10 text,
    col_11 varint,
    col_12 decimal,
    col_13 double,
    col_14 float,
    col_15 inet,
    col_16 int,
    col_17 list<int>,
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
    col_4 map<int, int>,
    col_5 set<int>,
    col_6 text,
    col_7 timestamp,
    col_8 timeuuid,
    col_9 uuid,
    col_10 text,
    col_11 varint,
    col_12 decimal,
    col_13 double,
    col_14 float,
    col_15 inet,
    col_16 int,
    col_17 list<int>,
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

CREATE TABLE IF NOT EXISTS ks_1.tbl_0 (
    col_0 ascii,
    col_1 bigint,
    col_2 blob,
    col_3 boolean,
    col_4 map<int, int>,
    col_5 set<int>,
    col_6 text,
    col_7 timestamp,
    col_8 timeuuid,
    col_9 uuid,
    col_10 text,
    col_11 varint,
    col_12 decimal,
    col_13 double,
    col_14 float,
    col_15 inet,
    col_16 int,
    col_17 list<int>,
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
    col_4 map<int, int>,
    col_5 set<int>,
    col_6 text,
    col_7 timestamp,
    col_8 timeuuid,
    col_9 uuid,
    col_10 text,
    col_11 varint,
    col_12 decimal,
    col_13 double,
    col_14 float,
    col_15 inet,
    col_16 int,
    col_17 list<int>,
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
    col_4 map<int, int>,
    col_5 set<int>,
    col_6 text,
    col_7 timestamp,
    col_8 timeuuid,
    col_9 uuid,
    col_10 text,
    col_11 varint,
    col_12 decimal,
    col_13 double,
    col_14 float,
    col_15 inet,
    col_16 int,
    col_17 list<int>,
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
