CREATE KEYSPACE testkeyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}  AND durable_writes = true;

CREATE TABLE testkeyspace.testtable (
    key1 text,
    key2 text,
    value text,
    unsupported list<int>,
    PRIMARY KEY (key1, key2)
) WITH CLUSTERING ORDER BY (key2 ASC)
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'};
