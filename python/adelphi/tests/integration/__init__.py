import logging
import os
import sys
import time

from cassandra.cluster import Cluster

# Default C* versions to include in all integration tests
CASSANDRA_VERSIONS = ["2.1.22", "2.2.19", "3.0.23", "3.11.9", "4.0-beta3"]

log = logging.getLogger('adelphi')

class BaseIntegrationTest:

    def connectToLocalCassandra(self):
        session = None
        while not session:
            try:
                cluster = Cluster(["127.0.0.1"],port=9042)
                session = cluster.connect()

                # Confirm that the session is actually functioning before calling things good
                rs = session.execute("select * from system.local")
                log.info("Connected to Cassandra cluster, first row of system.local: {}".format(rs.one()))
                log.info("Cassandra cluster ready")
                return (cluster,session)
            except:
                log.info("Couldn't quite connect yet, will retry")
                time.sleep(1)


    def createSchema(self, session=None, schemaPath=None):
        log.info("Creating schema on Cassandra cluster")
        with open(schemaPath) as schema:
            for stmt in [s.strip() for s in schema.read().split(';')]:
                if len(stmt) == 0:
                    log.info("Skipping empty statement")
                    continue
                if stmt.startswith("//"):
                    log.info("Skipping commented statement {}".format(stmt))
                    continue
                realStmt = stmt + ';'
                log.debug("Executing statement {}".format(realStmt))
                try:
                    session.execute(realStmt)
                except:
                    log.info("Exception executing statement: {}".format(realStmt), exc_info=sys.exc_info()[0])
