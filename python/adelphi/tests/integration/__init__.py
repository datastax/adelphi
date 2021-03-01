import logging
import os
import sys
import time

from cassandra.cluster import Cluster

import docker

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


    def createSchema(self, session=None):
        schemaPath = self.getSchemaPath()
        log.info("Creating schema on Cassandra cluster from file {}".format(schemaPath))
        with open(schemaPath) as schema:
            for stmt in [s.strip() for s in schema.read().split(';')]:
                if len(stmt) == 0:
                    log.debug("Skipping empty statement")
                    continue
                if stmt.startswith("//"):
                    log.debug("Skipping commented statement {}".format(stmt))
                    continue
                realStmt = stmt + ';'
                log.debug("Executing statement {}".format(realStmt))
                try:
                    session.execute(realStmt)
                except:
                    log.info("Exception executing statement: {}".format(realStmt), exc_info=sys.exc_info()[0])


    def runTestForVersion(self, version=None):
        log.info("Testing Cassandra version {}".format(version))

        container = self.client.containers.run(name="adelphi", remove=True, detach=True, ports={9042:9042}, image="cassandra:{}".format(version))

        (cluster,session) = (None,None)
        try:
            (cluster,session) = self.connectToLocalCassandra()
            self.createSchema(session)
            self.runTestWithSchema(version)
        finally:
            if cluster:
                cluster.shutdown()

            if "KEEP_CONTAINER" in os.environ:
                log.info("KEEP_CONTAINER env var set, preserving Cassandra container 'adelphi'")
            else:
                container.stop()

            self.cleanUpVersion(version)


    def testVersions(self):
        versions = CASSANDRA_VERSIONS
        if "CASSANDRA_VERSIONS" in os.environ:
            versions = os.environ["CASSANDRA_VERSIONS"].split(',')

        log.info("Testing the following Cassandra versions: {}".format(versions))

        for version in versions:
            self.runTestForVersion(version)


    def setUp(self):
        self.client = docker.from_env()
