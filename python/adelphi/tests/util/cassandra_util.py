# A few utility methods for interacting with Cassandra from within tests
import logging
import time

from cassandra.cluster import Cluster

from tenacity import retry, wait_fixed

log = logging.getLogger('adelphi')

@retry(wait=wait_fixed(3))
def connectToLocalCassandra():
    cluster = Cluster(["127.0.0.1"], port=9042)
    session = cluster.connect()

    # Confirm that the session is actually functioning before calling things good
    rs = session.execute("select * from system.local")
    log.info("Connected to Cassandra cluster, first row of system.local: {}".format(rs.one()))
    return (cluster, session)


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


def callWithCassandra(someFn):
    cluster = None
    try:
        (cluster,session) = connectToLocalCassandra()
        return someFn(cluster, session)
    finally:
        cluster.shutdown()
