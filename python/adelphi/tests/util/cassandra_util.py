# Using "c8" rather than "cassandra" to avoid any conflicts with "cassandra" package in
# cassandra-driver
import logging
import time

from cassandra.cluster import Cluster

log = logging.getLogger('adelphi')

def connectToLocalCassandra():
    session = None
    while not session:
        try:
            cluster = Cluster(["127.0.0.1"], port=9042)
            session = cluster.connect()

            # Confirm that the session is actually functioning before calling things good
            rs = session.execute("select * from system.local")
            log.info("Connected to Cassandra cluster, first row of system.local: {}".format(rs.one()))
            log.info("Cassandra cluster ready")
            return (cluster, session)
        except:
            log.info("Couldn't quite connect yet, will retry")
            time.sleep(3)


def createSchema(session, schemaPath):
    log.info("Creating schema on Cassandra cluster from file {}".format(schemaPath))
    with open(schemaPath) as schema:
        buff = ""
        for line in schema:
            realLine = line.strip()
            if len(realLine) == 0:
                log.debug("Skipping empty statement")
                continue
            if realLine.startswith("//") or realLine.startswith("--"):
                log.debug("Skipping commented statement")
                continue
            buff += (" " if len(buff) > 0 else "")
            buff += realLine
            if buff.endswith(';'):
                log.debug("Executing statement {}".format(buff))
                try:
                    session.execute(buff)
                except Exception as exc:
                    log.error("Exception executing statement: {}".format(buff), exc_info=exc)
                finally:
                    buff = ""
