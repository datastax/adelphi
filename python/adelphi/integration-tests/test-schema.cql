CREATE KEYSPACE IF NOT EXISTS testkeyspace
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    AND durable_writes = true;

  CREATE TABLE IF NOT EXISTS testkeyspace.testtable (
    key text,
    value text,
    PRIMARY KEY (key)
  );
